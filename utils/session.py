# utils/session.py
import streamlit as st

def get_session_state():
    return st.session_state

# Add more session-related utilities as needed

def init_session_vars(defaults: dict):
    """
    Initialize session state variables with defaults if not already set.
    Args:
        defaults (dict): key-value pairs for session variables and their default values
    """
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_session_vars(keys: list):
    """
    Reset specified session state variables.
    Args:
        keys (list): list of session variable names to reset
    """
    for key in keys:
        if key in st.session_state:
            del st.session_state[key]


def update_session_flag(key: str, value):
    """
    Update a session flag variable.
    Args:
        key (str): session variable name
        value: value to set
    """
    st.session_state[key] = value
