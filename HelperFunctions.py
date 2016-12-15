import urllib2
import re
from dateutil.parser import parse
from bs4 import BeautifulSoup
import os
import sys
from datetime import datetime, timedelta


def read_file_to_long(fpath):
    # If our file exists, it'll have a value in it.
    # Use this to determine which tweets to check after
    if os.path.isfile(fpath):
        with open(fpath, 'rb') as file:
            return long(file.read())
    # If it doesn't, set to "None" to avoid conflicts when it is used as an argument.
    else:
        return None


def get_lib_file(filename):
    return os.path.join(sys.path[0], 'lib', filename)


def write_long_to_file(fpath, val):
    with open(fpath, 'wb') as file:
        file.write(str(val))