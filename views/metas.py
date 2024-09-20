import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

st.set_page_config(page_title="Pró-Corpo - Configurar Metas", page_icon="💎",layout="wide")

@st.cache_data()
def load_dataframe(worksheet):

  conn = st.connection("gsheets", type=GSheetsConnection)
  df = conn.read(worksheet=worksheet)

  return df

st.markdown("# Cadastrar Metas")

st.session_state.setdefault("main_df", load_dataframe("aux - Configurar metas"))

df_metas = st.session_state["main_df"]

df_categorias = load_dataframe("Auxiliar - Categorias")
categorias = df_categorias["Categoria"].unique()
categorias = list(categorias)

st.write("df_metas teste")
st.write(df_metas["month"])

df_metas["month"] = pd.to_datetime(df_metas["month"], format='%Y-%m')
df_metas["month"] = df_metas["month"].dt.to_period("M")

current_date = datetime.now()
periods = pd.period_range(start=current_date - pd.DateOffset(months=11),
                          end=current_date, freq='M')

combined_periods = pd.concat([df_metas["month"], pd.Series(periods)])
combined_periods = combined_periods.drop_duplicates().sort_values(ascending=False)
combined_periods = combined_periods.reset_index(drop=True)

filtro_1, filtro_2 = st.columns([2,1])

with filtro_1:
  plataforma_filter = st.selectbox("Selecione a Plataforma",["Facebook","Google Ads"])
with filtro_2:
  period_filter = st.selectbox("Selecione o Mês",combined_periods)

filtered_metas = df_metas.loc[
    (df_metas["month"] == period_filter) &
    (df_metas["plataforma"] == plataforma_filter)
]

if filtered_metas.shape[0] == 0:
  filtered_metas = pd.DataFrame(columns=["plataforma","month","categoria","meta"])
  filtered_metas["categoria"] = categorias
  filtered_metas["plataforma"] = plataforma_filter
  filtered_metas["month"] = period_filter

edited_df = st.data_editor(filtered_metas,
                           column_config={
                                "command": "Streamlit Command",
                                "meta": st.column_config.NumberColumn(
                                    "Meta",
                                    min_value=0,
                                    format="R$ %.2f",
                                )},
                           hide_index=True
                          )

def upload_changes(df_original,df_edited):

  df_to_upload = pd.concat([df_original,df_edited])
  df_to_upload = df_to_upload.drop_duplicates(subset=["plataforma","month","categoria"],keep="last")

  conn = st.connection("gsheets", type=GSheetsConnection)
  try:
    response = conn.update(data=df_to_upload,worksheet="aux - Configurar metas")
    st.session_state["main_df"]  = df_to_upload
    st.session_state["callback_result"] = True
  except:
    response = "Erro"
    st.session_state["callback_result"] = False

st.write("session")
st.dataframe(st.session_state["main_df"])

st.write("dataframe")
st.dataframe(df_metas)

if st.button("Salvar modificações",on_click=upload_changes,args=(st.session_state["main_df"],edited_df)):
  if ("callback_result" in st.session_state) and st.session_state["callback_result"]:
    st.balloons()
    st.success("Modificações salvas com sucesso")

  else:
    st.error("Erro: Alterações não foram salvas")
