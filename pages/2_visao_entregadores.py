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

def df_ratings(df):
    return (df[['Delivery_person_ID', 'Delivery_person_Ratings']]
            .groupby(['Delivery_person_ID'])
            .mean()
            .reset_index()
            .sort_values('Delivery_person_Ratings', ascending=False))

def df_traffic_ratings(df):
    result = (df[['Road_traffic_density', 'Delivery_person_Ratings']]
              .groupby(['Road_traffic_density'])
              .agg(['mean', 'std'])
              .reset_index())
    result.columns = ['Road_traffic_density', 'rating mean', 'rating std']
    return result

def df_weather_ratings(df):
    result = (df1[['Weatherconditions', 'Delivery_person_Ratings']]
              .groupby(['Weatherconditions'])
              .agg(['mean', 'std'])
              .reset_index())
    result.columns = ['Weatherconditions', 'rating mean', 'rating std']
    return result

def fastest_delivery(df):
    return (df[['City', 'Delivery_person_ID', 'Time_taken(min)']]
            .groupby(['City', 'Delivery_person_ID'])
            .max()
            .reset_index()
            .groupby('City')
            .apply(lambda x: x.nsmallest(10, 'Time_taken(min)'))
            .reset_index(drop=True)
            .sort_values(by=['City', 'Time_taken(min)']))

def slower_delivery(df): 
    return (df[['City', 'Delivery_person_ID', 'Time_taken(min)']]
            .groupby(['City', 'Delivery_person_ID'])
            .min()
            .reset_index()
            .groupby('City')
            .apply(lambda x: x.nlargest(10, 'Time_taken(min)'))
            .reset_index(drop=True)
            .sort_values(by=['City', 'Time_taken(min)'], ascending=False))

# ==================================================
# Layout no Sreamlit
# ==================================================

st.set_page_config(
    page_title = 'Visão Entregadores',
    page_icon = '🏍️',
    layout="wide"
)

st.header('Marketplace - Visão Cliente', divider='rainbow')

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

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

with tab1:
    with st.container():
        st.title('Overall Metrics')
        col1, col2, col3, col4 = st.columns(4, gap='large')
        with col1:
            col1.metric('Maior idade', df1.Delivery_person_Age.max())
        with col2:
            col2.metric('Menor idade', df1.Delivery_person_Age.min())
        with col3:
            col3.metric('Melhor condição de veículos', df1.Vehicle_condition.max())
        with col4:
            col4.metric('Pior condição de veículos', df1.Vehicle_condition.min())

    with st.container():
        st.markdown("""___""")
        st.title('Avaliações')
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('#### Avaliação média por entregador')
            st.dataframe(df_ratings(df1))
        with col2:
            st.markdown('#### Avaliação média por trânsito')            
            st.dataframe(df_traffic_ratings(df1))

            st.markdown('#### Avaliação média por condições climáticas')
            st.dataframe(df_weather_ratings(df1))

    with st.container():
        st.markdown("""___""")    
        st.title('Velocidade de entrega')
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('#### Top empregadores mais rápidos')
            st.dataframe(fastest_delivery(df1))
        with col2:
            st.markdown('#### Top empregadores mais lentos')
            st.dataframe(slower_delivery(df1))