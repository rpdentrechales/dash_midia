import streamlit as st 
import altair as alt
import pandas as pd

# Show the page title and description.
st.set_page_config(page_title="Pró-Corpo - Dash de Mídia", page_icon="💎")
st.title("💎 Facebook Ads")

# Load the data from a CSV. We're caching this so it doesn't reload every time the app
# reruns (e.g. if the user interacts with the widgets).
# @st.cache_data
# def load_data():
#     df = pd.read_csv("/data/fb_data_clean.csv")
#     return df


# df = load_data()
df = pd.read_csv("/data/fb_data_clean.csv")

# Show a multiselect widget with the genres using `st.multiselect`.
unidades = st.multiselect(
    "Unidades",
    df["store"].unique(),
    default = ['IPIRANGA', 'TUCURUVI', 'MOEMA', 'JARDINS', 'ITAIM']
)

# Filter the dataframe based on the widget input and reshape it.
df_filtered = df[df["store"].isin(unidades)]
df_reshaped = df_filtered.pivot_table(
    index="month", columns="category", values="Resultados", aggfunc="sum", fill_value=0
)
df_reshaped = df_reshaped.sort_values(by="month", ascending=False)

df_reshaped


# Display the data as a table using `st.dataframe`.
st.dataframe(
    df_reshaped,
    use_container_width=True,
    column_config={"year": st.column_config.TextColumn("Year")},
)
