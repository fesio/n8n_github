#!/usr/bin/env python3
"""
Google Cloud Storage helper utilities
Requires: google-cloud-storage and GOOGLE_APPLICATION_CREDENTIALS env var (service account JSON)
"""
from google.cloud import storage
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def upload_file_to_gcs(bucket_name: str, source_file_path: str, dest_blob_name: Optional[str] = None) -> str:
    """Upload a local file to GCS and return the gs:// path

    Args:
        bucket_name: name of the GCS bucket
        source_file_path: local file path
        dest_blob_name: destination blob name in bucket (defaults to basename of source)

    Returns:
        gs://bucket_name/blob_name
    """
    if dest_blob_name is None:
        dest_blob_name = os.path.basename(source_file_path)

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(dest_blob_name)

    blob.upload_from_filename(source_file_path)
    gs_path = f"gs://{bucket_name}/{dest_blob_name}"
    logger.info(f"Uploaded {source_file_path} -> {gs_path}")
    return gs_path


def download_blob_to_file(bucket_name: str, blob_name: str, destination_file_path: str) -> None:
    """Download a blob from GCS to a local file"""
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.download_to_filename(destination_file_path)
    logger.info(f"Downloaded gs://{bucket_name}/{blob_name} -> {destination_file_path}")
