# components/sidebar.py
import streamlit as st

def render_sidebar():
    st.sidebar.title("Navigation")
    st.sidebar.markdown("---")
    st.sidebar.page_link("pages/home.py", label="Home")
    st.sidebar.page_link("pages/errors.py", label="Errors")
    # Add more links as needed

