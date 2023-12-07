#AnalyticsAPI Packages
from fds.analyticsapi.engines import ApiException
from fds.analyticsapi.engines.api.components_api import ComponentsApi
from fds.analyticsapi.engines.api.pa_calculations_api import PACalculationsApi
from fds.analyticsapi.engines.model.pa_calculation_parameters_root import PACalculationParametersRoot
from fds.analyticsapi.engines.model.pa_calculation_parameters import PACalculationParameters
from fds.analyticsapi.engines.model.pa_date_parameters import PADateParameters
from fds.analyticsapi.engines.model.pa_identifier import PAIdentifier
from fds.protobuf.stach.extensions.StachVersion import StachVersion
from fds.protobuf.stach.extensions.StachExtensionFactory import StachExtensionFactory
from fds.analyticsapi.engines import ApiException
from fds.analyticsapi.engines.api.components_api import ComponentsApi
from fds.analyticsapi.engines.api.column_statistics_api import ColumnStatisticsApi
from fds.analyticsapi.engines.api_client import ApiClient
from fds.analyticsapi.engines.configuration import Configuration
from fds.analyticsapi.engines.api.columns_api import ColumnsApi
from fds.analyticsapi.engines.model.unlinked_pa_template_parameters import UnlinkedPATemplateParameters
from fds.analyticsapi.engines.model.unlinked_pa_template_parameters_root import UnlinkedPATemplateParametersRoot
from fds.analyticsapi.engines.api.unlinked_pa_templates_api import UnlinkedPATemplatesApi
from fds.analyticsapi.engines.model.pa_calculation_column import PACalculationColumn
from fds.analyticsapi.engines.model.pa_calculation_group import PACalculationGroup
from fds.analyticsapi.engines.api.components_api import ComponentsApi
from fds.analyticsapi.engines.api.groups_api import GroupsApi
from fds.analyticsapi.engines import ApiException
from fds.analyticsapi.engines.api.pricing_sources_api import PricingSourcesApi
from fds.analyticsapi.engines.model.pa_calculation_data_sources import PACalculationDataSources
from fds.analyticsapi.engines.model.pa_calculation_pricing_source import PACalculationPricingSource
import os
from urllib3 import Retry
import time
from dotenv import load_dotenv
import os
import time
from urllib3 import Retry
from urllib import parse
load_dotenv()
import pandas as pd
import numpy as np

host ="https://api.factset.com"
fds_username = os.getenv("FACTSET_USERNAME")
fds_api_key = os.getenv("FACTSET_API_KEY")

"""
Initialize configuraiton object for Analytics API v3
Force 3 retrys when response times out or hits rate limit
"""
fds_config = Configuration(
    host="https://api.factset.com",
    username=fds_username,
    password=fds_api_key,
)
# 429 -> Max Requests
# 503 -> Requet Timed Out

## SSL verification
fds_config.verify_ssl=True

fds_config.retries = Retry(
    total=3,
    status=3,
    status_forcelist=frozenset([429, 503]),
    backoff_factor=2,
    raise_on_status=False,
    
)
#connect to api
api_client = ApiClient(fds_config)

#function to get component id given document name component category, and component name
def find_component_id(pa_document_name,pa_component_category,pa_component_name):
    #Pass the PA inputs
    try:
        #get all document components
        get_components_response = ComponentsApi(api_client).get_pa_components(document=pa_document_name)
        #Search all document components for specific component
        component_id = [id for id in list(get_components_response[0].data.keys()) 
                                if get_components_response[0].data[id].name == pa_component_name and 
                                get_components_response[0].data[id].category == pa_component_category][0]
        #return matched id
        return component_id

    except ApiException as e:
        print("Api exception Encountered")
        print(e)
        exit()

#get all PA groups
def get_pa_groups():
    return GroupsApi(api_client=api_client).get_pa_groups()

#Get PA columns for name/cat/directory
def get_pa_columns(directory='Factset',name='',category='',**kwargs):
    return ColumnsApi(api_client=api_client).get_pa_columns(name=name,category=category,directory=directory)

