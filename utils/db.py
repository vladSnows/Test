import cx_Oracle
from core.config import DB_HOST, DB_USER, DB_PASS
import streamlit as st
import logging

# Configure logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s %(levelname)s %(message)s')

@st.cache_resource
def get_dmsf_cml_connection():
    """Establish and return a connection to the DMSF CML database."""
    try:
        connection = cx_Oracle.connect(DB_USER, DB_PASS, DB_HOST)
        return connection
    except Exception as e:
        logging.error(f"DB connection error: {e}")
        return None

@st.cache_data
def execute_dynamic_query(connection, query, params, schema):
    """Execute a dynamic SQL query and return results as a pandas DataFrame.
    Args:
        connection: cx_Oracle.Connection
        query: str, SQL query with {schema} placeholder
        params: dict, query parameters
        schema: str, schema name to use in the query
    Returns:
        pd.DataFrame: Query results
    """
    import pandas as pd
    try:
        formatted_query = query.format(schema=schema)
        with connection.cursor() as cursor:
            cursor.execute(formatted_query, params)
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            return pd.DataFrame(rows, columns=columns)
    except Exception as e:
        logging.error(f"Query execution error: {e}")
        return pd.DataFrame()

@st.cache_data
def get_total_count(connection, params, schema):
    """Get total count of records for pagination.
    Args:
        connection: cx_Oracle.Connection
        params: dict, query parameters
        schema: str, schema name to use in the query
    Returns:
        int: Total record count
    """
    count_query = f"""
    SELECT COUNT(*) FROM {schema}.MT_PROCESSING_ERROR
    WHERE SUBSTR(T_BATCH_ID,1,8) = REPLACE(TO_CHAR(:processing_date), '-' )
    AND (:workflow_name IS NULL OR WORKFLOW_NAME = :workflow_name)
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute(count_query, params)
            return cursor.fetchone()[0]
    except Exception as e:
        logging.error(f"Count query error: {e}")
        return 0

@st.cache_data
def get_processing_names(connection, schema):
    """Fetch distinct processing names for dropdown."""
    name_query = f"SELECT DISTINCT PROCESSING_NAME FROM {schema}.MT_PROCESSING_STATE ORDER BY PROCESSING_NAME"
    return execute_dynamic_query(connection, name_query, {}, schema)["PROCESSING_NAME"].tolist()

@st.cache_data
def get_workflow_names(connection, schema):
    """Fetch distinct workflow names for dropdown."""
    name_query = f"SELECT DISTINCT WORKFLOW_NAME FROM {schema}.MT_PROCESSING_ERROR ORDER BY WORKFLOW_NAME"
    return execute_dynamic_query(connection, name_query, {}, schema)["WORKFLOW_NAME"].tolist()

@st.cache_data
def get_paginated_processing_state(connection, params, offset, limit, schema):
    """Fetch paginated processing state records."""
    query = f"""
    SELECT * FROM (
        SELECT
            PROCESSING_NAME AS 'PROCESSING NAME',
            BATCH_ID AS 'BATCH ID',
            PROCESSING_DATE AS 'PROCESSING DATE',
            PROCESSING_STATE AS 'PROCESSING STATE',
            PRC_PERIOD_FLAG AS 'PRC PERIOD FLAG',
            PROCESSING_MODE AS 'PROCESSING MODE',
            SCHEDULING_DATE AS 'SCHEDULING_DATE'
        FROM {schema}.MT_PROCESSING_STATE
        WHERE
            (:processing_name IS NULL OR PROCESSING_NAME = :processing_name)
            AND (:processing_date IS NULL OR PROCESSING_DATE = :processing_date)
        ORDER BY PROCESSING_DATE DESC)
    OFFSET {offset} ROWS FETCH NEXT {limit} ROWS ONLY
    """
    return execute_dynamic_query(connection, query, params, schema)

@st.cache_data
def get_paginated_processing_error(connection, params, offset, limit, schema):
    """Fetch paginated processing error records."""
    query = f"""
    SELECT * FROM (
        SELECT
            T_BATCH_ID as 'Batch ID',
            T_PROCESS_NAME as 'Process Name',
            T_PROCESS_EXEC_ID as 'Process Execution ID',
            TABLE_NAME as 'Table Name',
            WORKFLOW_NAME as 'Workflow Name',
            MAPPING_NAME as 'Mapping Name',
            ERROR_TIMESTAMP as 'Error Timestamp',
            ERROR_MSG as 'Error message'
        FROM {schema}.MT_PROCESSING_ERROR
        WHERE
            SUBSTR(T_BATCH_ID,1,8) = REPLACE(TO_CHAR(:processing_date), '-' )
            AND (:workflow_name IS NULL OR WORKFLOW_NAME = :workflow_name)
        ORDER BY ERROR_TIMESTAMP DESC)
    OFFSET {offset} ROWS FETCH NEXT {limit} ROWS ONLY
    """
    return execute_dynamic_query(connection, query, params, schema)

# Add more DB utility functions as needed
