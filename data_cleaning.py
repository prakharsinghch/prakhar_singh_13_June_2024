import pandas as pd
import json
from collections import defaultdict

def data_convert(filename):
    df=pd.read_csv(filename)
    data_cols = df.columns.tolist()
    result = defaultdict(dict)
    for _, row in df.iterrows():
            key = row['store_id']
            result[key] = {col: row[col] for col in data_cols if col!='store_id'} 
    return result

def data_convert_days(filename, nest):
    df=pd.read_csv(filename)
    data_cols = df.columns.tolist()
    result = defaultdict(dict)
    for _, row in df.iterrows():
            key = row['store_id']
            nest_key = str(row[nest])
            result[key][nest_key] = {col: row[col] for col in data_cols if (col!=nest and col!='store_id')}
    return result


def data_cleaning():
    folder_name = "./store-monitoring-data/"
    timezones = data_convert(folder_name+"timezones.csv")
    menu_hours = data_convert_days(folder_name + "menu_hours.csv" , nest='dayOfWeek')
    store_status = data_convert_days(folder_name+"store_status.csv",nest='timestamp_utc')

    return timezones,menu_hours,store_status



