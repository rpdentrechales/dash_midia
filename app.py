import streamlit as st

# --- PAGE SETUP ---
fb_page = st.Page(
    "views/fb_dash.py",
    title="Facebook Dash",
    icon=":material/thumb_up:",
    default=True,
)
acompanhamento_page = st.Page(
    "views/acompanhamento.py",
    title="Acompanhamento",
    icon=":material/summarize:",
)
metas_page = st.Page(
    "views/metas.py",
    title="Cadastrar Metas",
    icon=":material/manufacturing:",
)
google_page = st.Page(
    "views/google_dash.py",
    title="Google Dash",
    icon=":material/search:",
)
gsheets_test = st.Page(
    "views/test_gsheets.py",
    title="Testes",
    icon=":material/bug_report:",
)


# --- NAVIGATION SETUP [WITHOUT SECTIONS] ---
# pg = st.navigation(pages=[about_page, project_1_page, project_2_page])

# --- NAVIGATION SETUP [WITH SECTIONS]---
pg = st.navigation(
    {
        "Relatórios": [fb_page, acompanhamento_page],
        "Configurações": [metas_page,gsheets_test]
    }
)


# --- SHARED ON ALL PAGES ---
# st.logo("assets/codingisfun_logo.png")


# --- RUN NAVIGATION ---
pg.run()
