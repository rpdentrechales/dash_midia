import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Pró-Corpo - COnfigurar Metas", page_icon="💎",layout="wide")

@st.cache_data
def load_aux_dataframe(worksheet,duplicates_subset):

  conn = st.connection("gsheets", type=GSheetsConnection)
  df = conn.read(worksheet=worksheet)
  df = df.drop_duplicates(subset=duplicates_subset)

  return df

df_metas = load_aux_dataframe("aux - Configurar metas")

df_metas
