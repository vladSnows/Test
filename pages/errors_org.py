import streamlit as st
import pandas as pd
from OraConnector import *

st.title("Błędy przetwarzań")

if "connector" not in st.session_state:
    st.session_state.connector = None
if "connected" not in st.session_state:
    st.session_state.connected = False

connection_DMSF = get_dmsf_cml_connection()

query = """
SELECT *
FROM (
SELECT
T_BATCH_ID as "Batch ID",
T_PROCESS_NAME as "Process Name",
T_PROCESS_EXEC_ID as "Process Execution ID",
TABLE_NAME as "Table Name",
WORKFLOW_NAME as "Workflow Name",
MAPPING_NAME as "Mapping Name",
ERROR_TIMESTAMP as "Error Timestamp",
ERROR_MSG as "Error message"
FROM DEV03_DMSF_CML.MT_PROCESSING_ERROR
WHERE
SUBSTR(T_BATCH_ID,1,8) = REPLACE(TO_CHAR(:processing_date), '-' )
AND (:workflow_name IS NULL OR WORKFLOW_NAME = :workflow_name)
ORDER BY ERROR_TIMESTAMP DESC)
OFFSET {offset} ROWS FETCH NEXT {limit} ROWS ONLY
"""

@st.cache_data
def get_workflow_names():
    name_query = "SELECT DISTINCT WORKFLOW_NAME FROM DEV03_DMSF_CML.MT_PROCESSING_ERROR ORDER BY WORKFLOW_NAME"
    return pd.read_sql(name_query, connection_DMSF)["WORKFLOW_NAME"].tolist()

workflow_names = get_workflow_names()

col0, col1, col2, col3 = st.columns([1.5, 1, 3, 3])

with col0:
    workflow_name = st.selectbox("**Workflow Name**", [""] + workflow_names)

with col1:
    processing_date = st.date_input("**Processing/Error Date**", value=None)

if "errors_last_filters" not in st.session_state or not isinstance(st.session_state.errors_last_filters, dict):
    st.session_state.errors_last_filters = {}

for key in ["workflow_name", "processing_date"]:
    if key not in st.session_state.errors_last_filters:
        st.session_state.errors_last_filters[key] = None

filters_changed = (
    st.session_state.errors_last_filters["workflow_name"] != workflow_name or
    st.session_state.errors_last_filters["processing_date"] != processing_date
)

if filters_changed:
    st.session_state.errors_offset = 0
    st.session_state.errors_data_cache = pd.DataFrame()
    st.session_state.errors_initial_load_done = False
    st.session_state.errors_last_filters["workflow_name"] = workflow_name
    st.session_state.errors_last_filters["processing_date"] = processing_date

if "errors_offset" not in st.session_state:
    st.session_state.errors_offset = 0
if "errors_limit" not in st.session_state:
    st.session_state.errors_limit = 20
if "errors_data_cache" not in st.session_state:
    st.session_state.errors_data_cache = pd.DataFrame()
if "errors_initial_load_done" not in st.session_state:
    st.session_state.errors_initial_load_done = False

params_dict = {
    "workflow_name": workflow_name if workflow_name else None,
    "processing_date": processing_date if processing_date else None
}

offset = st.session_state.errors_offset
limit = st.session_state.errors_limit

paginated_query = query.format(offset=offset, limit=limit)

@st.cache_data
def get_total_count(_connection, params):
    count_query = """
    SELECT COUNT(*) FROM DEV03_DMSF_CML.MT_PROCESSING_ERROR
    WHERE SUBSTR(T_BATCH_ID,1,8) = REPLACE(TO_CHAR(:processing_date), '-' )
    AND (:workflow_name IS NULL OR WORKFLOW_NAME = :workflow_name)
    """
    with _connection.cursor() as cursor:
        cursor.execute(count_query, params)
        return cursor.fetchone()[0]

if "errors_total_count" not in st.session_state or filters_changed:
    st.session_state.errors_total_count = get_total_count(connection_DMSF, params_dict)

@st.cache_data
def execute_dynamic_query(_connection, query, params):
    with _connection.cursor() as cursor:
        cursor.execute(query, params)
        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        return pd.DataFrame(rows, columns=columns)

if not st.session_state.errors_initial_load_done or filters_changed:
    paginated_query = query.format(
        offset=st.session_state.errors_offset,
        limit=st.session_state.errors_limit
    )
    new_data = execute_dynamic_query(connection_DMSF, paginated_query, params_dict)
    st.session_state.errors_data_cache = new_data
    st.session_state.errors_offset = st.session_state.errors_limit
    st.session_state.errors_initial_load_done = True

st.dataframe(st.session_state.errors_data_cache, use_container_width=True)

st.markdown(f"**Showing {len(st.session_state.errors_data_cache)} of {st.session_state.errors_total_count} records**")

if len(st.session_state.errors_data_cache) < st.session_state.errors_total_count:
    if st.button("Pokaż więcej"):
        paginated_query = query.format(
            offset=st.session_state.errors_offset,
            limit=st.session_state.errors_limit
        )
        new_data = execute_dynamic_query(connection_DMSF, paginated_query, params_dict)
        st.session_state.errors_data_cache = pd.concat([st.session_state.errors_data_cache, new_data], ignore_index=True)
        st.session_state.errors_offset += st.session_state.errors_limit
        st.rerun()
else:
    st.info("All records loaded.")

st.markdown(
    """
    <style>
    .stDataFrame > div {
        height: 55vh !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)