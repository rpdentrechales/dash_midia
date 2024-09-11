
import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.title("Read Google Sheet as DataFrame")

conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(worksheet="FB - Compilado")

df.drop_duplicates(subset=["Day","Ad ID"],inplace=True)

conn.update(data=df,worksheet="FB - Compilado")

st.dataframe(df)
