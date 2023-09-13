
import pandas as pd
import numpy as np
import pandas as pd
import os
import io
import requests
import base64
import time
import urllib.parse 
import re
from dotenv import load_dotenv
load_dotenv()

host ="https://api.factset.com"
fds_username = os.getenv("FACTSET_USERNAME")
fds_api_key = os.getenv("FACTSET_API_KEY")

# Assemble basic auth user + pass
auth = bytes(f"{fds_username.upper()}:{fds_api_key}", "utf-8")

headers = {
    'Authorization': 'Basic %s' % str(base64.b64encode(auth).decode('ascii'))
}
api = 'https://api.factset.com/analytics/quant/qre'

#PA document class
class FpeRequest:
    def __init__(self,script,data=None, status=None,log=None,calc_id = None):
        self.script = script
    def __str__(self):
        return self

def post_fpe_script(script):
    fpe_req = FpeRequest(script)
    # Start the QRE calculation
    r = requests.post(
        api + '/v1/calculations', 
        headers=headers, 
        json={'script': script} # Using `json` will encode the script as needed
    )
    fpe_req.status = format(r.status_code)

    # Calculation returns JSON body
    fpe_req.calc_id = r.json()['id']

    # Calculation also returns a `Location` header which contains a relative URL for where to poll for calculation status
    pollUrl = r.headers['Location']

    # The unique id for this calculation. Used later to get the log and ouput
    calculation_id = r.json()['id']

    #print("Polling url:", pollUrl)

    # Poll for script completion
    while True:
        #print("Polling for results...")
        r = requests.get(api + pollUrl, headers=headers)
        
        if r.status_code == 200:
            break
        elif r.status_code > 299:
            print('Pickup request failed: ' + r.status_code)
            logs = requests.get(
            api + '/v1/calculations/'+calculation_id+'/log', 
            headers=headers
        )
            print("Logs:" + logs.content.decode('utf8'))
            fpe_req.log = logs.content.decode('utf8')
            raise SystemExit('Pickup request failed')
        time.sleep(10)
    
    #print("Run finished")
    # Get script log 
    
    # Get output (if there is any)
    output = requests.get(
        api + '/v1/calculations/'+calculation_id+'/output', 
        headers=headers
    )
    df =pd.read_csv(io.StringIO(output.content.decode('utf8')))
    fpe_req.data = df
    return fpe_req


def get_time_series(start,stop,freq,cal):
    script = '\
from fds.quant.dates import TimeSeries \n\
from fds.quant.output.dataframe import to_csv \n\
import pandas as pd \n\
time_series = TimeSeries(start="'+start+'",stop = "'+stop+'",freq="'+freq+'",calendar = "'+cal+'") \n\
da = pd.Series(time_series.dates) \n\
to_csv(da)\
    '
    req = post_fpe_script(script)
    req.data = req.data.iloc[:,1].to_list()
    return req

def get_univ_constituents(universe_formula,start,stop,freq,cal):
    script = '\
from fds.quant.universe import IdentifierUniverse, ScreeningExpressionUniverse \n\
from fds.quant.dates import TimeSeries \n\
from fds.quant.screening import Screen, ScreeningExpression \n\
import pandas as pd \n\
from fds.quant.output.dataframe import to_csv \n\
univ = ScreeningExpressionUniverse("'+universe_formula+'", time_series = TimeSeries(start="'+start+'",stop = "'+stop+'",freq="'+freq+'",calendar = "'+cal+'")) \n\
univ.calculate() \n\
to_csv(univ.constituents)\
    '
    req = post_fpe_script(script)
    req.data = req.data.set_index('symbol')
    return req


def screen_scr_univ(universe_formula,start,stop,freq,cal,formulas,columns):
    script = '\
from fds.quant.universe import IdentifierUniverse, ScreeningExpressionUniverse \n\
from fds.quant.dates import TimeSeries \n\
from fds.quant.screening import Screen, ScreeningExpression \n\
import pandas as pd \n\
from fds.quant.output.dataframe import to_csv \n\
scr = Screen(universe = ScreeningExpressionUniverse("'+universe_formula+'", time_series = TimeSeries(start="'+start+'",stop = "'+stop+'",freq="'+freq+'",calendar = "'+cal+'")),formulas ='+str(formulas)+',columns = '+str(columns)+') \n\
scr.calculate()\n\
to_csv(scr.data)\
    '
    req = post_fpe_script(script)
    req.data = req.data.set_index(['date','symbol'])
    return req

