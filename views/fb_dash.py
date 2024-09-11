import streamlit as st
import altair as alt
import pandas as pd
import plotly.express as px
from numerize.numerize import numerize
from streamlit_gsheets import GSheetsConnection
import datetime

st.set_page_config(page_title="Pró-Corpo - Relatório Facebook", page_icon="💎",layout="wide")

@st.cache_data
def load_main_dataframe(worksheet):

  conn = st.connection("gsheets", type=GSheetsConnection)
  df = conn.read(worksheet=worksheet)

  df['Day'] = pd.to_datetime(df['Day'])

  df["Account Name"] = df["Account Name"].astype(str)
  df["Campaign Name"] = df["Campaign Name"].astype(str)
  df["Ad Set Name"] = df["Ad Set Name"].astype(str)
  df["Ad Name"] = df["Ad Name"].astype(str)
  df["Ad ID"] = df["Ad ID"].astype(str)

  df.drop_duplicates(subset=["Day","Ad ID"],inplace=True)

  conn.update(data=df,worksheet="FB - Compilado")

  return df

@st.cache_data
def load_aux_dataframe(worksheet,duplicates_subset):

  conn = st.connection("gsheets", type=GSheetsConnection)
  df = conn.read(worksheet=worksheet)

  return df

df = load_main_dataframe("FB - Compilado")

df_categorias = load_aux_dataframe("Auxiliar - Categorias","Anuncio")
df_unidades = load_aux_dataframe("Auxiliar - Unidades","Campaign Name")
df_whatsapp = load_aux_dataframe("Auxiliar - Whatsapp","Ad Name")

df = pd.merge(df,df_categorias,how="left",left_on="Ad Name",right_on="Anuncio")
df = df.drop(columns=["Anuncio"])
df["Results"] = df["Results"].fillna(0)
df["Categoria"] = df["Categoria"].fillna("Sem Categoria")

st.write(df_unidades.columns)

# Show the page title and description.


st.markdown(
    '<style>.centered-title { text-align: center; }</style><h1 class="centered-title">Dash Mídia Facebook</h1>',
    unsafe_allow_html=True
)

st.title("Filtros")

filtro_1,filtro_2,filtro_3= st.columns(3,gap='small')

with filtro_1:
  account_filter = st.multiselect(label= 'Selecione a Conta',
                                  options=df['Account Name'].unique(),
                                  default=df['Account Name'].unique())

with filtro_2:
  today = datetime.datetime.now()
  first_day_month = today.replace(day=1)

  date_picker = st.date_input(
      label="Selecionar data",
      value = (first_day_month, today),
      format="DD/MM/YYYY",
  )

  date_picker = pd.to_datetime(date_picker)

df_filtered = df.loc[df['Account Name'].isin(account_filter)]
df_filtered = df_filtered.loc[df_filtered['Day'].between(date_picker[0],date_picker[1])]

total_resultados = float(df_filtered['Results'].sum())
total_custo = float(df_filtered['Amount Spent'].sum())

try:
  custo_por_resultado = total_custo/total_resultados
except:
  custo_por_resultado = 0

metric_1,metric_2,metric_3= st.columns(3,gap='large')

with metric_1:
    st.metric(label = 'Custo Total', value= f"R${numerize(total_custo)}")

with metric_2:
    st.metric(label='Resultados Total', value=numerize(total_resultados))

with metric_3:
    st.metric(label='Custo por Resultado', value= f"R${numerize(custo_por_resultado)}")

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
