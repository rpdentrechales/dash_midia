import streamlit as st

# --- PAGE SETUP ---
fb_page = st.Page(
    "views/fb_dash.py",
    title="Facebook Dash",
    icon=":material/thumb_up:",
    default=True,
)
google_page = st.Page(
    "views/google_dash.py",
    title="Google Dash",
    icon=":material/search:",
)
gsheets_test = st.Page(
    "views/test_gsheets.py",
    title="Teste Gsheets",
    icon=":material/bug_report:",
)


# --- NAVIGATION SETUP [WITHOUT SECTIONS] ---
# pg = st.navigation(pages=[about_page, project_1_page, project_2_page])

# --- NAVIGATION SETUP [WITH SECTIONS]---
pg = st.navigation(
    {
        "Relatórios": [fb_page, google_page],
        "teste": [gsheets_test]
    }
)


# --- SHARED ON ALL PAGES ---
# st.logo("assets/codingisfun_logo.png")


# --- RUN NAVIGATION ---
pg.run()