#get all PA Columns statistics
def get_pa_column_statistics():
    return ColumnStatisticsApi(api_client=api_client).get_pa_column_statistics()

#Get all unlinked templated types
def get_unlinked_template_types():
    return UnlinkedPATemplatesApi(api_client=api_client).get_default_unlinked_pa_template_types()

def get_pricing_sources(directory='Factset',name='',category='',**kwargs):
    return PricingSourcesApi(api_client=api_client).get_pa_pricing_sources(name=name,category=category,directory=directory)

def format_dataframe(df):
    """Reindex and Center Headers"""
    header_align = "center"
    text_align = "left"
    return (df.style.hide(axis="index")).set_table_styles(
        [
            dict(selector="td", props=[("text-align", text_align)]),
            dict(selector="th", props=[("text-align", header_align)]),
        ])

#format json object to dataframe
def format_stach(result):      
        stachBuilder = StachExtensionFactory.get_row_organized_builder(StachVersion.V2)
        stachExtension = stachBuilder.set_package(result).build()
        dataFramesList = stachExtension.convert_to_dataframe()
        return dataFramesList

def transform_stach_index_cols(df):
    # First, split the column names into item and date using '|' as the separator
    new_columns = pd.MultiIndex.from_tuples([col.split(' | ') for col in df.columns])
    df.columns = new_columns
    na_columns = [col for col in df.columns if pd.isnull(col[1])]

    df.set_index(na_columns, inplace=True)
    # Finally, rename the index, so it's easier to understand
    df.index.names = [col[0] for col in na_columns]
    df = df.replace('',np.nan)
    return df

def transform_stach(df):
    # First, split the column names into item and date using '|' as the separator
    new_columns = pd.MultiIndex.from_tuples([col.split(' | ') for col in df.columns])
    df.columns = new_columns
    df = df.replace('',np.nan)
    return df

#collapse multiportfolio outputs into single df
def merge_wide_outputs(data):
    dfs =[]
    for x,port in enumerate(data.keys()):
        temp_df = data[list(data.keys())[x]][0]
        temp_df['port_bench']= port
        dfs.append(temp_df)

    final_df = pd.concat(dfs)

    return final_df

#collapse multiportfolio outputs into single df
def merge_long_outputs(data):
    dfs =[]
    for x,port in enumerate(data.keys()):
        temp_df = data[list(data.keys())[x]][0]
        temp_df = temp_df.set_index('Date0')
        dfs.append(temp_df)

    final_df = pd.concat(dfs,axis=1)

    return final_df

#structure PA API post call
def build_pa_post(pa_doc):
    #build API calculation root
    pa_calcs = dict()
    #define PA date or date range
    try:
        if (pa_doc.start_date == None):
            pa_dates=PADateParameters(startdate= pa_doc.end_date,enddate=pa_doc.end_date,frequency=pa_doc.frequency)
        else:
            pa_dates=PADateParameters(startdate= pa_doc.start_date,enddate=pa_doc.end_date,frequency=pa_doc.frequency)
    except ApiException as e:
        print("Dates exception Encountered")
        print(e)
        exit()
        
    if(len(pa_doc.portfolios)!=len(pa_doc.benchmarks)):
        pa_doc.benchmarks = pa_doc.benchmarks * len(pa_doc.portfolios)

    #build portfolio/bench list
    for y in enumerate(pa_doc.portfolios):
        pa_accounts = [PAIdentifier(id=y[1], holdingsmode=pa_doc.mode)]
        pa_benchmarks = [PAIdentifier(id=pa_doc.benchmarks[y[0]], holdingsmode=pa_doc.mode)]
        #Store accts benchs and dates in our dictionary
        if pa_doc.groups == None:
            pa_calcs[str(pa_doc.portfolios[y[0]])+" | "+str(pa_doc.benchmarks[y[0]])] = PACalculationParameters(componentid=pa_doc.component_id, accounts=pa_accounts,benchmarks=pa_benchmarks,
                                                                                                                dates=pa_dates,currencyisocode=pa_doc.curr,componentdetail = pa_doc.componentdetail)
        else:
            pa_calcs[str(pa_doc.portfolios[y[0]])+" | "+str(pa_doc.benchmarks[y[0]])] = PACalculationParameters(componentid=pa_doc.component_id, accounts=pa_accounts,benchmarks=pa_benchmarks, 
                                                                                                            dates=pa_dates,currencyisocode=pa_doc.curr,componentdetail = pa_doc.componentdetail,groups=pa_doc.group_id_list)
            
    return pa_calcs

