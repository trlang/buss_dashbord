import pandas as pd
import requests
import json

def vaer_data():
    url = 'https://api.met.no/weatherapi/locationforecast/2.0/complete?altitude=35&lat=59.92453&lon=10.709682'
    headers = requests.utils.default_headers()
    headers.update(
        {
            'User-Agent': 'Munthes',
        }
    )
    
    response = requests.get(url, headers=headers)
    response_dict = json.loads(response.text)
    
    
    tidsserie_temp = pd.DataFrame()
    for i in range(len(response_dict['properties']['timeseries'])):
        instans = response_dict['properties']['timeseries'][i]['data']['instant']['details']
        df = pd.DataFrame(instans, index=[response_dict['properties']['timeseries'][i]['time']])
        tidsserie_temp = pd.concat([tidsserie_temp, df])
        
    tidsserie_regn = pd.DataFrame()
    for i in range(len(response_dict['properties']['timeseries'])):
        try:
            instans = response_dict['properties']['timeseries'][i]['data']['next_1_hours']['details']
            df = pd.DataFrame(instans, index=[response_dict['properties']['timeseries'][i]['time']])
            tidsserie_regn = pd.concat([tidsserie_regn, df])
        except KeyError:
            pass
    return tidsserie_regn