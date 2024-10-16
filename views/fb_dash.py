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
  df = conn.read(worksheet=worksheet,dtype={"Ad ID": str})

  df['Day'] = pd.to_datetime(df['Day'])

  df["Ad ID"] = df["Ad ID"].astype(str)

  df.drop_duplicates(subset=["Day","Ad ID"],inplace=True)

  conn.update(data=df,worksheet=worksheet)

  return df

@st.cache_data
def load_aux_dataframe(worksheet,duplicates_subset):

  conn = st.connection("gsheets", type=GSheetsConnection)
  df = conn.read(worksheet=worksheet)
  df = df.drop_duplicates(subset=duplicates_subset)

  return df

df = load_main_dataframe("Compilado - FB e Gads")

df_categorias = load_aux_dataframe("Auxiliar - Categorias - FB","Anuncio")
df_unidades = load_aux_dataframe("Auxiliar - Unidades - FB","Campaign Name")
df_whatsapp = load_aux_dataframe("Auxiliar - Whatsapp - FB","Ad Name")

df = pd.merge(df,df_categorias,how="left",left_on="Ad Name",right_on="Anuncio")
df = df.drop(columns=["Anuncio"])
df["Results"] = df["Results"].fillna(0)

df = pd.merge(df,df_unidades,how="left",left_on="Campaign Name",right_on="Campaign Name")
df["Unidade"] = df["Unidade"].fillna("Sem Categoria")
df["Região"] = df["Região"].fillna("Sem Categoria")

# Create a mapping dictionary from df1
whatsapp_map = df_whatsapp.set_index('Ad Name')['Categoria'].to_dict()
df.loc[df['Account Name'] == "Campanhas Whatsapp","Categoria"] = df.loc[df['Account Name'] == "Campanhas Whatsapp","Ad Name"].map(whatsapp_map)

df["Categoria"] = df["Categoria"].fillna("Sem Categoria")

st.markdown(
    '<style>.centered-title { text-align: center; }</style><h1 class="centered-title">Dash Mídia Facebook</h1>',
    unsafe_allow_html=True
)

df = df.loc[df["Plataforma"] == "Facebook"]

df_sem_cirurgia = df.loc[df["Account Name"] != "CA1 - ANUNCIANTE - MAIS CIRURGIA"]
df_cirurgia = df.loc[df["Account Name"] == "CA1 - ANUNCIANTE - MAIS CIRURGIA"]

filtro_1,filtro_2,filtro_3= st.columns([2.5,2.5,1],gap='small')

with filtro_1:
  account_filter = st.multiselect(label = "Selecione a Conta",
                                  placeholder= 'Selecione a Conta',
                                  options=df_sem_cirurgia['Account Name'].unique())

  category_filter = st.multiselect(label = "Selecione a Categoria",
                                   placeholder= 'Selecione a Categoria',
                                   options=df_sem_cirurgia['Categoria'].unique())
with filtro_2:
  store_filter = st.multiselect(label = "Selecione a Unidade",
                                   placeholder= 'Selecione a Unidade',
                                   options=df_sem_cirurgia['Unidade'].unique())

  region_filter = st.multiselect(label = "Selecione a Região",
                                   placeholder= 'Selecione a Região',
                                   options=df_sem_cirurgia['Região'].unique())
with filtro_3:
  today = datetime.datetime.now()
  first_day_month = today.replace(day=1)

  date_picker = st.date_input(
      label="Selecionar data",
      value = (first_day_month, today),
      format="DD/MM/YYYY",
  )

  date_picker = pd.to_datetime(date_picker)

df_filtered = df_sem_cirurgia.loc[df_sem_cirurgia['Day'].between(date_picker[0],date_picker[1])]

if (account_filter):
  df_filtered = df_filtered.loc[df_filtered['Account Name'].isin(account_filter)]
if (category_filter):
  df_filtered = df_filtered.loc[df_filtered['Categoria'].isin(category_filter)]
if (store_filter):
  df_filtered = df_filtered.loc[df_filtered['Unidade'].isin(store_filter)]
if (region_filter):
  df_filtered = df_filtered.loc[df_filtered['Região'].isin(region_filter)]

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

st.markdown("## Gráficos")

visualizao_filter = st.selectbox(label= 'Selecione a Visualização',
                                 placeholder = 'Selecione a Visualização',
                                 options=["Account Name","Campaign Name","Categoria","Unidade","Região"],
                                 index=0)

df_amount_spent = df_filtered.pivot_table(
    index="Day", columns=visualizao_filter, values="Amount Spent", aggfunc="sum", fill_value=0
)

df_amount_spent.index = pd.to_datetime(df_amount_spent.index).strftime('%d/%m/%Y')
df_amount_spent = df_amount_spent.sort_values(by="Day", ascending=False)

df_results = df_filtered.pivot_table(
    index="Day", columns=visualizao_filter, values="Results", aggfunc="sum", fill_value=0
)

df_results.index = pd.to_datetime(df_results.index).strftime('%d/%m/%Y')
df_results = df_results.sort_values(by="Day", ascending=False)

metric_filter = st.selectbox(label= 'Selecione a Métrica',
                                 placeholder = 'Selecione a Métrica',
                                 options=["Custo","Resultados"],
                                 index=0)


if (metric_filter == "Custo"):
  table = df_amount_spent.copy()
  table.loc['Total'] = table.sum()
  table = table.applymap(lambda x: f"R${x:,.2f}")

  graph = df_amount_spent
  markdown = "Custo (R$)"

elif (metric_filter == "Resultados"):
  table = df_results.copy()
  table.loc['Total'] = table.sum()

  graph = df_results
  markdown = "Resultados"

else:
  table = None

st.markdown(f"## {markdown}")
st.line_chart(data=graph,y=graph.columns)

st.markdown(f"## Tabelas - {markdown}")


st.dataframe(
    table,
    use_container_width=True,
  )
