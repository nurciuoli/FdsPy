import requests
import json
import pandas as pd
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from pandas import json_normalize
from dotenv import load_dotenv
load_dotenv()
import os

fds_username = os.getenv("FACTSET_USERNAME")
fds_api_key = os.getenv("FACTSET_API_KEY")
authorization=(fds_username,fds_api_key)

personal_username = os.getenv("FDS_PERSONAL_USERNAME")
personal_api_key = os.getenv("FDS_PERSONAL_KEY")

entity_match_endpoint = 'https://api.factset.com/content/factset-concordance/v2/entity-match'
def search_symbols(entity_data):
    
    headers = {'Accept': 'application/json','Content-Type': 'application/json'}

    # CREATE THE POST

    #create a post request and print the Status Code

    entity_match_post = json.dumps(entity_data)
    entity_match_response = requests.post(url = entity_match_endpoint, data=entity_match_post, auth = authorization, headers = headers, verify= True )

    entity_match_data = entity_match_response.json()
    entity_match_df = json_normalize(entity_match_data['data'])
    # SHOW THE LAST FIVE RECORDS

    return entity_match_df


people_match_endpoint = 'https://api.factset.com/content/factset-concordance/v2/people-match'
def search_people(people_data):
    
    headers = {'Accept': 'application/json','Content-Type': 'application/json'}

    # CREATE THE POST

    #create a post request and print the Status Code

    match_post = json.dumps(people_data)
    match_response = requests.post(url = people_match_endpoint, data=match_post, auth = authorization, headers = headers, verify= True )

    match_data = match_response.json()
    match_df = json_normalize(match_data['data'])
    # SHOW THE LAST FIVE RECORDS

    return match_df

def id_lookup(search,search_type= ['equities'],result_limit=10):
    #ID Lookup API endpoint for the request call
    id_endpoint = 'https://api.factset.com/idsearch/v1/idsearch'
    headers = {'Accept': 'application/json','Content-Type': 'application/json'}
    jsondata = {}
    query={}
    query['pattern'] = search
    query['entities'] = search_type
    settings={}
    settings['result_limit'] = result_limit
    jsondata['query'] = query
    jsondata['settings'] = settings

    # Create a POST Request
    id_post = json.dumps(jsondata)
    id_response = requests.post(url = id_endpoint, data=id_post, auth = authorization, headers = headers)
    return pd.json_normalize(id_response.json()['typeahead']['results']).set_index('symbol')
    #Display the results


def get_qfl_factors(library_request={}):
    library_endpoint = 'https://api.factset.com/content/factset-quant-factor-library/v1/library'
    headers = {'Accept': 'application/json','Content-Type': 'application/json'}
    #create a post request
    #helper is a utility endpoint, no parameters are required to return the list of metrics
    library_post = json.dumps(library_request)
    library_response = requests.post(url = library_endpoint, data = library_post, auth = authorization, headers = headers, verify= True)
    #create a dataframe from POST request, show dataframe properties
    library_data = json.loads(library_response.text)
    library_df = json_normalize(library_data['data'])
    return library_df


def get_formulas():
    url = 'https://api.factset.com/data-dictionary/navigator/products'
    headers = {
        'accept': 'application/json',
    }

    # Replace 'username' and 'password' with your own credentials.
    response = requests.get(url, headers=headers, auth=HTTPBasicAuth(personal_username, personal_api_key))

    df = pd.DataFrame(response.json())
    return df

def search_formulas(terms):
    url = 'https://api.factset.com/data-dictionary/navigator/basic_search'
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
    }
    data = {
        "searchTerms": terms
    }

    # replace 'username' and 'password' with your own credentials
    response = requests.post(url, headers=headers, data=json.dumps(data), auth=HTTPBasicAuth(personal_username, personal_api_key))

    df = pd.DataFrame(response.json()['results'])
    #df = response.json()
    df_data = pd.json_normalize(df['dataItem'])
    df_product = pd.json_normalize(df['product'])

    df_final = pd.concat([df_data, df_product], axis=1)
    return df_final