def build_group_list(groups):
    group_list = []
    for group in groups:
        groups_api = GroupsApi(api_client=api_client)
        groups = groups_api.get_pa_groups()
        group_id = [id for id in list(
                groups[0].data.keys()) if groups[0].data[id].category == group['cat'] and 
                                        groups[0].data[id].directory == group['dir'] and
                                        groups[0].data[id].name == group['name']][0]

        group_list.append(PACalculationGroup(id=group_id))
    return group_list

#calculate weighted average by group
def wavg(group,col,weight):
    d = group[col]
    w = group[weight]
    try:
        return (d * w).sum() / w.sum()
    except ZeroDivisionError:
        return d.mean()
#calculate weighted average for multiple columns
def wavg_multicol(group,col_list,weight):
    out = {}
    for col in col_list:
        try:
            out[col] = wavg(group, col, weight)
        except KeyError:
            out[col] = np.nan
    return pd.Series(out)

#wait for API Call
def wait_for_calc(post_and_calculate_response):
    try:
        if post_and_calculate_response[1] == 201:
            results = format_stach(post_and_calculate_response[0]['data'])[0]
            meta =post_and_calculate_response[0]['data']['tables']['table_0']['data']['tableMetadata']
            raw= post_and_calculate_response
        elif post_and_calculate_response[1] == 200:
            for (calculation_unit_id, calculation_unit) in post_and_calculate_response[0].data.units.items():
                print("Calculation Unit Id:" +
                    calculation_unit_id + " Failed!!!")
                print("Error message : " + str(calculation_unit.errors))
        else:
            calculation_id = post_and_calculate_response[0].data.calculationid

            status_response = PACalculationsApi(api_client).get_calculation_status_by_id(id=calculation_id)

            while status_response[1] == 202 and (status_response[0].data.status in ("Queued", "Executing")):
                max_age = '5'
                age_value = status_response[2].get("cache-control")
                if age_value is not None:
                    max_age = age_value.replace("max-age=", "")
                time.sleep(int(max_age))
                status_response = PACalculationsApi(api_client).get_calculation_status_by_id(calculation_id)
            results = dict()
            meta=dict()
            raw = dict()
            for (calculation_unit_id, calculation_unit) in status_response[0].data.units.items():
                if calculation_unit.status == "Success":
                    result_response = PACalculationsApi(api_client).get_calculation_unit_result_by_id(id=calculation_id,
                                                                                            unit_id=calculation_unit_id)
                    #append to aggregated data structure
                    if(len(status_response[0].data.units.keys())>1):
                        try:
                            results[str(calculation_unit_id)]= format_stach(result_response)[0]
                            raw[str(calculation_unit_id)] = result_response
                            meta[str(calculation_unit_id)] = result_response[0]['data']['tables']['table_0']['data']['tableMetadata']
                        except:
                            results[str(calculation_unit_id)]= format_stach(result_response[0]['data'])
                            raw[str(calculation_unit_id)] = result_response
                            meta[str(calculation_unit_id)] = result_response[0]['data']['tables']['table_0']['data']['tableMetadata']
                    else:
                        try:
                            results= format_stach(result_response)[0]
                            raw = result_response
                            meta= result_response[0]['data']['tables']['table_0']['data']['tableMetadata']
                        except:
                            results= format_stach(result_response[0]['data'])[0]
                            raw = result_response
                            meta = result_response[0]['data']['tables']['table_0']['data']['tableMetadata']

                else:
                    print("Calculation Unit Id:" +
                        calculation_unit_id + " Failed!!!")
                    print("Error message : " + str(calculation_unit.errors))

        return (results,meta,raw)

    except ApiException as e:
        print("Api exception Encountered")
        print(e)
        exit()

