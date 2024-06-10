from etl_pipeline import extract
from etl_pipeline import transform

import re
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import folium
import streamlit as st

from datetime import datetime
from PIL import Image
from streamlit_folium import folium_static

# Extrair os dados
df_raw = extract.csv('data/train.csv')

# Transformar os dados
df1 = transform.dataframe(df_raw)

# ==================================================
# Methods
# ==================================================

def diftribution_distance_avg_by_city(df):
    df_aux = (df[['City', 'Time_taken(min)']]
              .groupby(['City'])
              .agg(['mean', 'std'])
              .reset_index())
    df_aux.columns = ['City', 'Avg_Time', 'Std_Time']
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Control',
                        x=df_aux['City'],
                        y=df_aux['Avg_Time'],
                        error_y=dict(type='data', array=df_aux['Std_Time'])))
    fig.update_layout(barmode='group')
    return fig

def avg_time_by_city_and_traffic(df):
    df_aux = (df1[['City', 'Type_of_order', 'Time_taken(min)']]
              .groupby(['City', 'Type_of_order'])
              .agg(['mean', 'std'])
              .reset_index())
    df_aux.columns = ['City', 'Type_of_order', 'Avg_Time', 'Std_Time']
    return df_aux

def delivery_time_avg_by_city(df):
    cols = [ 'Delivery_location_latitude',
            'Delivery_location_longitude',
            'Restaurant_latitude',
            'Restaurant_longitude']
    avg_distance = df1.loc[:, ['City', 'Distance' ]].groupby('City').mean().reset_index()
    fig = go.Figure(data=[go.Pie(labels=avg_distance['City'], values=avg_distance['Distance'], pull=[0, 0.1, 0])])
    return fig

def avg_time_taken_by_devlivery_type(df):
    df_aux = (df1[['City', 'Road_traffic_density', 'Time_taken(min)']]
              .groupby(['City', 'Road_traffic_density'])
              .agg(['mean','std'])
              .reset_index())
    df_aux.columns = ['City', 'Road_traffic_density', 'Avg_Time', 'Std_Time']
    fig = px.sunburst(df_aux,
                    path=['City', 'Road_traffic_density'],
                    values='Avg_Time',
                    color='Std_Time',
                    color_continuous_scale='RdBu',
                    color_continuous_midpoint=np.average(df_aux['Std_Time']))
    fig.update_traces(textfont=dict(size=[20]))
    return fig

# ==================================================
# Layout no Sreamlit
# ==================================================

st.set_page_config(
    page_title = 'Visão Restaurante',
    page_icon = '🍽️',
    layout="wide"
)

st.header('Marketplace - Visão Restaurantes', divider='rainbow')

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

df_aux = (df1[['Festival', 'Time_taken(min)']]
          .groupby(['Festival'])
          .agg(['mean','std'])
          .reset_index())

df_aux.columns = ['Festival', 'Time_taken mean', 'Time_taken std']
df_festival_yes = df_aux[df_aux.Festival == 'Yes']
df_festival_no = df_aux[df_aux.Festival == 'No']

# ==================================================
# Layout no Sreamlit
# ==================================================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

with tab1:
    with st.container():
        st.title('Overall Metrics')
        col1, col2, col3, col4 = st.columns(4, gap='large')
        with col1:
            col1.metric('Entregadores únicos', df1.Delivery_person_ID.nunique())
        with col2:
            col2.metric("Distância média", "{:.2f}".format(df1.Distance.mean()))
        with col3:
            col3.markdown('**Tempo de Entrega com Festival**')
            c1, c2 = st.columns(2, gap='large')
            with c1:
                c1.metric('Média', "{:.2f}".format(float(df_festival_yes['Time_taken mean'])))
            with c2:
                c2.metric('Desvio padrão', "{:.2f}".format(float(df_festival_yes['Time_taken std'])))
        with col4:
            col4.markdown('**Tempo de Entrega sem Festival**')
            c1, c2 = st.columns(2, gap='large')
            with c1:
                c1.metric('Média', "{:.2f}".format(float(df_festival_no['Time_taken mean'])))
            with c2:
                c2.metric('Desvio padrão', "{:.2f}".format(float(df_festival_no['Time_taken std'])))

    with st.container():
        st.markdown("""___""")
        col1, col2 = st.columns(2, gap='large')
        with col1:
            st.title('Distruição da distância média por cidade')
            st.plotly_chart(diftribution_distance_avg_by_city(df1))
        with col2:
            st.title('Tempo médio por cidade e tipo de tráfego (SunBurst)')
            st.dataframe(avg_time_by_city_and_traffic(df1))

    with st.container():
        st.markdown("""___""")
        col1, col2 = st.columns(2, gap='large')
        with col1:
            st.title('Distribuição do tempo de entrega por cidade')
            st.plotly_chart(delivery_time_avg_by_city(df1))
        with col2:
            st.title('Tempo médio por tipo de entrega')
            st.plotly_chart(avg_time_taken_by_devlivery_type(df1))

        