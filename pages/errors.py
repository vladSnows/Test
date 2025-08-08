import streamlit as st
import pandas as pd
from utils import helper as u
from sqlalchemy.orm import sessionmaker
from db.models import MtProcessingError
from db.generic_utils import get_unique_column_values, get_paginated_data, get_total_count_orm, errors_query
from st_aggrid import AgGrid, GridOptionsBuilder

st.title("Błędy przetwarzań")

# Initialize connection
if "connector" not in st.session_state:
    st.session_state.connector = None
if "connected" not in st.session_state:
    st.session_state.connected = False

# Get DB connection
engine = u.getEngine()
Session = sessionmaker(bind=engine)
session = Session()

if 'isInitialOpen_ERRORS' not in st.session_state:
    st.session_state['isInitialOpen_ERRORS'] = True
else:
    st.session_state['isInitialOpen_ERRORS'] = False

if st.session_state.get('isInitialOpen_ERRORS', True):
    session_defaults = {
        'errors_last_filters': {
            'workflow_name': None,
            'processing_date': None
        }
    }
    for key, val in session_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

for key, default_value in st.session_state.errors_last_filters.items():
    if key not in st.session_state.errors_last_filters or st.session_state.errors_last_filters[key] is None:
        if key == 'workflow_name':
            st.session_state.errors_last_filters[key] = get_unique_column_values(session, MtProcessingError.workflow_name)

col0, col1, col2, col3 = st.columns([1.5, 1, 3, 3])

with col0:
    workflow_name = st.selectbox("**Workflow Name**", options=[None] + sorted(st.session_state.errors_last_filters['workflow_name']), key='WORKFLOW_NAME')

with col1:
    processing_date = st.date_input("**Processing/Error Date**", value=None)

filters = []
if workflow_name:
    filters.append(MtProcessingError.workflow_name == workflow_name)
if processing_date:
    filters.append(MtProcessingError.error_timestamp.cast(pd.Timestamp).date() == processing_date)

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

if "errors_total_count" not in st.session_state or filters_changed:
    st.session_state.errors_total_count = get_total_count_orm(
        session,
        errors_query(session),
        filters
    )

if not st.session_state.errors_initial_load_done or filters_changed:
    results = get_paginated_data(
        session,
        errors_query(session),
        filters,
        offset,
        limit,
        order_by=MtProcessingError.error_timestamp,
        desc=True
    )
    new_data = pd.DataFrame([r._asdict() for r in results])
    st.session_state.errors_data_cache = new_data
    st.session_state.errors_offset = st.session_state.errors_limit
    st.session_state.errors_initial_load_done = True

if st.session_state.errors_data_cache is not None and not st.session_state.errors_data_cache.empty and len(st.session_state.errors_data_cache.columns) > 0:
    gb = GridOptionsBuilder.from_dataframe(st.session_state.errors_data_cache)
    gb.configure_default_column(
        filter=True,
        sortable=True,
        groupable=True,
        resizable=True,
        wrapText=True,
        autoHeight=True,
        enableRowGroup=True,
        enablePivot=True,
        enableValue=True,
        headerCheckboxSelection=True,
    )
    gb.configure_grid_options(
        pagination=True,
        paginationAutoPageSize=False,
        domLayout='normal',
        suppressRowClickSelection=False,
        rowSelection='single',
        enableRangeSelection=True,
        suppressAggFuncInHeader=False,
        animateRows=True,
        defaultColDef={
            "resizable": True,
            "sortable": True,
            "filter": True
        },
        groupSelectsChildren=True,
        suppressRowDeselection=False,
        suppressCellSelection=False,
        suppressHorizontalScroll=False
    )
    gb.configure_side_bar()
    grid_options = gb.build()
    AgGrid(st.session_state.errors_data_cache, gridOptions=grid_options, enable_enterprise_modules=True, theme="streamlit", update_mode="NO_UPDATE", pagination=True, height=400)
    st.markdown(f"**Showing {len(st.session_state.errors_data_cache)} of {st.session_state.errors_total_count} records**")
else:
    st.info("No data to display for the selected filters.")

if len(st.session_state.errors_data_cache) < st.session_state.errors_total_count:
    if st.button("Pokaż więcej"):
        results = get_paginated_data(
            session,
            errors_query(session),
            filters,
            offset,
            limit,
            order_by=MtProcessingError.error_timestamp,
            desc=True
        )
        new_data = pd.DataFrame([r._asdict() for r in results])
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
