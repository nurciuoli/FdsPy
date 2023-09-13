import time
import pandas as pd
import os
from fds.analyticsapi.engines import ApiException
from fds.analyticsapi.engines.api.spar_calculations_api import SPARCalculationsApi
from fds.analyticsapi.engines.api.components_api import ComponentsApi
from fds.analyticsapi.engines.api_client import ApiClient
from fds.analyticsapi.engines.configuration import Configuration
from fds.analyticsapi.engines.model.spar_calculation_parameters_root import SPARCalculationParametersRoot
from fds.analyticsapi.engines.model.spar_calculation_parameters import SPARCalculationParameters
from fds.analyticsapi.engines.model.spar_date_parameters import SPARDateParameters
from fds.analyticsapi.engines.model.spar_identifier import SPARIdentifier
from fds.protobuf.stach.extensions.StachVersion import StachVersion
from fds.protobuf.stach.extensions.StachExtensionFactory import StachExtensionFactory

import os
from urllib3 import Retry
import time
from dotenv import load_dotenv
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

def calc_spar_data(doc_name,comp_name,comp_cat,ports,bench,bench_prefix,ret_type,sd,ed,freq,curr):
    results = dict()
    try:
        spar_document_name = doc_name
        spar_component_name = comp_name
        spar_component_category = comp_cat
        spar_benchmark_prefix = bench_prefix
        spar_benchmark_return_type = ret_type
        currency = curr
        startdate = sd
        enddate = ed
        frequency = freq
        # uncomment the below code line to setup cache control; max-stale=0 will be a fresh adhoc run and the max-stale value is in seconds.
        # Results are by default cached for 12 hours; Setting max-stale=300 will fetch a cached result which is 5 minutes older.
        cache_control = "max-stale=0"
        spar_calcs = dict()
        
        components_api = ComponentsApi(api_client)

        get_components_response = components_api.get_spar_components(spar_document_name)
        
        component_id = [id for id in list(get_components_response[0].data.keys()) if get_components_response[0].data[id].name == spar_component_name and get_components_response[0].data[id].category == spar_component_category][0]
        

        spar_account_identifier = SPARIdentifier(id=bench, returntype=spar_benchmark_return_type,
                                                 prefix=spar_benchmark_prefix)
        spar_accounts = [spar_account_identifier]
        spar_dates = SPARDateParameters(startdate, enddate, frequency)
        
        spar_calcs[str(bench)]=SPARCalculationParameters(componentid=component_id, accounts=spar_accounts,
                                                                         dates=spar_dates, currencyisocode=currency)
        
        for x,y in enumerate(ports):
            spar_account_identifier = SPARIdentifier(id=str(y), returntype=spar_benchmark_return_type)
            
            spar_accounts = [spar_account_identifier]
            spar_calcs[str(y)]=SPARCalculationParameters(componentid=component_id, accounts=spar_accounts,
                                                                         dates=spar_dates, currencyisocode=currency)
        

        
        spar_calculation_parameter_root = SPARCalculationParametersRoot(
            data=spar_calcs)

        post_and_calculate_response = SPARCalculationsApi(api_client).post_and_calculate(
            spar_calculation_parameters_root=spar_calculation_parameter_root, cache_control=cache_control)
        
        if post_and_calculate_response[1] == 201:

            return format_stach(post_and_calculate_response[0]['data'])

        if post_and_calculate_response[1] == 202 or post_and_calculate_response[1] == 200:
            calculation_id = post_and_calculate_response[0].data.calculationid

            status_response = SPARCalculationsApi(api_client).get_calculation_status_by_id(id=calculation_id)

            while status_response[1] == 202 and (status_response[0].data.status in ("Queued", "Executing")):
                max_age = '5'
                age_value = status_response[2].get("cache-control")
                if age_value is not None:
                    max_age = age_value.replace("max-age=", "")
                time.sleep(int(max_age))
                status_response = SPARCalculationsApi(api_client).get_calculation_status_by_id(calculation_id)

            for (calculation_unit_id, calculation_unit) in status_response[0].data.units.items():
                if calculation_unit.status == "Success":
                    result_response = SPARCalculationsApi(api_client).get_calculation_unit_result_by_id(id=calculation_id,
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
        else:
            print("Calculation creation failed")
            print("Error status : " + str(post_and_calculate_response[1]))
            print("Error message : " + str(post_and_calculate_response[0]))

    except ApiException as e:
        print("Api exception Encountered")
        print(e)
        exit()

       
    return results
    
def format_stach(result):      
    #Format JSON object nand convert to dataframe
    stachBuilder = StachExtensionFactory.get_row_organized_builder(StachVersion.V2)
    stachExtension = stachBuilder.set_package(result).build()
    dataFramesList = stachExtension.convert_to_dataframe()
    return dataFramesList

    