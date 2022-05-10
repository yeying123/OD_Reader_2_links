
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
uploaded_files = st.sidebar.file_uploader('Upload a CSV file', accept_multiple_files=True, type=['csv'])

# Ask to specify delimiter
st.sidebar.subheader('Step 2: Specify csv file delimiter')
delimit=st.sidebar.text_input('Specify the Delimiter used in the csv file:', ';')

# Input field to ask for Remix link to extract IDs
st.sidebar.subheader('Step 3.1: Remix OD Layer - Origin')
title1 = st.sidebar.text_input('Remix Link (O):', 'Copy URL')

st.sidebar.subheader('Step 3.2: Remix OD Layer - Destination')
title2 = st.sidebar.text_input('Remix Link (D):', 'Copy URL')

if uploaded_files == []:
     st.write('no csv found')
for i in uploaded_files:
     df=pd.read_csv(i,delimiter=delimit)

# Read IDs in the link
if title1 == 'Copy URL' or len(title1)==0:
          st.write('OD-Origin URL needed')
elif title1.find("od=destination")>0:
     st.write('Step 3.1 OD-Origin URL needed' )
else:
     from_='origin_area_id'
     to_='destination_area_id'
     ID_start=title1.find("od=origin")+10
     ID=title1[ID_start:]

if title2=='Copy URL' or len(title2)==0:
     st.write('OD-Destination URL needed')
elif title2.find("od=origin")>0:
          st.write('Step 3.2 OD-Distination URL needed ' )
else:
     from_2='destination_area_id'
     to_2='origin_area_id'
     ID_start2=title2.find("od=destination")+15
     ID2=title2[ID_start2:]
     
if uploaded_files != [] and ID!=0 and ID2!=0:
     ######--------------------------------- Section 1: Matched Pair --------------------------------######
     st.header('Matched Pair')

     # create empty dataframe (table)
     table=pd.DataFrame()
     table2=pd.DataFrame()

     ID_list=ID.split(",")
     if len(df.columns)==1:
          st.write('Make sure you have the right delimiter in Step 2')
     for t in ID_list:
          if int(t) in df[from_].values:
               number=int(t)
               df1=df.loc[df[from_]==number]
               table=table.append(df1)

     ID_list2=ID2.split(",")
     for t in ID_list2:
          if int(t) in df[from_2].values:
               number=int(t)
               df_2=df.loc[df[from_2]==number]
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
     st.write('The origin ID(s) extracted from the Remix URL: ',ID)

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
               if int(t) in table[from_].values:
                    number=int(t)
                    #st.write(t)
                    df_new=table.loc[table[from_]==number]
                    total=df_new['count'].sum()
                    st.write("Total travel from ", from_, " ", number , "is: ", total)
                    summary+=total
               else:
                    number=int(t)
                    st.write("Total travel from ", from_, " ", number, "is: ", 'No matching record')
          st.write("Sum: ",summary)

     st.markdown("""---""")

     ######--------------------------------- Section 3:Destination ---------------------------------######

     st.header('Destination ID(s)')
     st.write('The destination ID(s) extracted from the 2nd Remix URL: ',ID2)
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
               if int(t) in table2[from_2].values:
                    number=int(t)
                    #st.write(t)
                    df_2=table2.loc[table2[from_2]==number]
                    total2=df_2['count'].sum()
                    st.write("Total travel from ", from_2, " ", number , "is: ", total2)
                    summary+=total2
               else:
                    number=int(t)
                    st.write("Total travel from ", from_2, " ", number, "is: ", 'No matching record')
          st.write("Sum: ",summary)

