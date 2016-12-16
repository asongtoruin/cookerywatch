import blinkt
from picamera import PiCamera
from time import sleep
from datetime import datetime

def initialise_lights():
    blinkt.clear()
    blinkt.set_brightness(0.1)
    change_light(0, 102, 255, 102)


def change_light(pixel, r, g, b):
    blinkt.set_pixel(pixel % 8, r % 256, g % 256, b % 256)

def take_photo():
    camera = PiCamera()
    camera.start_preview()
    change_light(1, 255, 153, 51)
    sleep(5)
    output_name = '{}.jpg'.format(datetime.strftime(datetime.now(), '%Y%m%d_%H%M%S'))
    camera.capture(output_name)
    return output_name


if __name__ == '__main__':
    print datetime.strftime(datetime.now(), '%Y%m%d_%H%M%S')

