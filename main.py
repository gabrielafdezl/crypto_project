import krakenex
from pykrakenapi import KrakenAPI
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
from datetime import date, timedelta

api = krakenex.API()
k = KrakenAPI(api)

#colocamos el layout
st.set_page_config(layout="wide", page_title="Análisis de Criptomonedas frente al USDT",
                   initial_sidebar_state='auto')
st.title("Análisis de Criptomonedas frente al USDT")

# ------------ DATAFRAME CON LOS PARES DE VALORES ------------ #

aux = k.get_tradable_asset_pairs()              #nos devuelve un dataframe con todos los asset pairs
aux = aux[aux.wsname.str.contains('/USDT')]     #restringimos a que sean asset pairs que esten expresados en USDT
par_defecto = 'ETHUSDT'
aux["num_column"] = list(range(len(aux.index))) #agrego una lista numerica
index_num = aux.loc[par_defecto,'num_column']
opciones_pares = aux['wsname']                  #generamos una serie con las opciones que le vamos a detallar al usuario
aux.set_index('wsname',inplace=True)            #le cambiamos al df su index para que sea las opciones que le detallamos al usuario

opcion_elegida = st.selectbox('Seleccione un par de monedas a graficar:', opciones_pares, index = int(index_num)) #index es el par por defecto

#Con la opción  que el usuario eligió nos traemos el código en formato altname
par_info = aux['altname'].loc[opcion_elegida]

#Creamos una variable para que nos calcule la fecha desde, definiendola como un año antes de la fecha.
today = date.today()
DateSince = today - timedelta(days = 365)
DateSince_UTS = (time.mktime(DateSince.timetuple()))

ohlc, last = k.get_ohlc_data(pair=par_info, interval=1440, since=DateSince_UTS, ascending=True)
df = ohlc

#Calculamos la media móvil
ohlc['20_SMA'] = ohlc['close'].rolling(20).mean()

#calculamos RSI
from ta.momentum import RSIIndicator
classrsi = RSIIndicator(df['close'])
rsi = classrsi.rsi()

# ------------ GRAFICAMOS ------------ #

# Creamos figura con eje y secundario
fig = make_subplots(specs=[[{"secondary_y": True}]])

# Agregamos los gráficos de interés
fig.add_trace(go.Candlestick(   x = df.index,
                                open = df['open'],
                                high = df['high'],
                                low = df['low'],
                                close = df['close'],
                                name=opcion_elegida,
                                legendgroup=opcion_elegida,
                                increasing_line_color= 'rgb(10, 120, 24)', #green
                                decreasing_line_color= 'rgb(205, 12, 24)'), #red
                                secondary_y=False,)

fig.add_trace(go.Scatter(   x=df.index,
                            y=df['20_SMA'],
                            mode='lines',
                            name="20 SMA",
                            legendgroup='20 SMA',
                            line=dict(color='black', width=2)),
                            secondary_y=False,)

fig.add_trace(  go.Scatter( x=df.index,
                            y=rsi,
                            mode='lines',
                            name='RSI',
                            legendgroup='RSI',
                            line=dict(color='purple', width=2)    ),
                            secondary_y=True,)

fig.update_layout(xaxis_rangeslider_visible=False)

st.plotly_chart(fig, use_container_width=True, height=600)
st.write("[Fuente de datos](https://www.kraken.com/es-es/prices?quote=eur)")

with st.sidebar:
    st.subheader('Acerca de')
    st.markdown ('Si necesita alguna aclaración o responder cualquier pregunta acerca de los datos mostrados, favor contactarnos en figlesiasbo@alumni.unav.es / gfernandezl.1@alumni.unav.es ')
    st.sidebar.image('https://www.unav.edu/documents/10162/30622995/Marca+Universidad+de+Navarra_200__rojo.png/66f537d6-2397-84d5-6e69-0b00f0543d00?t=1635332700414',width=200)
