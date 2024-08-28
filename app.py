import streamlit as st
import altair as alt
import pandas as pd
import plotly.express as px
from numerize.numerize import numerize

# Show the page title and description.
st.set_page_config(page_title="Pró-Corpo - Dash de Mídia", page_icon="💎")

# Load the data from a CSV. We're caching this so it doesn't reload every time the app
# reruns (e.g. if the user interacts with the widgets).
@st.cache_data
def load_data():
    df = pd.read_csv("data/fb_data_clean.csv")
    return df

df = load_data()
st.markdown(
    '<style>.centered-title { text-align: center; }</style><h1 class="centered-title">Dash Mídia Facebook</h1>',
    unsafe_allow_html=True
)

with st.sidebar:
    unidade_filter = st.multiselect(label= 'Selecione a Unidade',
                                options=df['store'].unique(),
                                default=df['store'].unique())

df_filtered = df.query('store == @unidade_filter')

total_resultados = float(df_filtered['Resultados'].sum())
total_custo = float(df_filtered['Valor usado (BRL)'].sum())
total_impressoes = float(df_filtered['Impressões'].sum())
total_alcance= float(df_filtered['Alcance'].sum())

total1,total2,total3,total4 = st.columns(4,gap='large')

with total1:
    st.metric(label = 'Custo Total', value= numerize(total_custo))

with total2:
    st.metric(label='Resultados Total', value=numerize(total_resultados))

with total3:
    st.metric(label= 'Impressões Total',value=numerize(total_impressoes,2))

with total4:
    st.metric(label='Alcance Total',value=numerize(total_alcance))


graph_1,graph_2 = st.columns(2,gap='small')

df_reshaped = df_filtered.pivot_table(
    index="month", columns="category", values="Resultados", aggfunc="sum", fill_value=0
)
df_reshaped = df_reshaped.sort_values(by="month", ascending=False)

st.markdown(
    '<style>.left-title { text-align: center; }</style><h1 class="left-title">Gráficos</h1>',
    unsafe_allow_html=True
)


with graph_1:
  # Display the data as a table using `st.dataframe`.
  st.bar_chart(data=df_reshaped)

st.markdown(
    '<style>.left-title { text-align: center; }</style><h1 class="left-title">Tabelas</h1>',
    unsafe_allow_html=True
)

table = st.columns(1)

with table:
    st.dataframe(
      df_reshaped,
      use_container_width=True,
      column_config={"year": st.column_config.TextColumn("Year")},
  )
