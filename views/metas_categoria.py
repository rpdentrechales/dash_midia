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

st.markdown("# Cadastrar Metas por Categoria")

st.session_state.setdefault("meta_categoria_df", load_dataframe("aux - Configurar metas categoria"))

df_metas = st.session_state["meta_categoria_df"]

df_categorias = load_dataframe("Auxiliar - Categorias - FB")
categorias = df_categorias["Categoria"].unique()
categorias = list(categorias)

df_metas["month"] = pd.PeriodIndex(df_metas["month"], freq="M")

current_date = datetime.now()
periods = pd.period_range(start=current_date - pd.DateOffset(months=11),
                          end=current_date + pd.DateOffset(months=1), freq='M')

combined_periods = pd.concat([df_metas["month"], pd.Series(periods)])
combined_periods = combined_periods.drop_duplicates().sort_values(ascending=False)
combined_periods = combined_periods.reset_index(drop=True)

filtro_1, filtro_2 = st.columns([2,1])

with filtro_1:
  plataforma_filter = st.selectbox("Selecione a Plataforma",["Facebook","Google Ads"])
with filtro_2:
  period_filter = st.selectbox("Selecione o Mês", combined_periods, index=1)


display_1,display_2 = st.columns([2,1])

with display_1:

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
                                  "meta": st.column_config.NumberColumn(
                                      "Meta",
                                      min_value=0,
                                      format="%d %%"),
                                  "plataforma": st.column_config.Column(
                                      "Plataforma",
                                      disabled = True),
                                  "month": st.column_config.Column(
                                      "Mês",
                                      disabled = True),
                                  "categoria": st.column_config.Column(
                                      "Categoria",
                                      disabled = True)
                                  },
                            hide_index=True,
                            use_container_width = True
                            )
  with display_2:
    soma_da_meta = edited_df["meta"].sum()
    if soma_da_meta != 100:
      st.markdown(f"# :red[{soma_da_meta} %]")
    else:
      st.markdown(f"# :green[{soma_da_meta} %]")

def upload_changes(df_original,df_edited):

  df_to_upload = pd.concat([df_original,df_edited])
  df_to_upload = df_to_upload.drop_duplicates(subset=["plataforma","month","categoria"],keep="last")

  conn = st.connection("gsheets", type=GSheetsConnection)
  try:
    response = conn.update(data=df_to_upload,worksheet="aux - Configurar metas categoria")
    st.session_state["meta_categoria_df"]  = df_to_upload
    st.session_state["callback_meta_categoria_result"] = True
  except:
    response = "Erro"
    st.session_state["callback_meta_categoria_result"] = False

if st.button("Salvar modificações",on_click=upload_changes,args=(st.session_state["meta_categoria_df"],edited_df)):
  if ("callback_meta_categoria_result" in st.session_state) and st.session_state["callback_meta_categoria_result"]:
    st.balloons()
    st.success("Modificações salvas com sucesso")

  else:
    st.error("Erro: Alterações não foram salvas")
