import streamlit as st
import json
import base64

def context_loadout():
    data = st.context.headers.get("X-Ms-Client-Principal", "")
    if not data:
        return
    missing_padding = len(data) % 4
    if missing_padding:
        data += '=' * (4 - missing_padding)
    decoded = base64.b64decode(data)
    decoded_json = json.loads(decoded.decode("utf-8"))
    st.session_state.claims = decoded_json.get("claims", [])

def get_claim_value(claims: list, claim_type: str) -> str:
    return next(
        (claim["val"] for claim in claims if claim.get("typ") == claim_type),
        f"Nie znaleziono pola '{claim_type}'"
    )

def has_claim_value(claims: list, claim_type: str, expected_value: str) -> bool:
    return any(
        claim.get("typ") == claim_type and claim.get("val") == expected_value
        for claim in claims
    )

def login():
    import streamlit as st
    import time
    from utils.helper import initConnection
    c1, c2, c3 = st.columns([3, 3, 3])
    with c2:
        # context_loadout() ##! app-rad
        st.image("images/streamlit_logo.png")
        container = st.container(border=True)
        container.title("DMSF Środowisko DEV - wersja 001.027.00")
        container.caption("Powered by :blue[Streamlit!]")
        # st.session_state.streamlit_privilege = (has_claim_value(st.session_state.claims, "groups", "512bc6b1-b534-49df-b5f4-618da7b012d9")) ##! app-rad
        # st.session_state.username = container.text_input("Witaj", key="username_input", disabled=True, placeholder=get_claim_value(st.session_state.claims, "name")) ##! app-rad
        # st.session_state.password = os.environ.get("DBPASS","") ## zmienna w app service - hasło do oracle ##! app-rad
        # st.session_state.dbschema = "DEV01_FATCRS"
        # st.session_state.username = st.text_input("Username", key="username_input")  ##! Revert-debug
        # st.session_state.password = st.text_input("db-debug-Password", key="password_input", type='password')  ##! Revert-debug
        # st.session_state.dbschema = st.text_input("Schema name", placeholder='np. DEV01_FATCRS')  ##! Revert-debug

        if container.button("Przejdź dalej", key="login_button"):
            with st.status("Inicjalizacja aplikacji...", expanded=True) as status:
                time.sleep(0.5)
                status.update(label="Aplikacja załadowana...", state="complete", expanded=True)
                time.sleep(1)
                st.session_state.logged_in = True
                if initConnection():
                    st.toast(f"Connected", icon="✅")
                    st.session_state.logged_in = True
                    time.sleep(0.5)
                else:
                    st.session_state.logged_in = False
                    st.toast(f"Database connection failed", icon="❌")
                    time.sleep(0.5)
                st.rerun()

def logout():
    import streamlit as st
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.password = ""
    st.session_state.admin = False
    st.cache_data.clear()
    st.rerun()
