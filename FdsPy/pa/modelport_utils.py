import os
from urllib3 import Retry
import time
import requests
from dotenv import load_dotenv
import pandas as pd
import numpy as np
from fds.analyticsapi.engines.configuration import Configuration
import requests
import json
from fds.analyticsapi.engines.api_client import ApiClient
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



def URL_encode(value_to_encode):
            """Encodes String Replace Special Characters for URL Encoding"""
            return parse.quote(value_to_encode, safe="")

def http_delete(URL, fds_username_hyphen_serial, fds_apikey):
    try:
        response = requests.delete(
            url=URL,
            auth=(fds_username_hyphen_serial, fds_apikey),
            headers={"Content-type": "application/json", "Accept": "application/json"},
        )

        return True, response

    except Exception as e:
        return False, e

def http_get(URL, fds_username_hyphen_serial, fds_apikey):
    try:
        return True, requests.get(
            URL,
            auth=(fds_username_hyphen_serial, fds_apikey),
            headers={"Content-type": "application/json", "Accept": "application/json"},
        )
    except Exception as e:
        return False, (e)

def http_put(URL, json_string, fds_username_hyphen_serial, fds_apikey):
    try:
        return True, requests.put(
            URL,
            auth=(fds_username_hyphen_serial, fds_apikey),
            headers={"Content-type": "application/json", "Accept": "application/json"},
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

def make_model_portfolio(
    account_name_path, df
):
    """Create a New or Update and Existing Account"""
    URL = f"{host}/analytics/accounts/v3/models/{URL_encode(account_name_path)}"
    bSuccess, response = http_put(
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