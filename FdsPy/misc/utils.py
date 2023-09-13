import fredapi
import pandas as pd
import os
from pytrends.request import TrendReq
import numpy as np
import re

from dotenv import load_dotenv
load_dotenv()
fred_api_key = os.getenv("FRED_API_KEY")

def get_fred_series(series_id,start_date, end_date, frequency=None):
    try:
        if (frequency!=None):
            data = fredapi.Fred(fred_api_key).get_series(series_id, start_date,end_date, frequency=frequency)
        else:
            data = fredapi.Fred(fred_api_key).get_series(series_id, start_date,end_date)
        return pd.DataFrame(data).rename(columns={0: series_id})
    except Exception as e: 
        print(e)
        
def get_google_trends(search_list,start_date,end_date):
    try:
        pytrends = TrendReq(hl='en-US', tz=360,timeout=(10,25),retries=3, backoff_factor=20) 
        date_range = str(start_date)+' '+str(end_date)
        pytrends.build_payload(search_list, cat=0, timeframe=date_range)
        data = pytrends.interest_over_time()
        return data
    except Exception as e: 
        print(e)

def replace_equation(map_dict, equation):
    keys = sorted(map_dict, key=len, reverse=True) # sorted by length, in case one expression is a prefix of another
    regexp = re.compile('|'.join(map(re.escape, keys)))

    while re.search('#P.P', equation):
        equation = regexp.sub(lambda match: '(' + map_dict[match.group(0)] + ')', equation)
    return equation  # Add a semicolon at the end of the equation

def convert_formulas_with_ref_var(variables,formulas):

    concatenated_variables = []
    for variable in variables:
        concatenated_variable = "#P." + str(variable)
        concatenated_variables.append(concatenated_variable)
    mapping_table = dict(zip(concatenated_variables, formulas))

    map_dict = mapping_table
    transformed_formulas = []
    for formula in formulas:
        transformed_formulas.append(replace_equation(map_dict, formula))

    return transformed_formulas

