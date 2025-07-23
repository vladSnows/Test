import streamlit as st
import oracledb
import os

DSN = """
  (DESCRIPTION =
    (ADDRESS = (PROTOCOL = TCP)(HOST = exa2-scan.mbank.pl)(PORT = 1521))
    (CONNECT_DATA =
      (SERVER = DEDICATED)
      (SERVICE_NAME = FINREP_DEV_UI)
    )
  )"""

USER = "UI_ZEW_2_33905[DEV03_DMSF_CML]"
PASS_ENV_VAR = "DBPASS"

@st.cache_resource
def get_dmsf_cml_connection():
    password = os.getenv(PASS_ENV_VAR)
    if not password:
        st.error(f"Environment variable '{PASS_ENV_VAR}' is not set.")
        return None
    return oracledb.connect(
        user=USER,
        password=password,
        dsn=DSN
    )

