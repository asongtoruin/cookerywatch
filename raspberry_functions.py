import blinkt
from picamera import PiCamera
from time import sleep
from datetime import datetime


def initialise_lights():
    blinkt.clear()
    blinkt.set_brightness(0.2)
    change_light(0, 102, 255, 102)


def change_light(pixel, r, g, b):
    blinkt.set_pixel(pixel % 8, r % 256, g % 256, b % 256)
    blinkt.show()


def take_photo():
    camera = PiCamera()
    camera.start_preview()
    change_light(1, 255, 153, 51)
    sleep(5)
    output_name = '{}.jpg'.format(datetime.strftime(datetime.now(), '%Y%m%d_%H%M%S'))
    nice_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    camera.annotate_text = nice_time
    camera.capture(output_name)
    change_light(1, 0, 0, 0)
    return output_name, nice_time


if __name__ == '__main__':
    initialise_lights()
    take_photo()
