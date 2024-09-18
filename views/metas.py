import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

st.set_page_config(page_title="Pró-Corpo - COnfigurar Metas", page_icon="💎",layout="wide")

@st.cache_data
def load_dataframe(worksheet):

  conn = st.connection("gsheets", type=GSheetsConnection)
  df = conn.read(worksheet=worksheet)

  return df

st.markdown("# Cadastrar Metas")

df_metas = load_dataframe("aux - Configurar metas",)

df_metas["month"] = df_metas["month"].dt.to_period("M")

current_date = datetime.now()
periods = pd.period_range(start=current_date - pd.DateOffset(months=11), 
                          end=current_date, freq='M')

period_filter = st.selectbox("Selecione o Mês",periods)

filtered_metas = df_metas.loc[df_metas["month"] == period_filter]

filtered_metas
