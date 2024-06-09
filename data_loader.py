import pandas as pd
import json
import requests,os

class DataLoader:
    def __init__(self, file_path):
        self.file_path = file_path

    def load_data(self):
        with open(self.file_path) as f:
            data = json.load(f)
        return pd.json_normalize(data)
    
    
class ApiDataLoader:
    def get_data(eventtimestampstart, eventtimestampend):
        api_key = os.getenv('API_KEY', 'default_key_if_none')
        api_url = f'https://results.us.securityeducation.com/api/reporting/v0.3.0/phishing_extended?filter[_eventtimestamp_start]={eventtimestampstart}&filter[_eventtimestamp_end]={eventtimestampend}'

        headers = {
            'Accept': 'application/json',
            'x-apikey-token': api_key,
            'Content-Type': 'application/json'
        }
        response = requests.get(api_url, headers=headers)
        return response.json()
