#!/usr/bin/env python3
"""
BigQuery helper utilities
Requires: google-cloud-bigquery and GOOGLE_APPLICATION_CREDENTIALS env var (service account JSON)
"""
from google.cloud import bigquery
import logging
from typing import Optional
import pandas as pd

logger = logging.getLogger(__name__)


def load_dataframe_to_bq(df: pd.DataFrame, table_id: str, if_exists: str = 'append') -> int:
    """Load a pandas DataFrame into BigQuery table

    Args:
        df: DataFrame to load
        table_id: target table id in format `project.dataset.table`
        if_exists: 'append' or 'replace'

    Returns:
        number of rows loaded
    """
    client = bigquery.Client()

    job_config = bigquery.LoadJobConfig()
    if if_exists == 'replace':
        job_config.write_disposition = bigquery.WriteDisposition.WRITE_TRUNCATE
    else:
        job_config.write_disposition = bigquery.WriteDisposition.WRITE_APPEND

    job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
    result = job.result()  # wait for job to finish
    logger.info(f"Loaded {result.output_rows} rows into {table_id}")
    return int(result.output_rows)


def run_query(query: str):
    client = bigquery.Client()
    query_job = client.query(query)
    result = query_job.result()
    rows = [dict(row) for row in result]
    return rows
