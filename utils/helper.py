import os
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
import streamlit as st

def initConnection():
    st.session_state.dbusername = "UI_ZEW_2_33905[DEV02_DMSF_CML]"  # app-rad
    st.session_state.password = os.environ.get("DBPASS", "")
    dsn = '(DESCRIPTION = (ADDRESS = (PROTOCOL = TCP)(HOST = exa2-scan.mbank.pl)(PORT = 1521)) (CONNECT_DATA = (SERVER = DEDICATED) (SERVICE_NAME = FINREP_DEV_UI)))'
    connection_string = f"oracle+oracledb://{st.session_state.dbusername}:{st.session_state.password}@{dsn}"
    engine = create_engine(connection_string)
    try:
        with engine.connect() as conn:
            if conn is not None:
                return True
            else:
                return False
    except SQLAlchemyError:
        return False

def getEngine():
    # Check if engine already exists in session_state
    if "engine" in st.session_state:
        if st.session_state.engine is not None:
            return st.session_state.engine

    # Build connection string
    st.session_state.dbusername = "UI_ZEW_2_33905[DEV03_DMSF_CML]"  # app-rad
    dsn = '(DESCRIPTION = (ADDRESS = (PROTOCOL = TCP)(HOST = exa2-scan.mbank.pl)(PORT = 1521)) (CONNECT_DATA = (SERVER = DEDICATED) (SERVICE_NAME = FINREP_DEV_UI)))'
    connection_string = f"oracle+oracledb://{st.session_state.dbusername}:{st.session_state.password}@{dsn}"

    # Create engine with pool settings
    engine = create_engine(connection_string, pool_size=10, max_overflow=20, pool_timeout=30)
    st.session_state.engine = engine
    return engine
