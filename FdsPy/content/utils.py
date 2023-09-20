import requests
import json
import pandas as pd
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from pandas import json_normalize
from dotenv import load_dotenv
load_dotenv()
import os

fds_username = os.getenv("FACTSET_USERNAME")
fds_api_key = os.getenv("FACTSET_API_KEY")
authorization=(fds_username,fds_api_key)

entity_match_endpoint = 'https://api.factset.com/content/factset-concordance/v2/entity-match'
def search_symbols(entity_data):
    
    headers = {'Accept': 'application/json','Content-Type': 'application/json'}

    # CREATE THE POST

    #create a post request and print the Status Code

    entity_match_post = json.dumps(entity_data)
    entity_match_response = requests.post(url = entity_match_endpoint, data=entity_match_post, auth = authorization, headers = headers, verify= False )

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
    match_response = requests.post(url = people_match_endpoint, data=match_post, auth = authorization, headers = headers, verify= False )

    match_data = match_response.json()
    match_df = json_normalize(match_data['data'])
    # SHOW THE LAST FIVE RECORDS

    return match_df

def id_lookup(search,search_type,result_limit):
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