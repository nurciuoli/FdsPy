import fredapi
import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv
load_dotenv()
fred_api_key = os.getenv("FRED_API_KEY")

class Fred:
    def __init__(self):
        return None
    def __str__(self):
        return self
    def get_fred_series(self,series_id,start_date, end_date, frequency):
        data = fredapi.Fred(fred_api_key).get_series(series_id, start_date,end_date, frequency=frequency)
        return pd.DataFrame(data).rename(columns={0: series_id})
