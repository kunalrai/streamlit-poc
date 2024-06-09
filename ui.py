import streamlit as st
from datetime import datetime
import pandas as pd
import os,requests

import plotly.express as px
import plotly.subplots as sp
from dotenv import load_dotenv
load_dotenv()

def display_filters(api_df):
    filters = []

    # # Example filter: Selectbox for a column with categorical data
    # if 'Employee ID' in data.columns:
    #     category = st.sidebar.selectbox('Select Employee ID', options=data['Employee ID'].unique())
    #     filters.append(lambda df: df[df['Employee ID'] == category])

    
        
    return filters

def display_api_filters(api_df):
    filters = []
    if 'attributes.campaignname' in api_df.columns:
        st.sidebar.header('Filters')
        campaignname = st.sidebar.multiselect('Select Campaign', options=api_df['attributes.campaignname'].unique().tolist())
        filters.append(lambda df: df[df['attributes.campaignname'] == campaignname])
        
    return filters

@st.cache_data
def get_data(eventtimestampstart, eventtimestampend,page_number =1):
        api_key = os.getenv('API_KEY', 'default_key_if_none')
        url = 'https://results.us.securityeducation.com/api/reporting/v0.3.0/phishing_extended'
        api_url = f'https://results.us.securityeducation.com/api/reporting/v0.3.0/phishing_extended?filter[_eventtimestamp_start]={eventtimestampstart}&filter[_eventtimestamp_end]={eventtimestampend}'
        paginated_url = f"{url}?filter[_eventtimestamp_start]={eventtimestampstart}&filter[_campaignstartdate_end]={eventtimestampend}&page[number]={page_number}"
        print(paginated_url)
        headers = {
            'Accept': 'application/json',
            'x-apikey-token': api_key,
            'Content-Type': 'application/json'
        }
        response = requests.get(paginated_url, headers=headers)
        return response.json()


        

def display_data(filtered_data):
    
    page_size = 1000
    total_rows = len(filtered_data)
    total_pages = total_rows // page_size + (1 if total_rows % page_size > 0 else 0)

    page_number = st.number_input('Page Number', min_value=1, max_value=total_pages, value=1)
    start_row = (page_number - 1) * page_size
    end_row = start_row + page_size

    # Display the current page of data
    st.subheader(f'Data - Page {page_number}')
    st.write(filtered_data.iloc[start_row:end_row])

# Define the callback function to update the session state
def update_campaignname():
    st.session_state['campaignname'] = st.session_state.campaignname_multiselect
    # Update filtered data
    if st.session_state['campaignname']:
        st.session_state['filtered_data'] = st.session_state['original_data'][st.session_state['original_data']['attributes.campaignname'].isin(st.session_state['campaignname'])]
    else:
        st.session_state['filtered_data'] = st.session_state['original_data']


def apply_filters():
    if st.session_state.get('campaignname'):
        st.session_state['filtered_data'] = st.session_state['original_data'][st.session_state['original_data']['attributes.campaignname'].isin(st.session_state['campaignname'])]
    else:
        st.session_state['filtered_data'] = st.session_state['original_data']

def display_api_data():
    st.sidebar.empty()
    default_start = '2024-01-01'
    default_end = '2024-06-30'
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input('Start Date', datetime.strptime(default_start, '%Y-%m-%d'))
    with col2:
        end_date = st.date_input('End Date', datetime.strptime(default_end, '%Y-%m-%d'))
    page_number = st.number_input('Page Number', min_value=1, value=1)
    
    if st.button('Fetch Data'):
        api_data = get_data(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), page_number)
        if api_data:
            data_list = api_data["data"]
            meta_data = api_data["meta"]
            current_page = meta_data["page_number"]
            page_size = meta_data["page_size"]
            total_events = meta_data["count"]
            api_df = pd.json_normalize(data_list)  # Convert to DataFrame
            st.session_state['original_data'] = api_df
            st.session_state['filtered_data'] = api_df  # Initialize filtered data
            st.text(f'Total:  {api_df.shape[0]}')

    # Check if data is available in session state
    if 'original_data' in st.session_state:
        st.write(st.session_state['original_data'])

        st.subheader("Group by Campaign Name")
        campaign_group = st.session_state['original_data'].groupby('attributes.campaignname').size().reset_index(name='counts')
        st.dataframe(campaign_group)

        if 'attributes.campaignname' in st.session_state['original_data'].columns:
            st.sidebar.header('Filters')

            # Initialize session state variable if not present
            if 'campaignname' not in st.session_state:
                st.session_state['campaignname'] = []

            st.session_state.campaignname_multiselect = st.sidebar.multiselect(
                'Select Campaign',
                options=st.session_state['original_data']['attributes.campaignname'].unique().tolist(),
                default=st.session_state['campaignname'],
                on_change=update_campaignname
            )

            # Display the filtered data
            if st.sidebar.button('Filter Data'):
                apply_filters()

            if 'filtered_data' in st.session_state:
                st.subheader("Filtered Data")
                st.write(st.session_state['filtered_data'])
        else:
            st.write('No filterable data found.')
        