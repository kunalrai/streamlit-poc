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
    
    data = load_cached_data('data\output.csv')
    # Calculate total count
    total_count = data['campaignname'].count()

    st.markdown(f"""
    <div style="display: flex; width: 100%; margin-bottom: 20px;">
    <div style="padding: 10px; border-radius: 5px; background-color: #f0f0f0; border: 1px solid #ccc; text-align: center; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); width: 50%; margin-right: 10px;">
        <h3>Total Campaigns</h3>
        <p style="font-size: 24px; font-weight: bold;">{total_count}</p>
    </div>
    <div style="padding: 10px; border-radius: 5px; background-color: #f0f0f0; border: 1px solid #ccc; text-align: center; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); width: 50%;">
        <h3></h3>
        <p style="font-size: 24px; font-weight: bold;"></p>
    </div>
</div>

    """, unsafe_allow_html=True)
    
    
    filters = display_filters(data)
    data_processor = DataProcessor(data)
    filtered_data = data_processor.apply_filters(filters)
    if not filtered_data.empty:
        st.dataframe(filtered_data)
    else:
        st.dataframe(data)
    
    grouped_data = data.groupby('campaignname').size().reset_index(name='count')

# Display the grouped and counted data
    st.subheader("Group By Campaign Name")

    st.dataframe(grouped_data)

if __name__ == '__main__':
    main()
