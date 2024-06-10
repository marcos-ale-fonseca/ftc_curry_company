from etl_pipeline import extract
from etl_pipeline import transform

import re
import pandas as pd
import numpy as np
import plotly.express as px
import folium
import streamlit as st

from datetime import datetime
from haversine import haversine
from PIL import Image
from streamlit_folium import folium_static

# Extrair os dados
df_raw = extract.csv('data/train.csv')

# Transformar os dados
df1 = transform.dataframe(df_raw)

# ==================================================
# Methods
# ==================================================

def order_metrics(df):
    df_aux = df[['ID', 'Order_Date']].groupby(['Order_Date']).count().reset_index()
    return px.bar(df_aux, x='Order_Date', y='ID')
    
def traffic_order_share(df):
    df_aux = df[['ID', 'Road_traffic_density']].groupby(['Road_traffic_density']).count().reset_index()
    df_aux['Entregas_perc'] = df_aux['ID'] / df_aux['ID'].sum()
    return px.pie(df_aux, names='Road_traffic_density', values='Entregas_perc')

def trafic_order_city(df):
    df_aux = df[['ID', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).count().reset_index()
    return px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID', color='City')

def order_by_week(df):
    df_aux = df[['ID', 'week_of_year']].groupby(['week_of_year']).count().reset_index()
    return px.line(df_aux, x='week_of_year', y='ID')

def order_share_by_week(df):
    df_week = df[[
        'ID',
        'week_of_year'
    ]].groupby([
        'week_of_year'
        ]).count().reset_index()

    df_person = df[[
        'Delivery_person_ID',
        'week_of_year'
    ]].groupby([
        'week_of_year'
        ]).nunique().reset_index()

    df_inner = pd.merge(df_week, df_person, how='inner')
    df_inner['order_by_deliver'] = df_inner.ID / df_inner.Delivery_person_ID

    return px.line(df_inner, x='week_of_year', y='order_by_deliver')

def contry_maps(df):
    df_aux = df.copy()
    df_aux = df_aux[[
        'City',
        'Road_traffic_density',
        'Delivery_location_latitude',
        'Delivery_location_longitude',
    ]].groupby([
        'City', 
        'Road_traffic_density'
    ]).median().reset_index()

    latitude = df_aux.loc[0, 'Delivery_location_latitude']
    longitude = df_aux.loc[0, 'Delivery_location_longitude']

    map = folium.Map(
        location=[latitude, longitude],
        zoom_start=10)

    for index, row in df_aux.iterrows():
        folium.Marker(
            location=[row['Delivery_location_latitude'], row['Delivery_location_longitude']],
            popup=row[['City', 'Road_traffic_density']]
            ).add_to(map)
    return map

# ==================================================
# Layout no Sreamlit
# ==================================================

st.set_page_config(
    page_title = 'Visão Empresa',
    page_icon = '📈',
    layout="wide"
)

st.header('Marketplace - Visão Empresa', divider='rainbow')

image_path = 'images/logo.png'
image = Image.open(image_path)
st.sidebar.image(image, width=250)
st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.sidebar.markdown('## Selecione uma data limite:')


min_date = datetime(2022, 2, 11)
max_date = datetime(2022, 4, 6)

date_slider = st.sidebar.slider(
    'Selecione uma data:',
    value=max_date,
    min_value=min_date,
    max_value=max_date,
    format='DD-MM-YYYY'
)
st.sidebar.write("Data selecionada:", date_slider, divider='rainbow')

st.sidebar.markdown("""---""")
traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito?',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam']
)

st.sidebar.markdown("""---""")
st.sidebar.markdown('## Powerd by Comunidade DS')

# Filtro de data
filter_date = df1.Order_Date <= date_slider
df1 = df1.loc[filter_date, :]

# Filtro de trânsito
filter_trafic = df1.Road_traffic_density.isin(traffic_options)
df1 = df1.loc[filter_trafic, :]

# ==================================================
# Layout no Sreamlit
# ==================================================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    with st.container():
        st.markdown('# Orders by day')
        fig = order_metrics(df1)
        st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('# Traffic Order Share')
        fid_pie = traffic_order_share(df1)
        st.plotly_chart(fid_pie, use_container_width=True)

    with col2:
        st.markdown('# Trafic ORder City.')
        fig = trafic_order_city(df1)
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    with st.container():
        st.markdown('# Order by Week')
        fig = order_by_week(df1)
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        st.markdown('# Order Share by Week')
        fig = order_share_by_week(df1)
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.markdown('# City by Traffic Type')
    map = contry_maps(df1)
    folium_static(map, width=1024, height=600)
    

