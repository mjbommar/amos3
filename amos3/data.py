"""The amos3.data module provides a high-level interface to load image data and create datasets from AMOS."""

# Imports
import copy
import json
import multiprocessing
import os

# Packages
from zipfile import BadZipFile

import numpy.random

# Project imports
from amos3.client import get_camera_list, get_camera_info, get_camera_zip, get_zip_url


def build_camera_database(num_cameras=None):
    """
    Build camera metadata database, optionally using a random subset of all.
    :param num_cameras: optional, number of cameras to randomly sample
    :return: list, list of dictionaries containing camera info
    """
    # Get camera list
    camera_list = [c[0] for c in get_camera_list()]

    # Subset if requested
    if num_cameras is not None:
        camera_list = numpy.random.choice(camera_list, num_cameras)

    # Create dataset by iterating through IDs and querying
    camera_data = []
    for camera_id in camera_list:
        try:
            camera_data.append(get_camera_info(camera_id))
        except ValueError as e:
            print("Unable to retrieve camera {0}: {1}".format(camera_id, e))

    return camera_data


def build_camera_image_database(camera_id, start_date=None, end_date=None, output_path="data", skip_existing=True):
    """
    Build an image database for a single camera given start and end dates.
    :param camera_id: int, camera ID to retrieve
    :param start_date:, datetime.datetime, start date to pull year/month
    :param end_date:, datetime.datetime, end date to pull year/month
    :param output_path:  str, path to store images/json
    :param skip_existing:  bool, whether to skip existing camera IDs or update
    :return:
    """
    # Get info
    camera_info = get_camera_info(camera_id)
    camera_output_path = os.path.join(output_path, str(camera_id))
    if not os.path.exists(camera_output_path):
        os.makedirs(camera_output_path)
    else:
        # Skip camera ID if already exists
        if skip_existing:
            return True

    # Save info as JSON
    with open(os.path.join(camera_output_path, "info.json"), "w") as json_output_file:
        json_camera_info = copy.copy(camera_info)
        json_camera_info["date_added"] = json_camera_info["date_added"].isoformat() \
            if json_camera_info["date_added"] is not None else None
        json_camera_info["last_capture"] = json_camera_info["last_capture"].isoformat() \
            if json_camera_info["last_capture"] is not None else None
        json.dump(json_camera_info, json_output_file)

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
                    camera_zip.extractall(path=camera_output_path)
                else:
                    print("ZIP contents for cameraID={0}, year={1}, month={2} is malformed: {3}"
                          .format(camera_id, year, month, get_zip_url(camera_id, year, month)))
                    continue
            except BadZipFile as e:
                print("ZIP contents for cameraID={0}, year={1}, month={2} is malformed: {3}"
                      .format(camera_id, year, month, get_zip_url(camera_id, year, month)))
                continue

    return True


def build_image_database(camera_id_list, start_date=None, end_date=None, output_path="data", skip_existing=True,
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
    if not os.path.exists(output_path):
        os.makedirs(output_path)

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
