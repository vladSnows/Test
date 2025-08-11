import streamlit as st
import pandas as pd
from utils import helper as u
from sqlalchemy.orm import sessionmaker
from db.models import EvRkProcDqApex
from db.generic_utils import get_unique_column_values, get_paginated_data, get_total_count_orm
from sqlalchemy.dialects import oracle
from st_aggrid import AgGrid, GridOptionsBuilder

st.title("LOGi Data Quality")


# Initialize connection
if "connector" not in st.session_state:
    st.session_state.connector = None
if "connected" not in st.session_state:
    st.session_state.connected = False

# Get DB connection
engine = u.getEngine()
Session = sessionmaker(bind=engine)
session = Session()
connection_DMSF = engine.raw_connection()

# Remove st.cache_data from get_unique_column_values usage for dropdowns
batch_ids = get_unique_column_values(session, EvRkProcDqApex.t_batch_id)
dq_codes = get_unique_column_values(session, EvRkProcDqApex.dq_code)
process_names = get_unique_column_values(session, EvRkProcDqApex.t_process_name)

# Active filters
col0, col1, col2, col3 = st.columns([1, 0.5, 1.5, 3])

with col0:
    batch_id = st.selectbox("**Batch ID**", [""] + batch_ids)
with col1:
    dq_code = st.selectbox("**DQ Code**", [""] + [int(code) if code is not None and str(code).isdigit() else code for code in dq_codes])
with col2:
    process_name = st.selectbox("**Process Name**", [""] + process_names)

# Reset filters if changed
if "logs_last_filters" not in st.session_state or not isinstance(st.session_state.logs_last_filters, dict):
    st.session_state.logs_last_filters = {}

for key in ["batch_id", "dq_code", "process_name"]:
    if key not in st.session_state.logs_last_filters:
        st.session_state.logs_last_filters[key] = None

# Fix: On first load, do not apply any filters (show all records)
if (
    st.session_state.logs_last_filters["batch_id"] is None and
    st.session_state.logs_last_filters["dq_code"] is None and
    st.session_state.logs_last_filters["process_name"] is None and
    batch_id == "" and dq_code == "" and process_name == ""
):
    filters_changed = False
else:
    filters_changed = (
        st.session_state.logs_last_filters["batch_id"] != batch_id or
        st.session_state.logs_last_filters["dq_code"] != dq_code or
        st.session_state.logs_last_filters["process_name"] != process_name
    )

if filters_changed:
    st.session_state.logs_offset = 0
    st.session_state.logs_data_cache = pd.DataFrame()
    st.session_state.logs_initial_load_done = False
    st.session_state.logs_last_filters["batch_id"] = batch_id
    st.session_state.logs_last_filters["dq_code"] = dq_code
    st.session_state.logs_last_filters["process_name"] = process_name

# Session state defaults
if "logs_offset" not in st.session_state:
    st.session_state.logs_offset = 0
if "logs_limit" not in st.session_state:
    st.session_state.logs_limit = 20
if "logs_data_cache" not in st.session_state:
    st.session_state.logs_data_cache = pd.DataFrame()
if "logs_initial_load_done" not in st.session_state:
    st.session_state.logs_initial_load_done = False

params_dict = {
    "batch_id": batch_id if batch_id else None,
    "dq_code": dq_code if dq_code else None,
    "process_name": process_name if process_name else None
}

offset = st.session_state.logs_offset
limit = st.session_state.logs_limit

# Build filters for ORM
filters = []
if batch_id not in (None, ""):
    filters.append(EvRkProcDqApex.t_batch_id == batch_id)
if dq_code not in (None, ""):
    filters.append(EvRkProcDqApex.dq_code == str(dq_code))
if process_name not in (None, ""):
    filters.append(EvRkProcDqApex.t_process_name == process_name)

# Ensure all three filters can be set independently
# Fix: Always update all three filter values in session state, even if unchanged
st.session_state.logs_last_filters["batch_id"] = batch_id
st.session_state.logs_last_filters["dq_code"] = dq_code
st.session_state.logs_last_filters["process_name"] = process_name

