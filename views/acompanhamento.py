import streamlit as st
import altair as alt
import pandas as pd
import plotly.express as px
from numerize.numerize import numerize
from streamlit_gsheets import GSheetsConnection
import datetime

st.set_page_config(page_title="Pró-Corpo - Acompanhamento", page_icon="💎",layout="wide")

@st.cache_data
def load_main_dataframe(worksheet):

  conn = st.connection("gsheets", type=GSheetsConnection)
  df = conn.read(worksheet=worksheet,dtype={"Ad ID": str})

  df['Day'] = pd.to_datetime(df['Day'])

  df["Ad ID"] = df["Ad ID"].astype(str)

  df.drop_duplicates(subset=["Day","Ad ID"],inplace=True)

  conn.update(data=df,worksheet="FB - Compilado")

  return df

@st.cache_data
def load_aux_dataframe(worksheet,duplicates_subset):

  conn = st.connection("gsheets", type=GSheetsConnection)
  df = conn.read(worksheet=worksheet)
  df = df.drop_duplicates(subset=duplicates_subset)

  return df

df = load_main_dataframe("FB - Compilado")

df_categorias = load_aux_dataframe("Auxiliar - Categorias","Anuncio")
df_unidades = load_aux_dataframe("Auxiliar - Unidades","Campaign Name")
df_whatsapp = load_aux_dataframe("Auxiliar - Whatsapp","Ad Name")

df = pd.merge(df,df_categorias,how="left",left_on="Ad Name",right_on="Anuncio")
df = df.drop(columns=["Anuncio"])
df["Results"] = df["Results"].fillna(0)

df = pd.merge(df,df_unidades,how="left",left_on="Campaign Name",right_on="Campaign Name")
df["Unidade"] = df["Unidade"].fillna("Sem Categoria")
df["Região"] = df["Região"].fillna("Sem Categoria")

whatsapp_map = df_whatsapp.set_index('Ad Name')['Categoria'].to_dict()
df.loc[df['Account Name'] == "Campanhas Whatsapp","Categoria"] = df.loc[df['Account Name'] == "Campanhas Whatsapp","Ad Name"].map(whatsapp_map)

df["Categoria"] = df["Categoria"].fillna("Sem Categoria")
df["month"] = df["Day"].dt.to_period("M")

st.markdown("# Acompanhamento de Mídia")

df_sem_cirurgia = df.loc[df["Account Name"] != "CA1 - ANUNCIANTE - MAIS CIRURGIA"]
df_cirurgia = df.loc[df["Account Name"] == "CA1 - ANUNCIANTE - MAIS CIRURGIA"]

filtro_1,filtro_2= st.columns(2,gap='large')

with filtro_1:
  store_filter = st.selectbox(label = "Selecione a Unidade",
                                   placeholder= 'Selecione a Unidade',
                                   options=df_sem_cirurgia['Unidade'].unique())
with filtro_2:
  month_filter = st.selectbox(label = "Selecione o Mês",
                                   placeholder= 'Selecione o mês',
                                   options=df_sem_cirurgia['month'].unique())

if (month_filter):
  df_filtered = df_sem_cirurgia.loc[df_sem_cirurgia['month'] == month_filter]

if (store_filter):
  df_filtered = df_filtered.loc[df_filtered['Unidade'] == store_filter]

df_filtered.columns

categoria_groupby = df_filtered.groupby(["Categoria"]).agg({"Results":"sum","Results":"sum"})

st.dataframe(
    df_filtered,
    use_container_width=True
  )
