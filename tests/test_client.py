"""The module provides unit test coverage for amos3.client module."""

# Imports
import datetime
import os

# Packages
from nose.tools import assert_equal, assert_greater, assert_true, raises

# Project imports
from client import get_image_by_camera_timestamp, get_timestamps_by_camera_month, timestamp_to_datetime, \
    get_camera_list, get_camera_info, save_camera_zip, get_camera_zip


def test_timestamp_to_datetime():
    """
    Test timestamp_to_datetime basic case.
    :return:
    """
    new_date = timestamp_to_datetime("20160101_000356")
    assert_equal(new_date, datetime.datetime(2016, 1, 1, 0, 3, 56, tzinfo=datetime.timezone.utc))


def test_get_image_by_camera_timestamp():
    """
    Test get_image_by_camera_timestamp basic case.
    :return:
    """
    # Test single image size and type
    image_buffer = get_image_by_camera_timestamp(65, "20160101_000356")
    assert_equal(type(image_buffer), bytes)
    assert_equal(len(image_buffer), 137897)


@raises(ValueError)
def test_get_image_by_camera_timestamp_bad():
    """
    Test get_image_by_camera_timestamp with invalid ID.
    :return:
    """
    # Test single image size and type
    _ = get_image_by_camera_timestamp(0, "ABC123")


def test_get_timestamps_by_camera_month():
    """
    Test get_timestamps_by_camera_month basic case.
    :return:
    """
    # Check number of timestamps for year/month
    l = get_timestamps_by_camera_month(65, 2016, 1)
    assert_equal(len(l), 1367)

    # Check number of timestamps for year/month
    l = get_timestamps_by_camera_month(65, 2018, 1)
    assert_equal(len(l), 0)


def test_get_camera_list():
    """
    Test get_camera_list basic case.
    :return:
    """
    # Check length at least 29K and element size is 3
    l = get_camera_list()
    assert_greater(len(l), 29000)
    assert_equal(type(l[0]), tuple)
    assert_equal(len(l[0]), 3)


def test_get_camera_info():
    """
    Test get_camera_info basic case.
    :return:
    """
    ci = get_camera_info(21804)
    assert_equal(type(ci), dict)
    assert_equal(ci["id"], 21804)
    assert_equal(type(ci["latitude"]), float)
    assert_equal(type(ci["date_added"]), datetime.datetime)


@raises(ValueError)
def test_get_camera_info_bad():
    """
    Test get_camera_info with bad camera ID.
    :return:
    """
    ci = get_camera_info(999999)
    assert_equal(type(ci), dict)


def test_get_camera_zip():
    """
    Test get_camera_zip basic case.
    :return:
    """
    # Download and check path exists for pre-2012
    import zipfile
    zip_object = get_camera_zip(21804, 2002, 2)
    assert_equal(type(zip_object), zipfile.ZipFile)
    assert_equal(len(zip_object.namelist()), 13)


def test_save_camera_zip():
    """
    Test save_camera_zip basic case.
    :return:
    """
    # Download and check path exists for pre-2012
    status = save_camera_zip(21804, 2002, 2)
    assert_true(status)
    assert_true(os.path.exists("2002.02.zip"))
    os.unlink("2002.02.zip")

    # Download and check path exists for post-2012
    status = save_camera_zip(17345, 2017, 3)
    assert_true(status)
    assert_true(os.path.exists("2017.03.zip"))
    os.unlink("2017.03.zip")
