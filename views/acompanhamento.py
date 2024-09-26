import streamlit as st
import altair as alt
import pandas as pd
import plotly.express as px
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

df_sem_cirurgia = df.loc[df["Account Name"] != "CA1 - ANUNCIANTE - MAIS CIRURGIA"]
df_cirurgia = df.loc[df["Account Name"] == "CA1 - ANUNCIANTE - MAIS CIRURGIA"]

titulo_1,titulo_2 = st.columns([3,1])

with titulo_1:
  st.markdown("# Acompanhamento de Mídia")

with titulo_2:
  month_filter = st.selectbox(label = "Selecione o Mês",
                                   placeholder= 'Selecione o mês',
                                   options=df_sem_cirurgia['month'].unique())

st.markdown("## Facebook")

if (month_filter):
  df_sem_cirurgia = df_sem_cirurgia.loc[df_sem_cirurgia['month'] == month_filter]

total_groupby = df_sem_cirurgia.groupby(["Categoria"]).agg({"Results":"sum","Amount Spent":"sum"})
total_groupby = total_groupby.reset_index()
total_groupby["CPL"] = total_groupby["Amount Spent"]/total_groupby["Results"]

total_row = pd.DataFrame(total_groupby[['Results', 'Amount Spent']].sum()).transpose()
total_row["CPL"] = total_row['Amount Spent']/total_row['Results']

metrics_1,metrics_2,metrics_3 = st.columns(3)

with metrics_1:
  st.metric("Resultados Total",f"{total_row["Results"] :.0f}")
with metrics_2:
  st.metric("Custo Total",f"R$ {total_row["Amount Spent"] :.2f}")
with metrics_3:
  st.metric("CPL Total",f"R$ {total_row["CPL"] :.2f}")

st.dataframe(
    total_groupby,
    use_container_width=True,
    column_config={
        "Amount Spent": st.column_config.NumberColumn(
            "Custo",
            format="R$ %.2f",
            width="small"
        ),
        "CPL": st.column_config.NumberColumn(
            "CPL",
            format="R$ %.2f",
            width="small"
        ),
        "Categoria": st.column_config.Column(
            "Categoria",
            width="large"
        ),
        "Results": st.column_config.NumberColumn(
            "Resultados",
            width="small"
        ),
    },
    hide_index = True
  )

store_filter = st.selectbox(label = "Selecione a Unidade",
                                   placeholder= 'Selecione a Unidade',
                                   options=df_sem_cirurgia['Unidade'].unique())

if (store_filter):
  df_filtered = df_sem_cirurgia.loc[df_sem_cirurgia['Unidade'] == store_filter]

categoria_groupby = df_filtered.groupby(["Categoria"]).agg({"Results":"sum","Amount Spent":"sum"})

categoria_groupby["CPL"] = categoria_groupby["Amount Spent"]/categoria_groupby["Results"]

st.dataframe(
    categoria_groupby,
    use_container_width=True,
    column_config={
        "Amount Spent": st.column_config.NumberColumn(
            "Custo",
            format="R$ %.2f",
            width="small"
        ),
        "CPL": st.column_config.NumberColumn(
            "CPL",
            format="R$ %.2f",
            width="small"
        ),
        "Categoria": st.column_config.Column(
            "Categoria",
            width="large"
        ),
        "Results": st.column_config.NumberColumn(
            "Resultados",
            width="small"
        ),
    }
  )
