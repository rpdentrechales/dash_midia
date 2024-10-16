import streamlit as st
import altair as alt
import pandas as pd
import plotly.express as px
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

st.set_page_config(page_title="Pró-Corpo - Acompanhamento", page_icon="💎",layout="wide")

def days_until_end_of_month(period):
    today = datetime.today()

    if period.year == today.year and period.month == today.month:
        last_day_of_month = period.end_time
        days_remaining = (last_day_of_month - pd.Timestamp(today)).days
        return days_remaining
    else:
        return None


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

df_fb = load_main_dataframe("FB - Compilado")

df_categorias = load_aux_dataframe("Auxiliar - Categorias","Anuncio")
df_unidades = load_aux_dataframe("Auxiliar - Unidades","Campaign Name")
df_whatsapp = load_aux_dataframe("Auxiliar - Whatsapp","Ad Name")

df_metas_categoria = load_aux_dataframe("aux - Configurar metas categoria",["plataforma","month","categoria"])
df_metas_unidade = load_aux_dataframe("aux - Configurar metas unidade",["unidade","month"])

df_metas_unidade['month'] = pd.to_datetime(df_metas_unidade['month'])
df_metas_unidade['month'] = df_metas_unidade['month'].dt.to_period('M')

df_metas_categoria['month'] = pd.to_datetime(df_metas_categoria['month'])
df_metas_categoria['month'] = df_metas_categoria['month'].dt.to_period('M')

df_fb = pd.merge(df_fb,df_categorias,how="left",left_on="Ad Name",right_on="Anuncio")
df_fb = df_fb.drop(columns=["Anuncio"])
df_fb["Results"] = df_fb["Results"].fillna(0)

df_fb = pd.merge(df_fb,df_unidades,how="left",left_on="Campaign Name",right_on="Campaign Name")
df_fb["Unidade"] = df_fb["Unidade"].fillna("Sem Categoria")
df_fb["Região"] = df_fb["Região"].fillna("Sem Categoria")

whatsapp_map = df_whatsapp.set_index('Ad Name')['Categoria'].to_dict()
df_fb.loc[df_fb['Account Name'] == "Campanhas Whatsapp","Categoria"] = df_fb.loc[df_fb['Account Name'] == "Campanhas Whatsapp","Ad Name"].map(whatsapp_map)

df_fb["Categoria"] = df_fb["Categoria"].fillna("Sem Categoria")
df_fb["month"] = df_fb["Day"].dt.to_period("M")

df_sem_cirurgia = df_fb.loc[df_fb["Account Name"] != "CA1 - ANUNCIANTE - MAIS CIRURGIA"]
df_cirurgia = df_fb.loc[df_fb["Account Name"] == "CA1 - ANUNCIANTE - MAIS CIRURGIA"]

titulo_1,titulo_2 = st.columns([3,1])

with titulo_1:
  st.markdown("# Acompanhamento de Mídia")

with titulo_2:
  month_filter = st.selectbox(label = "Selecione o Mês",
                                   placeholder= 'Selecione o mês',
                                   options=df_sem_cirurgia['month'].unique())

st.markdown("## Facebook - Total por Unidade")

store_filter = st.selectbox(label = "Selecione a Unidade",
                                   placeholder= 'Selecione a Unidade',
                                   options=df_sem_cirurgia['Unidade'].unique())

if (month_filter):
  df_sem_cirurgia = df_sem_cirurgia.loc[df_sem_cirurgia['month'] == month_filter]
  df_meta_categoria_mes = df_metas_categoria.loc[df_metas_categoria['month'] == month_filter]
  df_meta_unidade_mes = df_metas_unidade.loc[df_metas_unidade['month'] == month_filter]
  df_metas_categoria_mes = df_metas_categoria.loc[df_metas_categoria['month'] == month_filter]

if (store_filter):
  df_filtered = df_sem_cirurgia.loc[df_sem_cirurgia['Unidade'] == store_filter]
  meta_selecionada = df_meta_unidade_mes.loc[df_meta_unidade_mes['unidade'] == store_filter]

meta_facebook_mes = meta_selecionada["meta facebook"].values[0]
df_metas_categoria_mes = df_metas_categoria_mes.loc[df_metas_categoria["plataforma"] == "Facebook"]

df_metas_categoria_mes["meta"] = df_metas_categoria_mes["meta"]/100

metrics_unidade_1,metrics_unidade_2,metrics_unidade_3,metrics_unidade_4,metrics_unidade_5,metrics_unidade_6 = st.columns(6)

total_unidade_resultados = df_filtered["Results"].sum()
total_unidade_custo = df_filtered["Amount Spent"].sum()
total_unidade_cpl = total_unidade_custo/total_unidade_resultados

verba_restante = meta_facebook_mes - total_unidade_custo
dias_para_o_fim_do_mes = days_until_end_of_month(month_filter)
if dias_para_o_fim_do_mes:
  verba_restante_por_dia = verba_restante/dias_para_o_fim_do_mes
  verba_restante_por_dia = f"R$ {verba_restante_por_dia :.2f}"