#PA document class
class Document:
    def __init__(self, pa_document_name = None,component_id=None,**kwargs):
        self.root= None
        self.portfolios=None
        self.benchmarks=None
        self.start_date = None
        self.end_date = None
        self.curr = None
        self.frequency = None
        self.mode = None
        self.componentdetail = None
        self.data = None
        self.ts_data = None
        self.totals=None
        self.pa_document_name = pa_document_name
        self.pa_component_category = None
        self.pa_component_name = None
        self.component_id = component_id
        self.meta=None
        self.groups= None
        self.raw = None

    def __str__(self):
        return self
    
    def set_report(self,pa_component_category,pa_component_name):
        self.pa_component_name = pa_component_name
        self.pa_component_category = pa_component_category

        self.component_id = find_component_id(self.pa_document_name,pa_component_category,pa_component_name)


    #run document template calculation
    def generate_report(self,
                portfolios,
                benchmarks,
                start_date = None,
                end_date = '0',
                frequency = 'Single',
                curr = 'USD',
                mode= 'B&H',
                componentdetail = "SECURITIES",
                groups= None,
                **kwargs):

        self.data = None
        self.portfolios = portfolios
        self.benchmarks = benchmarks
        self.start_date = start_date
        self.end_date = end_date
        self.frequency = frequency
        self.curr = curr
        self.mode = mode
        self.componentdetail = componentdetail
        self.groups=groups
        self.group_id_list=None

        if(groups!=None):
            self.group_id_list = build_group_list(groups)

        #build the post root
        pa_calcs = build_pa_post(self)
        self.root = PACalculationParametersRoot(data=pa_calcs)
        #Pass the PA inputs
        post_and_calculate_response = PACalculationsApi(api_client).post_and_calculate(pa_calculation_parameters_root=self.root,cache_control = "max-stale=0")
        # comment the above line and uncomment the below line to run the request with the cache_control header defined earlier
        #get results
        results = wait_for_calc(post_and_calculate_response)
  
        self.data = results[0]
        self.meta =results[1]
        self.raw = results[2]
        return self.data
    
    def format_point_in_time_reports(self):
        temp_df = self.data.copy()
        if(len(self.portfolios)>1):
            df = merge_wide_outputs(temp_df)
            df.index = df.index.swaplevel(0, -1)
        else:
            df = temp_df
        df=transform_stach_index_cols(df)
        df = df.stack(0)
        df.index = df.index.rename("date", level=-1)
        df.index = df.index.swaplevel(0, -1)
        self.data = df.copy()

        try:
            dft = df.xs('Total',level=0)
            df_ot = df.drop('Total',level=0)
            self.totals = dft.copy()
        except:
            df_ot = self.data.copy()

        levels = [df_ot.index.get_level_values(i) for i in range(df_ot.index.nlevels)]
        levels[0] = pd.to_datetime(levels[0])
        df_ot.index = pd.MultiIndex.from_arrays(levels, names=df_ot.index.names)

        self.ts_data = df_ot.copy()
        

        return self.data
    
    def format_range_relative_reports(self):
        temp_df = self.data.copy()
        if(len(self.portfolios)>1):
            df = merge_wide_outputs(temp_df)
            
        else:
            df = temp_df
        df=transform_stach_index_cols(df)
        
        df = df.stack(0)
        df.index = df.index.rename("end_date", level=-1)
        
        levels = [df.index.get_level_values(i) for i in range(df.index.nlevels)]
        df['range']=levels[-1]
        levels[-1] = levels[-1].str[-11:]
        df.index = pd.MultiIndex.from_arrays(levels, names=df.index.names)
        df.index = df.index.swaplevel(0, -1)

        self.data = df.copy()
        try:
            dft = df.xs('Total',level=0)
            df_ot = df.drop('Total',level=0)
            self.totals = dft.copy()
        except:
            df_ot = self.data.copy()


        levels = [df_ot.index.get_level_values(i) for i in range(df_ot.index.nlevels)]
        levels[0] = pd.to_datetime(levels[0])
        df_ot.index = pd.MultiIndex.from_arrays(levels, names=df_ot.index.names)

        self.ts_data = df_ot.copy()
        

        return self.data
    
    def format_performance_reports(self,remove_duplicate_benchs=True):
        temp_df = self.data.copy()

        if(len(self.portfolios)>1):
            #temp_df = temp_df.set_index('Date0')
            df = transform_stach(merge_long_outputs(temp_df))
            
        else:
            df = temp_df.set_index('Date0')
            df = transform_stach(df)
            self.data=df.copy()
            

        df.index = df.index.rename("end_date")

        if(remove_duplicate_benchs==True):
                df = df.loc[:, ~df.columns.duplicated()] 

        self.data=df.copy()
        #df.index = df.index.rename("end_date")
        df['range']=df.index
        df.index = df.index.str[-11:]

        try:
            dft = df.xs('Total')
            df_ot = df.drop('Total')
            self.totals = dft.copy()
        except:
            df_ot = df.copy()

        df_ot.index = pd.to_datetime(df_ot.index)

        self.ts_data = df_ot.copy()
            

        return self.data
    
    def format_risk_summary(self,rotate_time_series=False):
        #reformat output
        if(len(self.data.keys())>1):
            temp_idx= ['port']
        else:
            temp_idx = []
        temp_idx.append('Section0')
        temp_idx.append('group1')
        temp_idx.append('group2')

        dfs = []
        for x,port in enumerate(list(self.data.keys())):
            temp_df = self.data[list(self.data.keys())[x]][0]
            temp_df=temp_df.replace('', np.nan)
            temp_df['group2']  = temp_df['group2'].fillna(temp_df['group1']).fillna(temp_df['Section0'] )
            temp_df['port'] = port
            
            temp_df = temp_df.set_index(temp_idx)

            dfs.append(temp_df)
        
        risk_df = pd.concat(dfs)
        cols = risk_df.columns
        risk_df['value'] = risk_df[cols].stack().reset_index(-1, drop=True)
        
        risk_df = risk_df.drop(columns = cols)
        
        self.risk_summary = risk_df.copy()
        return self.risk_summary
    
                
