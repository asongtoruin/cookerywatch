import urllib2
import re
from dateutil.parser import parse
#from bs4 import BeautifulSoup
import os
import sys
from datetime import datetime, timedelta
from PIL import Image
from random import randint


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


def colour_block(r, g, b):
    image_size = 200
    im = Image.new('RGBA', (image_size, image_size))

    for x in range(image_size):
        for y in range(image_size):
            im.putpixel((x,y), (r, g, b))
    
    out_name = '{}.jpg'.format('_'.join(map(str, [r, g, b])))
    im.save(out_name)
    return out_name


def colours_from_text(input_text):
    out = re.findall('(\d+)', input_text)
    colours = [0, 0, 0]
    for i,x in enumerate(out[:3]):
        colours[i] = int(x)
    if all(x == 0 for x in colours):
        colours = [randint(0, 255), randint(0, 255), randint(0, 255)]
    return colours
