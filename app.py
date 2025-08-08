import streamlit as st
import json
import base64
import time
from utils.auth import context_loadout, get_claim_value, has_claim_value, login, logout
from utils.helper import initConnection
import os
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Report a bug': 'mailto:huta@mbank.pl?subject=DMSF%20%E2%80%93%20nieprawid%C5%82owe%20dzia%C5%82anie%20aplikacji%20Streamlit',
        'About': "Raport z przetwarzań - DMSF"
    }
)
st.logo(image="images/dmsf_logo.png", size="large")


session_default_values = {
    'logged_in': False,
    'username': "",
    'password': "",
    'admin': False,
    'streamlit_privilege': "",
    'ldap_conn': None,
    'dbschema': None
}
for key, val in session_default_values.items():
    if key not in st.session_state:
        st.session_state[key] = val

login_page = st.Page(login, title="Zaloguj", icon=":material/login:")
logout_page = st.Page(logout, title="Wyloguj", icon=":material/logout:")
pages = [
    st.Page(
        "pages/home.py",
        title="Przetwarzania DMSF",
        icon=":material/monitor_heart:",
        default=True
    ),
    st.Page(
        "pages/errors.py",
        title="Błędy przetwarzań",
        icon=":material/error:"
    ),
    st.Page(
        "pages/logs.py",
        title="LOGi Data Quality",
        icon=":material/analytics:"
    )
]

if st.session_state.logged_in:
    pg_nav = {
        "🏠 Konto": [logout_page],
        "📊 Raporty": pages
    }
    st.sidebar.markdown("**Zalogowany: :green-background[" + "TEST user" + "]**")  #get_claim_value(st.session_state.claims, "name")
    if 1 == 1:  # st.session_state.streamlit_privilege == True:
        st.sidebar.markdown(":blue-badge[:material/verified: Zweryfikowany] :green-badge[:material/deployed_code_update: app v.1.027.00] :orange-badge[:material/manufacturing: in development]")
    else:
        st.sidebar.markdown(":violet-badge[:material/dangerous: Niezweryfikowany] :green-badge[:material/deployed_code_update: app v.1.027.00] :orange-badge[:material/manufacturing: in development]")
    st.sidebar.divider()
else:
    pg_nav = {"Account": [login_page]}

pg = st.navigation(pg_nav)
pg.run()

st.markdown(
    """
    <style>
    .sidebar-footer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        padding: 10px;
        text-align: center;
        font-size: 0.9em;
        color: gray;
    }
    </style>
    <div class="sidebar-footer">
        Made with ❤️ from HUTA
    </div>
    """,
    unsafe_allow_html=True
)