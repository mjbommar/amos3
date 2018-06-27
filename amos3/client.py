"""The amos3.client module provides a direct interface to query AMOS endpoints and retrieve AMOS ZIP data."""

# Imports
import datetime
import urllib.parse

# Packages
import dateutil.parser
import lxml.etree
import requests

# URL constants
BASE_URL = "http://amos.cse.wustl.edu"
PRE_2012_URL = "2012zipfiles"
POST_2012_URL = "zipfiles"

# Return type mapping
INFO_TYPE_MAP = {"id": "int",
                 "latitude": "float",
                 "longitude": "float",
                 "ip_latitude": "float",
                 "ip_longitude": "float",
                 "images_captured": "int",
                 "date_added": "datetime",
                 "last_capture": "datetime",
                 "width": "int",
                 "height": "int",
                 }


def timestamp_to_datetime(timestamp_string):
    """
    Convert a timestamp string to datetime.datetime object.
    :param timestamp_string: timestamp string, e.g., 20160101_000356
    :return: datetime.datetime object
    """
    return datetime.datetime(year=int(timestamp_string[0:4]),
                             month=int(timestamp_string[4:6]),
                             day=int(timestamp_string[6:8]),
                             hour=int(timestamp_string[9:11]),
                             minute=int(timestamp_string[11:13]),
                             second=int(timestamp_string[13:15]),
                             tzinfo=datetime.timezone.utc
                             )


def get_buffer(url):
    """
    Retrieve a buffer from a URL as an in-memory buffer.
    :param url: URL for a given document to request
    :return: bytes, request response
    """
    # Get response
    response = requests.get(url)
    return response.content


def save_buffer(url, file_path):
    """
    Retrieve a buffer form a URL and save to local file path.
    :param url: URL for a given document to request
    :param file_path: path to save contents locally
    :return: bool, status of retrieve and save
    """
    # Retrieve
    buffer = get_buffer(url)

    with open(file_path, "wb") as output_file:
        output_file.write(buffer)
        return True


def get_camera_list():
    """
    Get list of cameras with lat/long position.
    :return: list, list of (camera ID, lat, long)
    """
    # Create list URL and retrieve
    list_url = urllib.parse.urljoin(BASE_URL, "get_cams")
    list_buffer = get_buffer(list_url).decode("utf-8")

    # Parse list URL
    camera_list = []
    p0 = 0
    p1 = list_buffer.find("<br>", p0)

    while p1 != -1:
        # Parse line
        line = list_buffer[p0:p1]
        tokens = line.split()
        camera_id = int(tokens[0][0:-1])
        camera_latitude = float(tokens[1][1:-1])
        camera_longitude = float(tokens[2][0:-1])
        camera_list.append((camera_id, camera_latitude, camera_longitude))

        # Increment head
        p0 = p1 + len("<br>")
        p1 = list_buffer.find("<br>", p0)

    return camera_list


def get_camera_info(camera_id):
    """
    Get camera info from AMOS API.
    :param camera_id: int, camera ID
    :return: dict, camera info returned from /cam_info
    """
    # Create URL and retrieve
    info_url = urllib.parse.urljoin(BASE_URL, "webcam_info?id={0}".format(camera_id))
    info_buffer = get_buffer(info_url)

    # Setup return object and typing
    camera_info = {}

    # Parse from XML to dict
    info_xml_doc = lxml.etree.fromstring(info_buffer)
    camera_element = info_xml_doc.xpath(".//webcam").pop()
    for info_element in list(camera_element):
        if info_element.tag not in INFO_TYPE_MAP:
            camera_info[info_element.tag] = info_element.text
        else:
            if INFO_TYPE_MAP[info_element.tag] == "int":
                camera_info[info_element.tag] = int(info_element.text)
            elif INFO_TYPE_MAP[info_element.tag] == "float":
                try:
                    camera_info[info_element.tag] = float(info_element.text)
                except ValueError as e:
                    camera_info[info_element.tag] = None
            elif INFO_TYPE_MAP[info_element.tag] == "datetime":
                camera_info[info_element.tag] = dateutil.parser.parse(info_element.text)

    # Tokenize tags
    if "tags" in camera_info:
        camera_info["tags"] = [t.strip() for t in camera_info["tags"].split(",") if t.strip()]

    return camera_info


def get_image_by_camera_timestamp(camera_id, timestamp_string):
    """
    Retrieve an image by camera ID and timestamp string.
    :param camera_id: int, camera ID, e.g., 65
    :param timestamp_string: str, timestamp string, e.g., 20160101_163316
    :return: bytes, image contents
    """
    # Create image URL and retrieve
    image_url = urllib.parse.urljoin(BASE_URL, "image/{0}/{1}.jpg".format(camera_id, timestamp_string))
    return get_buffer(image_url)


def get_timestamps_by_camera_month(camera_id, year, month):
    """
    Retrieve a list of timestamps for a given camera/month.
    :param camera_id: int, camera ID, e.g., 65
    :param year: int, year to retrieve, e.g., 2016
    :param month: int, month to retrieve, e.g., 1
    :return: list, list of timestamp IDs, e.g., ["20160101_000356"]
    """
    # Create list URL and retrieve
    list_url = urllib.parse.urljoin(BASE_URL, "month_of_images?camera_id={0}&year={1}&month={2}"
                                    .format(camera_id, year, month))
    list_buffer = get_buffer(list_url)

    # Parse XML doc
    list_xml_doc = lxml.etree.fromstring(list_buffer)
    timestamp_list = []
    for image in list_xml_doc.xpath(".//image"):
        timestamp_list.append(image.text.replace(".jpg", ""))

    return timestamp_list


def save_camera_zip(camera_id, year, month, file_path=None):
    """
    Download a camera ZIP archive.

    :param camera_id: int, camera ID
    :param year: int, year
    :param month: int, month
    :param file_path: str, optional, path to save file
    :return: bool, status of download
    """
    # Setup strings for indexing
    camera_id_string = "{0:08d}".format(camera_id)
    camera_id_last2 = camera_id_string[-2:]
    camera_id_last4 = camera_id_string[-4:]

    # Setup file name
    file_name = "{0:04d}.{1:02d}.zip".format(year, month)
    if file_path is None:
        file_path = "./{0}".format(file_name)

    # Build URL based on year
    if year > 2012:
        zip_url = urllib.parse.urljoin(BASE_URL, "{0}/{1}/{2}/{3}/{4}/{5}".format(POST_2012_URL, year,
                                                                                  camera_id_last2,
                                                                                  camera_id_last4,
                                                                                  camera_id_string,
                                                                                  file_name))
    else:
        # raise NotImplementedError("URL format for pre-2013 is not yet implemented.")
        zip_url = urllib.parse.urljoin(BASE_URL, "{0}/{1}/{2}/{3}/{4}/{5}".format(PRE_2012_URL, year,
                                                                                  camera_id_last2,
                                                                                  camera_id_last4,
                                                                                  camera_id_string,
                                                                                  file_name))

    # Download
    save_buffer(zip_url, file_path)
    return True
