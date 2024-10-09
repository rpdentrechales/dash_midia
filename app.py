import streamlit as st

# --- PAGE SETUP ---
fb_page = st.Page(
    "views/fb_dash.py",
    title="Facebook Dash",
    icon=":material/thumb_up:",
    default=True,
)
acompanhamento_fb_page = st.Page(
    "views/acompanhamento_fb.py",
    title="Acompanhamento FB",
    icon=":material/summarize:",
)
metas_categoria_page = st.Page(
    "views/metas_categoria.py",
    title="Meta por Categoria",
    icon=":material/manufacturing:",
)
metas_unidade_page = st.Page(
    "views/metas_unidade.py",
    title="Meta por Unidade",
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
        "Relatórios": [fb_page, acompanhamento_fb_page],
        "Cadastrar Metas": [metas_unidade_page,metas_categoria_page]
    }
)


# --- SHARED ON ALL PAGES ---
# st.logo("assets/codingisfun_logo.png")


# --- RUN NAVIGATION ---
pg.run()
