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
import requests
import json
import time
from urllib3 import Retry
from urllib import parse
load_dotenv()

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

#format json object to dataframe
def format_stach(result):      
        stachBuilder = StachExtensionFactory.get_row_organized_builder(StachVersion.V2)
        stachExtension = stachBuilder.set_package(result).build()
        dataFramesList = stachExtension.convert_to_dataframe()
        return dataFramesList

#wait for API Call
def wait_for_calc(post_and_calculate_response):
    try:
        if post_and_calculate_response[1] == 201:
            results = format_stach(post_and_calculate_response[0]['data'])[0]
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
            for (calculation_unit_id, calculation_unit) in status_response[0].data.units.items():
                if calculation_unit.status == "Success":
                    result_response = PACalculationsApi(api_client).get_calculation_unit_result_by_id(id=calculation_id,
                                                                                            unit_id=calculation_unit_id)
                    #append to aggregated data structure
                    if(len(status_response[0].data.units.keys())>1):
                        try:
                            results[str(calculation_unit_id)]= format_stach(result_response)[0]
                        except:
                            results[str(calculation_unit_id)]= format_stach(result_response[0]['data'])
                    else:
                        try:
                            results= format_stach(result_response)[0]
                        except:
                            results= format_stach(result_response[0]['data'])[0]
                else:
                    print("Calculation Unit Id:" +
                        calculation_unit_id + " Failed!!!")
                    print("Error message : " + str(calculation_unit.errors))
        return results

    except ApiException as e:
        print("Api exception Encountered")
        print(e)
        exit()

#PA document class
class DocumentTemplate:
    def __init__(self,component_id=None, pa_document_name = None, pa_component_category = None, pa_component_name = None,**kwargs):
        if(component_id==None):
            self.component_id = find_component_id(pa_document_name,pa_component_category,pa_component_name)
        else:
            self.component_id = component_id
        self.root= None
        self.data = None
    def __str__(self):
        return self
    #run document template calculation
    def run_calc(self,
                portfolios,
                benchmarks,
                start_date = None,
                end_date = '0',
                frequency = 'Single',
                curr = 'USD',
                mode= 'B&H',
                componentdetail = "SECURITIES",
                **kwargs):
        
        #build API calculation root
        pa_calcs = dict()
        #define PA date or date range
        if (start_date == None):
            pa_dates=PADateParameters(startdate= end_date,enddate=end_date,frequency=frequency)
        else:
            pa_dates=PADateParameters(startdate= start_date,enddate=end_date,frequency=frequency)    
        
        #build portfolio/bench list
        for y in enumerate(portfolios):
            pa_accounts = [PAIdentifier(id=y[1], holdingsmode=mode)]
            pa_benchmarks = [PAIdentifier(id=benchmarks[y[0]], holdingsmode=mode)]
            #Store accts benchs and dates in our dictionary
            pa_calcs[str(portfolios[y[0]]+'_x_'+benchmarks[y[0]])] = PACalculationParameters(componentid=self.component_id, accounts=pa_accounts,benchmarks=pa_benchmarks, dates=pa_dates,currencyisocode=curr,componentdetail = componentdetail)

        self.root = PACalculationParametersRoot(data=pa_calcs)
        #Pass the PA inputs
            #Break up the calc
        post_and_calculate_response = PACalculationsApi(api_client).post_and_calculate(pa_calculation_parameters_root=self.root,cache_control = "max-stale=0")
        # comment the above line and uncomment the below line to run the request with the cache_control header defined earlier
        #get results
        results = wait_for_calc(post_and_calculate_response)
        self.data = results    
        return results
                
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


http_headers = {"Content-type": "application/json", "Accept": "application/json"}

def URL_encode(value_to_encode):
            """Encodes String Replace Special Characters for URL Encoding"""
            return parse.quote(value_to_encode, safe="")