def calc_unlinked_template(portfolios= ["LION:IVV-US"],
                                            benchmarks = ["DEFAULT"],
                                            start_date = None,
                                            end_date = "0D",
                                            template_type_name= 'Weights',
                                            columns = [{'name' : "Port. Ending Weight",'category':"Portfolio/Position Data",'directory' :"Factset"}],
                                            stats =["Weighted Average"],
                                            level = 'SECURITIES',
                                            groups = [{'name' : None,'category':None,'directory' :None}],
                                            holdings_mode = "B&H",
                                            report_frequency = 'Single',
                                            pricing_sources=None,
                                            **kwargs):
        
        #search all template type ids for match
        all_template_type_ids = get_unlinked_template_types()
        template_type_id = [id for id in list(all_template_type_ids[0].data.keys()) if all_template_type_ids[0].data[id].name==template_type_name][0]
        #search all column ids for matches
        col_id_list = []
        for x in range(len(columns)):
            for stat in stats:
                column = get_pa_columns(name = columns[x]['name'],category = columns[x]['category'],directory = columns[x]['directory'])
                column_id = list(column[0].data.keys())[0]
                # get column statistic ids for matches
                all_column_statistics = get_pa_column_statistics()
                column_statistic_id = [id for id in list(
                    all_column_statistics[0].data.keys()) if all_column_statistics[0].data[id].name == stat][0]
                col_id_list.append(PACalculationColumn(id=column_id,statistics=[column_statistic_id]))
        #search all groups ids for matches
        group_id_list = []
        if(groups[0]['name']!= None):
            for x in range(len(groups)):
                all_groups = get_pa_groups()
                group_id = [id for id in list(
                all_groups[0].data.keys()) if all_groups[0].data[id].category == groups[x]['category'] and 
                                      all_groups[0].data[id].directory == groups[x]['directory'] and
                                      all_groups[0].data[id].name == groups[x]['name']][0]
                group_id_list.append(PACalculationGroup(id=group_id))
        else:
            group_id_list.append(PACalculationGroup(id='E879EB3AC62F7725A0B33FCE30C3E4719B99B76F06913C62F4C6DED11D5EA197'))
        

        #set PA date/date range
        if (start_date == None):
            dates=PADateParameters(startdate= end_date,enddate=end_date,frequency=report_frequency)
        else:
            dates=PADateParameters(startdate= start_date,enddate=end_date,frequency=report_frequency)


        if(pricing_sources==None):
        #build template using first port/bench combo
            temp_params = UnlinkedPATemplateParameters(directory='personal:',
                                                    template_type_id = template_type_id,
                                                    accounts = [PAIdentifier(id=str(portfolios[0]),holdingsmode=holdings_mode)],
                                                    benchmarks = [PAIdentifier(id=str(benchmarks[0]),holdingsmode=holdings_mode)],
                                                    dates =dates,
                                                    columns =col_id_list,
                                                    )
        else:
            for x in range(len(pricing_sources)):
                pa_pricing_sources =[]
                get_pricing_sources_response = PricingSourcesApi(api_client).get_pa_pricing_sources(name=pricing_sources[x]['name'],
                                                                                    category=pricing_sources[x]['category'],
                                                                                    directory=pricing_sources[x]['directory'])
                pricing_source_id = [id for id in list(
                    get_pricing_sources_response[0].data.keys()) if
                                    get_pricing_sources_response[0].data[id].name == pricing_sources[x]['name']
                                    and get_pricing_sources_response[0].data[id].category == pricing_sources[x]['category']
                                    and get_pricing_sources_response[0].data[id].directory == pricing_sources[x]['directory']][0]


                pa_pricing_sources.append(PACalculationPricingSource(id=pricing_source_id))

            pa_datasources = PACalculationDataSources(portfoliopricingsources=pa_pricing_sources,
                                                    useportfoliopricingsourcesforbenchmark=True)
            temp_params = UnlinkedPATemplateParameters(directory='personal:',
                                                    template_type_id = template_type_id,
                                                    accounts = [PAIdentifier(id=str(portfolios[0]),holdingsmode=holdings_mode)],
                                                    benchmarks = [PAIdentifier(id=str(benchmarks[0]),holdingsmode=holdings_mode)],
                                                    dates =dates,
                                                    columns =col_id_list,
                                                    datasources=pa_datasources,
                                                    )
        #get an ID for template
        pa_root = UnlinkedPATemplateParametersRoot(temp_params)
        response = UnlinkedPATemplatesApi(api_client=api_client).create_unlinked_pa_templates(unlinked_pa_template_parameters_root = pa_root)
        comp_id = response[0]['data']['id']
        #build final calculation
        data= {}
        for portfolio,benchmark in zip(portfolios,benchmarks):
            root_index = str(portfolio)+"_x_"+str(benchmark)
            data[str(root_index)]=PACalculationParameters(componentid=comp_id ,accounts=[PAIdentifier(id=str(portfolio),holdingsmode=holdings_mode)],benchmarks=[PAIdentifier(id=str(benchmark),holdingsmode=holdings_mode)],dates=dates,columns =col_id_list,groups=group_id_list,componentdetail = level)
            try:
                pa_root = PACalculationParametersRoot(data=data)
            except Exception as e:
                print(f"An error occurred: {e}")   
        #get data
        response = PACalculationsApi(api_client).post_and_calculate(pa_calculation_parameters_root=pa_root,cache_control = "max-stale=0",x_fact_set_api_long_running_deadline=0)
        results = wait_for_calc(response)
        return results