def fql_scr_univ(universe_formula,start,stop,freq,cal,formulas,columns):
    script = '\
from fds.quant.universe import IdentifierUniverse, ScreeningExpressionUniverse \n\
from fds.quant.dates import TimeSeries \n\
from fds.quant.fql import FQL, FQLExpression \n\
import pandas as pd \n\
from fds.quant.output.dataframe import to_csv \n\
scr = FQL(universe = ScreeningExpressionUniverse("'+universe_formula+'", time_series = TimeSeries(start="'+start+'",stop = "'+stop+'",freq="'+freq+'",calendar = "'+cal+'")),formulas ='+str(formulas)+',columns = '+str(columns)+') \n\
scr.calculate()\n\
to_csv(scr.data)\
    '
    req = post_fpe_script(script)
    req.data = req.data.set_index(['date','symbol'])
    return req

def screen_ids(ids,start,stop,freq,cal,formulas,columns):
    script = '\
from fds.quant.universe import IdentifierUniverse, ScreeningExpressionUniverse \n\
from fds.quant.dates import TimeSeries \n\
from fds.quant.screening import Screen, ScreeningExpression \n\
import pandas as pd \n\
from fds.quant.output.dataframe import to_csv \n\
scr = Screen(universe = IdentifierUniverse('+str(ids)+', time_series = TimeSeries(start="'+start+'",stop = "'+stop+'",freq="'+freq+'",calendar = "'+cal+'")),formulas ='+str(formulas)+',columns = '+str(columns)+') \n\
scr.calculate()\n\
to_csv(scr.data)\
    '
    req = post_fpe_script(script)
    req.data = req.data.set_index(['date','symbol'])
    return req

def fql_ids(ids,start,stop,freq,cal,formulas,columns):
    script = '\
from fds.quant.universe import IdentifierUniverse, ScreeningExpressionUniverse \n\
from fds.quant.dates import TimeSeries \n\
from fds.quant.fql import FQL, FQLExpression \n\
import pandas as pd \n\
from fds.quant.output.dataframe import to_csv \n\
scr = FQL(universe = IdentifierUniverse('+str(ids)+', time_series = TimeSeries(start="'+start+'",stop = "'+stop+'",freq="'+freq+'",calendar = "'+cal+'")),formulas ='+str(formulas)+',columns = '+str(columns)+') \n\
scr.calculate()\n\
to_csv(scr.data)\
    '
    req = post_fpe_script(script)
    req.data = req.data.set_index(['date','symbol'])
    return req

def post_file(path,data):
    #set environment to upload files
    # - interactive
    # - batch
    env = 'interactive'
    #env = 'batch'
    
    uploadUrl = api + '/v1/files/' + env + '/' + path

    r = requests.post(uploadUrl,headers=headers,data=data.to_csv())
    #print('HTTP Status: {}'.format(r.status_code))
    upload_id = r.json()['id']
    #print("Upload id: " + upload_id)
    pollUrl = r.headers['Location']
    # Poll to see when the file is done uploading
    while True:
        #print("Polling for upload finish...")
        r = requests.get(api + pollUrl, headers=headers)
        if r.status_code == 200:
            break
        elif r.status_code > 299:
            print('Pickup request failed: ' + r.status_code)
            raise SystemExit('Pickup request failed')
        time.sleep(5)
    #print('Status: ' + r.json()['status']+'| Upload Path: '+path)
    return path

def post_file_to_ofdb(name,data):
    #set environment to upload files
    # - interactive
    # - batch
    env = 'interactive'
    #env = 'batch'
    path = name+'.csv'
    uploadUrl = api + '/v1/files/' + env + '/' + path

    r = requests.post(uploadUrl,headers=headers,data=data.to_csv())
    #print('HTTP Status: {}'.format(r.status_code))
    upload_id = r.json()['id']
    #print("Upload id: " + upload_id)
    pollUrl = r.headers['Location']
    # Poll to see when the file is done uploading
    while True:
        #print("Polling for upload finish...")
        r = requests.get(api + pollUrl, headers=headers)
        if r.status_code == 200:
            break
        elif r.status_code > 299:
            print('Pickup request failed: ' + r.status_code)
            raise SystemExit('Pickup request failed')
        time.sleep(5)
    #print('Status: ' + r.json()['status']+'| Upload Path: '+path)
    script = "\
import pandas as pd \n\
from fds.quant.ofdb import OFDB \n\
from fds.quant.output.dataframe import to_csv \n\
df = pd.read_csv('"+path+"') \n\
OFDB(" + path+",data = df,create_acct = True, acct_desc = 'Created with FPE API')"
    req = post_fpe_script(script)
    return req

def retrieve_file(path):
    script = "\
import pandas as pd \n\
from fds.quant.output.dataframe import to_csv \n\
to_csv(pd.read_csv('"+path+"'))\
    "
    req = post_fpe_script(script)
    req.data = req.data.set_index(['date','symbol']).iloc[:,1:]
    return req
