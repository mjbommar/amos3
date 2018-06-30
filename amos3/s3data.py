"""The amos3.s3data module provides a high-level interface to load image data and create datasets from AMOS
that are stored on S3 (Amazon Web Services Simple Storage Service)."""

# Imports
import copy
import json
import multiprocessing
import os
import posixpath
from zipfile import BadZipFile

# Packages
import botocore
import boto3
import numpy.random

# Project imports
from amos3.client import get_camera_list, get_camera_info, get_camera_zip, get_zip_url
from amos3.data import get_camera_info

# Load keys from env
S3_BUCKET = os.getenv("AMOS_S3_BUCKET", "amos-data")
S3_ACCESS_KEY = os.getenv("AMOS_S3_ACCESS_KEY", "")
S3_SECRET_KEY = os.getenv("AMOS_S3_SECRET_KEY", "")


def s3_path_exists(path, client):
    """
    Check if an S3 path exists given client.
    :param path: str, path to query
    :return: bool, true if S3 object exists, else false
    """
    try:
        client.head_object(Bucket=S3_BUCKET, Key=path)
        return True
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            return False
        else:
            return False


def build_camera_image_database(camera_id, start_date=None, end_date=None, output_path="cameras", skip_existing=True):
    """
    Build an image database on S3  for a single camera given start and end dates.
    :param camera_id: int, camera ID to retrieve
    :param start_date:, datetime.datetime, start date to pull year/month
    :param end_date:, datetime.datetime, end date to pull year/month
    :param output_path:  str, path to store images/json like s3://{S3_BUCKET}/path/
    :param skip_existing:  bool, whether to skip existing camera IDs or update
    :return:
    """
    # Create S3 client to re-use
    s3_client = boto3.client('s3', aws_access_key_id=S3_ACCESS_KEY, aws_secret_access_key=S3_SECRET_KEY)

    # Get info
    camera_info = get_camera_info(camera_id)
    camera_output_path = posixpath.join(output_path, str(camera_id), )
    if s3_path_exists(camera_output_path, s3_client):
        # Skip camera ID if already exists
        if skip_existing:
            return True

    # Save info as JSON
    json_camera_info = copy.copy(camera_info)
    json_camera_info["date_added"] = json_camera_info["date_added"].isoformat() \
        if json_camera_info["date_added"] is not None else None
    json_camera_info["last_capture"] = json_camera_info["last_capture"].isoformat() \
        if json_camera_info["last_capture"] is not None else None
    json_camera_buffer = json.dumps(json_camera_info)
    response = s3_client.put_object(Bucket=S3_BUCKET, Key=posixpath.join(camera_output_path, "info.json"),
                                    Body=json_camera_buffer)
    if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
        raise RuntimeError("Unable to upload camera info to S3: response={0}".format(response["ResponseMetadata"]))

    # Get start date
    if start_date is not None and camera_info['date_added'] is not None:
        start_date = max(start_date, camera_info['date_added'])
    elif start_date is None and camera_info['date_added'] is not None:
        start_date = camera_info['date_added']
    else:
        return False

    # Get end date
    if end_date is not None and camera_info['last_capture'] is not None:
        end_date = min(end_date, camera_info['last_capture'])
    elif end_date is None and camera_info['last_capture'] is not None:
        end_date = camera_info['last_capture']
    else:
        return False

    for year in range(start_date.year, end_date.year + 1):
        for month in range(1, 12):
            # skip early month in first year
            if year == start_date.year and month < start_date.month:
                continue

            # skip late month in last year
            if year == end_date.year and month > end_date.month:
                continue

            # retrieve archive and extract all
            try:
                camera_zip = get_camera_zip(camera_id, year, month)
                if camera_zip is not None:
                    for zip_member_name in camera_zip.namelist():
                        image_buffer = camera_zip.read(zip_member_name)
                        response = s3_client.put_object(Bucket=S3_BUCKET,
                                                        Key=posixpath.join(camera_output_path, zip_member_name),
                                                        Body=image_buffer)
                        if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
                            raise RuntimeError(
                                "Unable to upload camera info to S3: response={0}".format(response["ResponseMetadata"]))
                else:
                    print("ZIP contents for cameraID={0}, year={1}, month={2} is malformed: {3}"
                          .format(camera_id, year, month, get_zip_url(camera_id, year, month)))
                    continue
            except BadZipFile as e:
                print("ZIP contents for cameraID={0}, year={1}, month={2} is malformed: {3}"
                      .format(camera_id, year, month, get_zip_url(camera_id, year, month)))
                continue

    return True


def build_image_database(camera_id_list, start_date=None, end_date=None, output_path="cameras", skip_existing=True,
                         workers=1):
    """
    Build an image database given a list of camera IDs, start date, and end date.
    :param camera_id_list: list, list of camera ID integers
    :param start_date:, datetime.datetime, start date to pull year/month
    :param end_date:, datetime.datetime, end date to pull year/month
    :param output_path:  str, path to store images/json
    :param skip_existing:  bool, whether to skip existing camera IDs or update
    :param workers: int, number of worker processes to spawn
    :return: bool, status
    """
    # Check output path

    # Iterate through camera ID list
    if workers == 1:
        for camera_id in camera_id_list:
            build_camera_image_database(camera_id, start_date, end_date, output_path, skip_existing)
    elif workers > 1:
        pool_arguments = [(camera_id, start_date, end_date, output_path, skip_existing) for camera_id in camera_id_list]
        with multiprocessing.Pool(workers) as pool:
            results = pool.starmap(build_camera_image_database, pool_arguments)
    else:
        raise ValueError("workers must be >= 1")

    return True
