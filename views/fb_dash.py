import streamlit as st
import altair as alt
import pandas as pd
import plotly.express as px
from numerize.numerize import numerize
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Pró-Corpo - Relatório Facebook", page_icon="💎",layout="wide")


@st.cache_data

def load_dataframe():
  conn = st.connection("gsheets", type=GSheetsConnection)
  df = conn.read(worksheet="FB - Compilado")

  df.drop_duplicates(subset=["Day","Ad ID"],inplace=True)

  conn.update(data=df,worksheet="FB - Compilado")
  
  return df

df = load_dataframe('https://docs.google.com/spreadsheets/d/1A5sFf-hvJRs8FPo4I0UnZwbQ0q1afkT6qYboj3OC8tI/edit?usp=sharing')

# Show the page title and description.


st.markdown(
    '<style>.centered-title { text-align: center; }</style><h1 class="centered-title">Dash Mídia Facebook</h1>',
    unsafe_allow_html=True
)


with st.sidebar:
    account_filter = st.multiselect(label= 'Selecione a Conta',
                                options=df['Account Name'].unique(),
                                default=df['Account Name'].unique())

df_filtered = df.loc[df['Account Name'].isin(account_filter)]

total_resultados = float(df_filtered['Results'].sum())
total_custo = float(df_filtered['Amount Spent'].sum())

total1,total2= st.columns(2,gap='large')

with total1:
    st.metric(label = 'Custo Total', value= numerize(total_custo))

with total2:
    st.metric(label='Resultados Total', value=numerize(total_resultados))

df_reshaped = df_filtered.pivot_table(
    index="Day", columns="Campaign Name", values="Amount Spent", aggfunc="sum", fill_value=0
)
df_reshaped = df_reshaped.sort_values(by="Day", ascending=False)

st.markdown(
    '<style>.left-title { text-align: center; }</style><h1 class="left-title">Gráficos</h1>',
    unsafe_allow_html=True
)

campanha_filter = st.multiselect(label= 'Selecione os campanha',
                                options=df_reshaped.columns,
                                default=df_reshaped.columns)

graph_1,graph_2 = st.columns(2,gap='small')

with graph_1:
  st.bar_chart(data=df_reshaped,y=campanha_filter)

with graph_2:
  st.line_chart(data=df_reshaped,y=campanha_filter)


st.markdown(
    '<style>.left-title { text-align: center; }</style><h1 class="left-title">Tabelas</h1>',
    unsafe_allow_html=True
)

table = st.columns(1)

with table[0]:
  st.dataframe(
    df_reshaped,
    use_container_width=True,
  )
