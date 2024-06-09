import streamlit as st
from data_loader import DataLoader
from data_processor import DataProcessor
from ui import display_api_data, display_data, display_filters,display_api_filters
import plotly.express as px
import pandas as pd
import os
import warnings
import requests
from datetime import datetime
warnings.filterwarnings('ignore')




def main():
    st.set_page_config(page_title="Data Viewer Application",page_icon = ":bar_chart:",layout="wide")
    st.title(":bar_chart: Data Viewer Application")
    tab1, tab2 = st.tabs(['Local Data', 'Phishing Data'])
    st.markdown("""
    <style>
    .block-container {
        padding-top: 2rem; 
    }
    </style>
    """,
    unsafe_allow_html=True
    )
    with tab1:
        # Load data
        data_loader = DataLoader('data.json')
        data = data_loader.load_data()

        # Display filters
        filters = display_filters(data)
        
        # Process data
        data_processor = DataProcessor(data)
        filtered_data = data_processor.apply_filters(filters)

        # Display data
        display_data(data)

    with tab2:
        #filters = display_api_filters()
        display_api_data()

if __name__ == '__main__':
    main()