from db.generic_utils import logs_query

# Get total count
if "logs_total_count" not in st.session_state or filters_changed:
    st.session_state.logs_total_count = get_total_count_orm(
        session,
        logs_query(session),
        filters
    )

# Load data (pagination)
if not st.session_state.logs_initial_load_done or filters_changed:
    data = get_paginated_data(
        session,
        logs_query(session),
        filters,
        offset,
        limit,
        order_by=EvRkProcDqApex.processing_date,
        desc=True
    )
    df = pd.DataFrame([row._asdict() for row in data])
    st.session_state.logs_data_cache = df
    st.session_state.logs_offset = limit
    st.session_state.logs_initial_load_done = True

# Ensure all date columns are formatted as YYYY-MM-DD strings
date_columns = [col for col in st.session_state.logs_data_cache.columns if 'date' in col.lower() or 'timestamp' in col.lower()]
for col in date_columns:
    st.session_state.logs_data_cache[col] = pd.to_datetime(st.session_state.logs_data_cache[col], errors='coerce').dt.strftime('%Y-%m-%d')

# Show data
if st.session_state.logs_data_cache is not None and not st.session_state.logs_data_cache.empty and len(st.session_state.logs_data_cache.columns) > 0:
    gb = GridOptionsBuilder.from_dataframe(st.session_state.logs_data_cache)
    gb.configure_default_column(
        filter=True,
        sortable=True,
        groupable=True,
        resizable=True,
        flex=1,  # Fit columns to table size
        wrapText=True,
        autoHeight=True,
        enableRowGroup=True,
        enablePivot=True,
        enableValue=True,
        headerCheckboxSelection=True,
    )
    # Format date columns to YYYY-MM-DD
    date_columns = [col for col in st.session_state.logs_data_cache.columns if 'date' in col.lower() or 'timestamp' in col.lower()]
    for col in date_columns:
        gb.configure_column(col, valueFormatter="(d ? d.substring(0, 10) : '')")
    gb.configure_default_column(resizable=True, flex=1)
    gb.configure_grid_options(
        pagination=False,
        domLayout='normal',
        suppressRowClickSelection=False,
        rowSelection='single',
        enableRangeSelection=True,
        suppressAggFuncInHeader=False,
        animateRows=True,
        defaultColDef={
            "resizable": True,
            "sortable": True,
            "filter": True,
            "flex": 1
        },
        groupSelectsChildren=True,
        suppressRowDeselection=False,
        suppressCellSelection=False,
        suppressHorizontalScroll=False
    )
    gb.configure_side_bar()
    grid_options = gb.build()
    # Detect Streamlit theme
    theme = "streamlit"
    if hasattr(st, 'get_theme'):
        theme_settings = st.get_theme()
        if theme_settings and theme_settings.get('base') == 'dark':
            theme = "alpine-dark"
        else:
            theme = "streamlit"
    AgGrid(
        st.session_state.logs_data_cache,
        gridOptions=grid_options,
        enable_enterprise_modules=True,
        theme=theme,
        update_mode="NO_UPDATE",
        pagination=False,
        fit_columns_on_grid_load=True,  # Auto-fit columns to grid width
        autoSizeColumns=True,
    )
    st.markdown(f"**Showing {len(st.session_state.logs_data_cache)} of {st.session_state.logs_total_count} records**")
else:
    st.info("No data to display for the selected filters.")

# Load more button
if len(st.session_state.logs_data_cache) < st.session_state.logs_total_count:
    if st.button("Pokaż więcej"):
        data = get_paginated_data(
            session,
            logs_query(session),
            filters,
            st.session_state.logs_offset,
            limit,
            order_by=EvRkProcDqApex.processing_date,
            desc=True
        )
        df = pd.DataFrame([row._asdict() for row in data])
        st.session_state.logs_data_cache = pd.concat([
            st.session_state.logs_data_cache, df
        ], ignore_index=True)
        st.session_state.logs_offset += limit
        st.rerun()
else:
    st.toast("All records loaded.")

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
