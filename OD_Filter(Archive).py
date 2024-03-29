
from collections import namedtuple
import math
import pandas as pd
import streamlit as st
import base64
import streamlit.components.v1 as components
import numpy as np

st.set_page_config(
     page_title="OD Selection from Remix",
     layout="wide",
     initial_sidebar_state="expanded")
st.sidebar.title('OD Selection from Remix')


# Ask to upload file
st.sidebar.subheader('Step 1: Upload the OD data file (with all OD pairs)')
st.sidebar.caption('Make sure the csv file with these columns (in lowercase): "origin_area_id", "destination_area_id", and "count" ')
st.sidebar.caption('Note: one file only')
uploaded_file = st.sidebar.file_uploader('Upload a CSV file', accept_multiple_files=False, type=['csv'])

# Ask to specify delimiter
st.sidebar.subheader('Step 2: Specify csv file delimiter')
delimit=st.sidebar.text_input('Specify the Delimiter used in the csv file:', ',')

# Input field to ask for Remix link to extract IDs
st.sidebar.subheader('Step 3.1: Remix OD Layer - Destination')
title2 = st.sidebar.text_input('Copy Area IDs from Remix:',placeholder='destination=')

st.sidebar.subheader('Step 3.2: Remix OD Layer - Origin')
title1 = st.sidebar.text_input('Copy Area IDs from Remix:',placeholder='origin=')

if uploaded_file is None:
     st.write('no csv found')
else:
     df=pd.read_csv(uploaded_file,delimiter=delimit)
     df['origin_area_id']=df['origin_area_id'].astype(str) # account for the situation that each area_id could be either int or str
     df['destination_area_id']=df['destination_area_id'].astype(str) # account for the situation that each area_id could be either int or str

# Read IDs in the link
if len(title2)==0:
     st.write('OD-Destination IDs needed')
     ID2=0
elif ("destination=" in title2) is False:
     st.write('Step 3.1 OD-Distination IDs needed ' )
     ID2=0     
else:
     from_2='destination_area_id'
     to_2='origin_area_id'
     ID_start2=title2.find("destination=")+12
     ID2=title2[ID_start2:]

if len(title1)==0:
     st.write('OD-Origin IDs needed')
     ID=0
elif ("origin=" in title1) is False:
     st.write('Step 3.2 OD-Origin IDs needed' )
     ID=0
else:
     from_='origin_area_id'
     to_='destination_area_id'
     ID_start=title1.find("od=origin")+8
     ID=title1[ID_start:]


     
if uploaded_file is not None and ID!=0 and ID2!=0:
     ######--------------------------------- Section 1: Matched Pair --------------------------------######
     st.header('Matched Pair')

     # create empty dataframe (table)
     table=pd.DataFrame()
     table2=pd.DataFrame()

     ID_list=ID.split(",")
     if len(df.columns)==1:
          st.write('Make sure you have the right delimiter in Step 2')
     for t in ID_list:
          if t in df[from_].values:
               df1=df.loc[df[from_]==t]
               table=table.append(df1)

     ID_list2=ID2.split(",")
     for t in ID_list2:
          if t in df[from_2].values:
               df_2=df.loc[df[from_2]==t]
               table2=table2.append(df_2)

     A=list(set(table.origin_area_id) & set(table2.origin_area_id))
     B=list(set(table.destination_area_id) & set(table2.destination_area_id))
     table_match=df[df['origin_area_id'].isin(A) & df['destination_area_id'].isin(B)]
     if len(table_match)==0:
          st.caption('No matched record')
     else:
          st.write(table_match)
          summary1=table_match['count'].sum()
          st.write("Sum: ",summary1)
          def convert_df(df):
          # IMPORTANT: Cache the conversion to prevent computation on every rerun
               return df.to_csv().encode('utf-8')
          csv = convert_df(table_match)

          st.download_button(
               "Press to Download CSV",
               csv,
               "OD_Selection_Matched.csv",
               "text/csv",
               key='download-csv'
               )
     
     #st.write(table2[table2.destination_area_id.isin(table['destination_area_id'])])
     st.markdown("""---""")

     ######--------------------------------- Section 2:Origin ---------------------------------------######
     
     # create empty dataframe (table)

     st.header('Origin ID(s)')
     st.write('The origin ID(s) extracted from Remix: ',ID)

     col1, col2= st.columns((0.8,0.8))
     with col1:
          st.subheader('OD Selection Table')
          st.dataframe(table,450, 600)
          def convert_df(df):
          # IMPORTANT: Cache the conversion to prevent computation on every rerun
               return df.to_csv().encode('utf-8')
          csv = convert_df(table)

          st.download_button(
               "Press to Download CSV",
               csv,
               "OD_Selection_Table_1.csv",
               "text/csv",
               key='download-csv'
               )
     with col2:
          st.subheader('OD Pair Summary')
          summary=0
          for t in ID_list:
               if t in table[from_].values:
                    #st.write(t)
                    df_new=table.loc[table[from_]==t]
                    total=df_new['count'].sum()
                    st.write("Total travel from ", from_, " ", t , "is: ", total)
                    summary+=total
               else:
                    st.write("Total travel from ", from_, " ", t, "is: ", 'No matching record')
          st.write("Sum: ",summary)

     st.markdown("""---""")

     ######--------------------------------- Section 3:Destination ---------------------------------######

     st.header('Destination ID(s)')
     st.write('The destination ID(s) extracted from Remix: ',ID2)
     #st.write(from_2)
     col3, col4= st.columns((0.8, 0.8))
     

     def get_table_download_link(df_2):
               """Generates a link allowing the data in a given panda dataframe to be downloaded
               in:  dataframe
               out: href string
               """
               csv2 = df_2.to_csv(index=False)
               b64 = base64.b64encode(csv2.encode()).decode()  # some strings <-> bytes conversions necessary here
               href = f'<a href="data:file/csv;base64,{b64}">Download table as csv file</a>'
               return href

     with col3:
          st.subheader('OD Selection Table')
          st.dataframe(table2,450, 600)
          def convert_df(df):
          # IMPORTANT: Cache the conversion to prevent computation on every rerun
               return df.to_csv().encode('utf-8')
          csv = convert_df(table2)

          st.download_button(
               "Press to Download CSV",
               csv,
               "OD_Selection_Table_2.csv",
               "text/csv",
               key='download-csv'
               )


     with col4:
          st.subheader('OD Pair Summary')
          summary=0
          for t in ID_list2:
               if t in table2[from_2].values:
                    #st.write(t)
                    df_2=table2.loc[table2[from_2]==t]
                    total2=df_2['count'].sum()
                    st.write("Total travel to ", from_2, " ", t , "is: ", total2)
                    summary+=total2
               else:
                    st.write("Total travel to ", from_2, " ", t, "is: ", 'No matching record')
          st.write("Sum: ",summary)

