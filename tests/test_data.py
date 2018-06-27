# Imports
import os

# Package imports
from nose.tools import assert_true, assert_equal, assert_in

# Project imports
from data import build_image_database, build_camera_database


def test_build_camera_database():
    """
    Test build_camera_database.
    :return:
    """
    camera_list = build_camera_database(num_cameras=10)
    assert_equal(type(camera_list), list)
    assert_equal(len(camera_list), 10)
    assert_equal(type(camera_list[0]), dict)
    assert_in("id", camera_list[0])


def test_build_image_database():
    """
    Test build_image_database.
    :return:
    """
    build_image_database([30815])
    assert_true(os.path.exists("data/30815/20150330_163044.jpg"))
