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
        total_count = df['campaignname'].count()
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
        st.dataframe(df)
        groupdatadf(df)

    else:
        df = load_cached_data('data\output.csv')
        total_count = df['campaignname'].count()
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
        st.dataframe(df)
        groupdatadf(df)

def groupdatadf(df):
    #col1,col2,col3 = st.columns((3))
    # with col1:
    #     st.subheader("Group By Campaign Name")
    #     grouped_data = df.groupby('campaignname').size().reset_index(name='count')
    #     st.dataframe(grouped_data)
    # with col2:
    #     st.subheader("Group By User")
    #     grouped_data = df.groupby(['useremailaddress']).size().reset_index(name='count')
    #     st.dataframe(grouped_data)
    #with col3:
    #st.subheader("Group By EventType")
    grouped_data = df.groupby(['eventtype','campaignname','useremailaddress']).agg({'eventtimestamp':['max']}).reset_index()
    pivoted_df = grouped_data.pivot(index=['campaignname', 'useremailaddress'], columns='eventtype', values=('eventtimestamp', 'max')).reset_index()
    st.write("### Pivoted Data")
    st.dataframe(pivoted_df)

    # Filter the DataFrame for non-None values in 'Email Click'
    df_filtered = pivoted_df[pivoted_df['Email Click'].notna()]
    
    # Group by campaignname and count the occurrences of 'Email Click'
    email_click_counts = df_filtered.groupby('campaignname')['Email Click'].count().reset_index()
    email_click_counts.columns = ['campaignname', 'click_count']
    
    # Plot the bar chart
    plt.figure(figsize=(10, 6))
    plt.bar(email_click_counts['campaignname'], email_click_counts['click_count'], color='skyblue')
    plt.xlabel('Campaign Name')
    plt.ylabel('Count of Email Clicks')
    plt.title('Count of User Email Clicks by Campaign')
    plt.xticks(rotation=90)
    bars = plt.bar(email_click_counts['campaignname'], email_click_counts['click_count'], color='skyblue')
        

    for bar in bars:
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2, yval + 0.1, int(yval), ha='center', va='bottom')
        
    
    # Display the plot in Streamlit
    col1,col2 = st.columns((2))
    with col1:
        st.pyplot(plt)

#@st.cache_data
def load_cached_data(file_path):
    try:
        print(file_path)
        df= pd.read_csv(file_path)
        selected_columns = ['useremailaddress', 'eventtype', 'campaignname', 'userfirstname','userlastname','eventtimestamp']
        return df
        
    except FileNotFoundError:
        raise f"File not found {file_path}" 