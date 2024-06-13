import pandas as pd
import json
import requests
import os
import csv
from io import StringIO

class DataLoader:
    def __init__(self, file_path):
        self.file_path = file_path

    def load_data(self):
        with open(self.file_path) as f:
            data = json.load(f)
        return pd.json_normalize(data)
    
    
class ApiDataLoader:
    def __init__(self, start_date, end_date):
        self.url_base = "https://results.us.securityeducation.com/api/reporting/v0.3.0/phishing_extended"
        self.headers = {
            'Content-Type': 'application/json',
            'x-apikey-token': os.getenv('API_KEY', 'default_key_if_none')
        }
        self.start_date = start_date
        self.end_date = end_date

    def fetch_data(self, page_number=1):
        paginated_url = (f"{self.url_base}?filter[_eventtimestamp_start]={self.start_date}&"
                         f"filter[_campaignstartdate_end]={self.end_date}&page[number]={page_number}")
        response = requests.get(paginated_url, headers=self.headers)
        return response.json()

    def flatten_dict(self, d, parent_key='', sep='_'):
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self.flatten_dict(v, new_key, sep=sep).items())
            else:
                clean_key = new_key.replace('attributes_', '')
                items.append((clean_key, v))
        return dict(items)

    def save_to_csv(self, data, filename):
        """Save the flattened data to a CSV file."""
        if not data:
            return  # Check if data is empty
        csv_columns = data[0].keys()  # Assumes all dictionaries have the same structure
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for row in data:
                writer.writerow(row)

    def stream_data(self):
        # Initial fetch to determine the number of pages
        initial_data = self.fetch_data()
        total_pages = (initial_data['meta']['count'] - 1) // initial_data['meta']['page_size'] + 1
        
        # Fetch and stream data for each page
        all_data = []
        for page_number in range(1, total_pages + 1):
            response_data = self.fetch_data(page_number)
            page_data = [self.flatten_dict(item) for item in response_data['data']]
            all_data.extend(page_data)
            progress = (page_number / total_pages) * 100
            print(f"Page {page_number}/{total_pages}, Progress: {progress:.2f}%")
            if page_number == total_pages:
                print("Data streaming complete.")
        
        self.save_to_csv(all_data, 'data/output.csv')

# Usage example
#api_loader = ApiDataLoader("2023-12-01", "2023-12-31")
#api_loader.stream_data()
