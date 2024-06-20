import streamlit as st
from data_loader import DataLoader
from data_processor import DataProcessor
from ui import   display_filters,download_data,load_cached_data
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
    
    st.markdown("""
    <style>
    .block-container {
        padding-top: 2rem; 
    }
    </style>
    """,
    unsafe_allow_html=True
    )
    data = pd.DataFrame()
    download_data()

    file_path = r"data\output.csv"
    if os.path.exists(file_path):
        data = load_cached_data(r'data\output.csv')
        # Display the grouped and counted data
        
    
    
    

    # data_processor = DataProcessor(data)
    # filtered_data = data_processor.apply_filters(filters)
    # if not filtered_data.empty:
    #     st.dataframe(filtered_data)
    #     grouped_data = filtered_data.groupby('campaignname').size().reset_index(name='count')

    # else:
    #     st.dataframe(data)
    #    

    
    



if __name__ == '__main__':
    main()
