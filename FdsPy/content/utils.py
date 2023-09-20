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
def search_symbols(entity_match_request):
    
    headers = {'Accept': 'application/json','Content-Type': 'application/json'}

    # CREATE THE POST

    #create a post request and print the Status Code

    entity_match_post = json.dumps(entity_match_request)
    entity_match_response = requests.post(url = entity_match_endpoint, data=entity_match_post, auth = authorization, headers = headers, verify= False )

    entity_match_data = entity_match_response.json()
    entity_match_df = json_normalize(entity_match_data['data'])
    # SHOW THE LAST FIVE RECORDS

    return entity_match_df