class web_requests:
        @staticmethod
        def http_delete(URL, fds_username_hyphen_serial, fds_apikey):
            try:
                response = requests.delete(
                    url=URL,
                    auth=(fds_username_hyphen_serial, fds_apikey),
                    headers=http_headers,
                )

                return True, response

            except Exception as e:
                return False, e

        @staticmethod
        def http_get(URL, fds_username_hyphen_serial, fds_apikey):
            try:
                return True, requests.get(
                    URL,
                    auth=(fds_username_hyphen_serial, fds_apikey),
                    headers=http_headers,
                )
            except Exception as e:
                return False, (e)

        # post web request
        @staticmethod
        def http_put(URL, json_string, fds_username_hyphen_serial, fds_apikey):
            try:
                return True, requests.put(
                    URL,
                    auth=(fds_username_hyphen_serial, fds_apikey),
                    headers=http_headers,
                    data=json.dumps(json_string),
                )
            except Exception as e:
                return False, str(e)

def get_err_detail(
            status_code, is_docbase=False, is_lookup=False, pa_document=""
        ):
            if status_code == 204:
                return "Model Account does not exist"
            elif status_code == 400 and is_docbase:
                return "Invalid PA document name or Query Parameter"
            elif status_code == 400 and is_lookup:
                return "Invalid Input Parameter(s)"
            elif status_code == 400:
                return "Invalid POST Body or Account Information"
            elif status_code == 401:
                return "Missing or Invalid Authentication"
            elif status_code == 403:
                return "User forbidden with Current Credentials"
            elif status_code == 404:
                return (
                    f"Docuement Not Found: {pa_document}"
                    if (pa_document)
                    else "Document Not Found"
                )
            elif status_code == 500:
                return "Request timed out."
            else:
                return ""


def check_mp_key(dict_data, key):
    if key not in dict_data:
        dict_data[key] = {}
    return dict_data
def create_mp_object(list_keys, list_values, symbol_index, date_index):
    dict_results = {}
    for x in range(len(list_keys)):
        if x != symbol_index and x != date_index:
            dict_results[list_keys[x]] = list_values[x]
    return dict_results

def make_model_portfolio(
    account_name_path, df
):
    """Create a New or Update and Existing Account"""
    URL = f"{host}/analytics/accounts/v3/models/{URL_encode(account_name_path)}"
    bSuccess, response = web_requests().http_put(
        URL=URL,
        json_string=make_model_portfolio_json(df)[1],
        fds_username_hyphen_serial=fds_username,
        fds_apikey=fds_api_key,
    )
    if bSuccess and response.status_code in (201, 200):
        return (
            True,
            f"Model Portfolio {account_name_path} Successfully {'Created' if response.status_code==201 else 'Updated'} (Status Code: {response.status_code})",
            "",
        )
    else:
        errMsg = (
            f"Failed to Create Account (Status Code: {response.status_code})"
        )
        errDetail = get_err_detail(
            response.status_code
        )
        return False, errMsg, errDetail



def make_model_portfolio_json(dataFrame):

    """
    Expects a pandas Dataframe, where the First Row are the dictionary keys.
    date,symbol,weight,price,priceiso
    20220203,FDS,25,1,usd
    20220203,AAPL,25,2,usd
    20220203,TSLA,25,3,usd
    20220203,IBM,25,4,usd

    Must have a date and symbol column
    """

    csv_model_portfolio_json = {}
    symbol_index = None
    date_index = None
    column_list = list(dataFrame.columns)

    if "symbol" in list(dataFrame.columns): 
        symbol_index = dataFrame.columns.get_loc("symbol")

    if "date" in list(dataFrame.columns):
        date_index = dataFrame.columns.get_loc("date")

    if symbol_index is None or date_index is None: 
        return False, "Missing Date or Symbol Column"
    
    for index, row in dataFrame.iterrows():
        csv_model_portfolio_json = (
            check_mp_key(
                dict_data=csv_model_portfolio_json,
                key=row[date_index],
            )
        )
        csv_model_portfolio_json[row[date_index]][
            row[symbol_index]
        ] = create_mp_object(
            column_list, row, symbol_index, date_index
        )
        
    return True, {"data": {"iterative": csv_model_portfolio_json}}


