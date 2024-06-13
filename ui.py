import streamlit as st
from datetime import datetime
import pandas as pd
import os,requests


from dotenv import load_dotenv

from data_loader import ApiDataLoader
load_dotenv()



def display_filters(api_df):
    filters = []
    if 'campaignname' in api_df.columns:
        campaignname = st.multiselect('Select Campaign', options=api_df['campaignname'].unique().tolist())
        filters.append(lambda df: df[df['campaignname'].isin(campaignname)])
    else:
        filters = ['']
    
    return filters



def display_data(filtered_data):
    
    # page_size = 1000
    # total_rows = len(filtered_data)
    # total_pages = total_rows // page_size + (1 if total_rows % page_size > 0 else 0)

    # page_number = st.number_input('Page Number', min_value=1, max_value=total_pages, value=1)
    # start_row = (page_number - 1) * page_size
    # end_row = start_row + page_size

    # Display the current page of data
    st.subheader(f'Campaign')
    #st.write(filtered_data.iloc[start_row:end_row])
    st.write(filtered_data)


def download_data():
    st.title("Phishing Event Data Loader")
    col1,col2 = st.columns((2))
    with col1:
        start_date = st.date_input("Start Date", value=pd.to_datetime("2024-01-01"))
    with col2:
         end_date = st.date_input("End Date", value=pd.to_datetime("today"), min_value=start_date)
    
    if st.button("Download Data"):
        api_loader = ApiDataLoader(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        with st.spinner("Loading data..."):
            data = api_loader.stream_data()
        
        if data:
            st.success("Data loaded successfully!")
            st.write("Sample Data:", data[:5])  # Display first 5 rows as sample
            csv = pd.DataFrame(data).to_csv(index=False)
            st.download_button(
                label="Download data as CSV",
                data=csv,
                file_name='phishing_data.csv',
                mime='text/csv',
            )

@st.cache_data
def load_cached_data(file_path):
    try:
        return pd.read_csv(file_path)
    except FileNotFoundError:
        return pd.DataFrame() 