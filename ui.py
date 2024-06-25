import streamlit as st
from datetime import datetime
import pandas as pd
import os,requests
from data_processor import DataProcessor
import matplotlib.pyplot as plt



from dotenv import load_dotenv

from data_loader import ApiDataLoader
load_dotenv()



def display_filters(api_df):
    filters = []
    if 'campaignname' in api_df.columns:
        campaignname = st.multiselect('Select Campaign', options=api_df['campaignname'].unique().tolist())
        #useremail = st.multiselect('Select User Email', options=api_df['useremailaddress'].unique().tolist())

        filters.append(lambda df: df[df['campaignname'].isin(campaignname)])
        #filters.append(lambda df: df[df['useremailaddress'].isin(useremail)])


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
    col1,col2,col3 = st.columns((3))
    with col1:
        start_date = st.date_input("Start Date", value=pd.to_datetime("2024-01-01"))
    with col2:
         end_date = st.date_input("End Date", value=pd.to_datetime("today"), min_value=start_date)
    with col3:
        campaignname = st.text_input("Enter Campaign ")

    if st.button("Run"):
        api_loader = ApiDataLoader(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        with st.spinner("Loading data..."):
                api_loader.stream_data()
        
    if not campaignname == '':
        df = load_cached_data('data\output.csv')
        df = df[df['campaignname'].str.contains(campaignname)]
        
        st.dataframe(df)
        groupdatadf(df)

    else:
        df = load_cached_data('data\output.csv')
        st.metric("Total",df.shape[0])
        st.dataframe(df)
        groupdatadf(df)

def groupdatadf(df):
    
    grouped_data = df.groupby(['eventtype','campaignname','useremailaddress']).agg({'eventtimestamp':['max']}).reset_index()
    pivoted_df = grouped_data.pivot(index=['campaignname', 'useremailaddress'], columns='eventtype', values=('eventtimestamp', 'max')).reset_index()
    

    # Filter the DataFrame for non-None values in 'Email Click'
    df_filtered = pivoted_df[pivoted_df['Email Click'].notna()]
    
    # Group by campaignname and count the occurrences of 'Email Click'
    columns_to_count = ['Email Click', 'Email View', 'No Action','Reported','TM Complete','TM Sent']
    email_click_counts = df_filtered.groupby('campaignname')[columns_to_count].count().reset_index()
    
   
        
    total_counts = pivoted_df[columns_to_count].count()
    campaign_name = pivoted_df['campaignname'].iloc[0].split("_")[1]
    
    email_view =  total_counts['Email View']

    phis_sent =  pivoted_df.shape[0]
    phis_open_rate = ( email_view/phis_sent) * 100

    email_click = total_counts['Email Click']
    email_open_click_rate = (email_click/phis_sent)*100

    for col, count in total_counts.items():
        print(f"{col}: {count}")
    
    def format_number(number):
        return '{:,.0f}'.format(number)
    
    st.markdown(
    f"""
    <div style=" justify-content: center; align-items: center; height: 200px;width:100%">
        <div style="background-color: #0074D9; padding: 20px; text-align: center;">
            <h2 style="color: white;">{campaign_name}</h1>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

    col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)
    col1.metric("Phishes Sent",format_number( phis_sent))
    col2.metric("Email Open", format_number(email_view))
    col3.metric("Phish Open Rate",f"{phis_open_rate:.2f}%")
    col4.metric("Email Open Clicked Rate", f"{email_open_click_rate:.2f}%")
    col5.metric("Overall Clicked Rate", "3%")
    col6.metric("Reported [ProofPoint]", "15,270")
    col7.metric("Overall Reported Rate [ProofPoint]", "32%")
    col8.metric("Reported [Other Sources]", "10")

    st.write("### Pivoted Data")
    st.dataframe(pivoted_df)

    st.write("### Group By Count")
    st.dataframe(email_click_counts)

#@st.cache_data
def load_cached_data(file_path):
    try:
        print(file_path)
        df= pd.read_csv(file_path)
        selected_columns = ['useremailaddress', 'eventtype', 'campaignname', 'userfirstname','userlastname','eventtimestamp','campaignstartdate','campaignenddate']
        df = df[selected_columns]
        return df
        
    except FileNotFoundError:
        raise f"File not found {file_path}" 