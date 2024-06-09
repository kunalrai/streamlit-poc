import streamlit as st
import pandas as pd
import requests,os
import json
from datetime import datetime
from io import StringIO
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv('API_KEY', 'default_key_if_none')

headers = {
            'Accept': 'application/json',
            'x-apikey-token': api_key,
            'Content-Type': 'application/json'
        }

def fetch_data(api_url, start_date, end_date, page_number=1):
    url = f"{api_url}&page[number]={page_number}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error: {response.status_code}")
        return None

def get_all_data(api_url, start_date, end_date):
    page_number = 1
    all_data = []

    while True:
        data = fetch_data(api_url, start_date, end_date, page_number)
        if data and 'data' in data:
            all_data.extend(data['data'])
            if 'next' not in data['links']:
                break
            page_number += 1
            break;
        else:
            break
    return all_data

#UI
st.set_page_config(page_icon = ":bar_chart:",layout="wide")

st.sidebar.title("Select Dates")

start_date = st.sidebar.date_input("Start Date", datetime(2024, 1, 1))
end_date = st.sidebar.date_input("End Date", datetime.now())

if start_date > end_date:
    st.sidebar.error("Error: End date must fall after start date.")

st.title(":bar_chart: Phishing Event Data")

col1, col2 = st.columns(2)

with col1:
    fetch_data_button = st.button("Fetch Data")

with col2:
    selected_campaign = None
    download_button = None

api_url = f'https://results.us.securityeducation.com/api/reporting/v0.3.0/phishing_extended?filter[_eventtimestamp_start]={start_date}&filter[_eventtimestamp_end]={end_date}'

if fetch_data_button:
    with st.spinner("Fetching data..."):
        data = get_all_data(api_url, start_date, end_date)
        if data:
            df = pd.json_normalize(data)
            st.write(f"Total Records: {len(df)}")

            st.subheader("Data Table")
            st.dataframe(df, height=400)

            st.subheader("Group by Campaign Name")
            campaign_group = df.groupby('attributes.campaignname').size().reset_index(name='counts')
            st.dataframe(campaign_group)

            campaigns = df['attributes.campaignname'].unique()
            selected_campaign = st.sidebar.selectbox("Select Campaign to Download Data", campaigns)

            if selected_campaign:
                with col2:
                    campaign_data = df[df['attributes.campaignname'] == selected_campaign]
                    csv = campaign_data.to_csv(index=False)
                    download_button = st.download_button("Download CSV", csv, file_name=f"{selected_campaign}.csv", mime='text/csv')