else:
  verba_restante_por_dia = "-"

with metrics_unidade_1:
  st.metric("Resultados Total",f"{total_unidade_resultados :.0f}")
with metrics_unidade_2:
  st.metric("Custo Total",f"R$ {total_unidade_custo :.2f}")
with metrics_unidade_3:
  st.metric("CPL Total",f"R$ {total_unidade_cpl :.2f}")
with metrics_unidade_4:
  st.metric("Verba Total",f"R$ {meta_facebook_mes :.2f}")
with metrics_unidade_5:
  st.metric("Verba Restante",f"R$ {verba_restante :.2f}")
with metrics_unidade_6:
  st.metric("Verba Restante por dia",verba_restante_por_dia)

categoria_groupby = df_filtered.groupby(["Categoria"]).agg({"Results":"sum","Amount Spent":"sum"})

categoria_groupby["CPL"] = categoria_groupby["Amount Spent"]/categoria_groupby["Results"]

categoria_total_row = pd.DataFrame(categoria_groupby[['Results', 'Amount Spent']].sum()).transpose()
categoria_total_row["CPL"] = categoria_total_row['Amount Spent']/categoria_total_row['Results']

categoria_total_resultados = categoria_total_row['Results'].values[0]
categoria_total_custo = categoria_total_row['Amount Spent'].values[0]
categoria_total_cpl = categoria_total_row['CPL'].values[0]

categoria_groupby["share_custo"] = (categoria_groupby["Amount Spent"]/categoria_total_custo) * 100
categoria_groupby["share_resultados"] = (categoria_groupby["Results"]/categoria_total_resultados) * 100

categoria_groupby = pd.merge(categoria_groupby,df_metas_categoria_mes[["categoria","meta"]],how="left",left_on=["Categoria"],right_on=["categoria"])

categoria_groupby["verba total"] = meta_facebook_mes*categoria_groupby["meta"]
categoria_groupby["verba restante"] = categoria_groupby["verba total"] - categoria_groupby["Amount Spent"]

if dias_para_o_fim_do_mes:
  categoria_groupby["verba restante por dia"] = categoria_groupby["verba restante"]/dias_para_o_fim_do_mes
else:
  categoria_groupby["verba restante por dia"] = 0

colunas = ["categoria","Amount Spent","Results","CPL","share_custo","share_resultados","verba total","verba restante","verba restante por dia"]
display_categoria_df = categoria_groupby[colunas]

st.dataframe(
    display_categoria_df,
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
        "categoria": st.column_config.Column(
            "Categoria",
            width="medium"
        ),
        "Results": st.column_config.NumberColumn(
            "Resultados",
            width="small"
        ),
        "share_custo": st.column_config.NumberColumn(
            "Share Custo (%)",
            format="%.2f %%",
            width="small"
        ),
        "share_resultados": st.column_config.NumberColumn(
            "Share Resultados (%)",
            format="%.2f %%",
            width="small"
        ),
        "verba total": st.column_config.NumberColumn(
            "Verba total",
            format="R$ %.2f",
            width="small"
        ),
        "verba restante": st.column_config.NumberColumn(
            "Verba Restante",
            format="R$ %.2f",
            width="small"
        ),
        "verba restante por dia": st.column_config.NumberColumn(
            "verba restante por dia",
            format="R$ %.2f",
            width="small"
        )
    }
    ,hide_index = True
  )

st.markdown("## Facebook - Total por categoria")

total_groupby = df_sem_cirurgia.groupby(["Categoria"]).agg({"Results":"sum","Amount Spent":"sum"})
total_groupby = total_groupby.reset_index()
total_groupby["CPL"] = total_groupby["Amount Spent"]/total_groupby["Results"]

total_row = pd.DataFrame(total_groupby[['Results', 'Amount Spent']].sum()).transpose()
total_row["CPL"] = total_row['Amount Spent']/total_row['Results']

total_resultados = total_row['Results'].values[0]
total_custo = total_row['Amount Spent'].values[0]
total_cpl = total_row['CPL'].values[0]

total_groupby["share_custo"] = (total_groupby["Amount Spent"]/total_custo) * 100
total_groupby["share_resultados"] = (total_groupby["Results"]/total_resultados) * 100

metrics_1,metrics_2,metrics_3 = st.columns(3)

with metrics_1:
  st.metric("Resultados Total",f"{total_resultados :.0f}")
with metrics_2:
  st.metric("Custo Total",f"R$ {total_custo :.2f}")
with metrics_3:
  st.metric("CPL Total",f"R$ {total_cpl :.2f}")

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
        "share_custo": st.column_config.NumberColumn(
            "Share Custo (%)",
            format="%.2f %%",
            width="small"
        ),
        "share_resultados": st.column_config.NumberColumn(
            "Share Resultados (%)",
            format="%.2f %%",
            width="small"
        )
    },
    hide_index = True
  )
