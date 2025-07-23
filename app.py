import streamlit as st
import streamlit as stlib
from core.config import APP_TITLE, AUTH_USERS
from components.footer import render_footer
from components.header import render_header
from utils.session import get_session_state

st.set_page_config(
    page_title=APP_TITLE,
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Report a bug': 'mailto:huta@mbank.pl?subject=DMSF%20%E2%80%93%20nieprawid%C5%82owe%20dzia%C5%82anie%20aplikacji%20Streamlit',
        'About': "DMSF Professional App – Monitorowanie i raportowanie statusu oraz błędów przetwarzań DMSF."
    }
)
render_header()

session = get_session_state()

if "logged_in" not in session:
    session.logged_in = False

# Authentication logic

def login():
    st.subheader("Log in to DMSF Professional App")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Log in"):
        if username in AUTH_USERS and AUTH_USERS[username] == password:
            session.logged_in = True
            session.username = username
            st.success(f"Welcome, {username}!")
            st.rerun()
        else:
            st.error("Invalid username or password.")

def logout():
    st.write(f"Logged in as: {session.get('username', '')}")
    if st.button("Log out"):
        session.logged_in = False
        session.username = ""
        st.rerun()

login_page = st.Page(login, title="Log in", icon=":material/login:")
logout_page = st.Page(logout, title="Log out", icon=":material/logout:")

pages = [
    st.Page(
        "pages/home.py",
        title="Przetwarzania DMSF",
        icon=":material/monitor_heart:"
    ),
    st.Page(
        "pages/errors.py",
        title="Błędy przetwarzań",
        icon=":material/error:"
    ),
    # Add more pages as needed
]

try:
    if session.logged_in:
        pg = st.navigation(
            {
                "🏠 Account": [logout_page],
                "📊 DMSF Reports": pages
            }
        )
    else:
        pg = st.navigation([login_page])
    pg.run()
except Exception as e:
    st.error(f"An error occurred: {e}")

render_footer()
