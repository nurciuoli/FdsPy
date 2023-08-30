import fredapi
import pandas as pd
import os
from pytrends.request import TrendReq
from dotenv import load_dotenv
load_dotenv()
fred_api_key = os.getenv("FRED_API_KEY")

def get_fred_series(series_id,start_date, end_date, frequency):
    try:
        data = fredapi.Fred(fred_api_key).get_series(series_id, start_date,end_date, frequency=frequency)
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

        