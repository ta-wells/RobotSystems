import logging
from logdecorator import log_on_start, log_on_end, log_on_error
from picarx_improved import Picarx
import atexit

from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2


logging.getLogger().setLevel(logging.DEBUG)


#Code from https://pyimagesearch.com/2015/03/30/accessing-the-raspberry-pi-camera-with-opencv-and-python/
camera = PiCamera()
rawCapture = PiRGBArray(camera)
time.sleep(.1)
px = Picarx()


class Camera():
     """
    Camera class for line following
    """
     def __init__(self):
        pass
     
     def get_image(self):
         #Get an image from the Picam
         camera.capture(rawCapture, format="bgr")
         logging.debug("Got Image:")
         return rawCapture.array
     


if __name__=='__main__':

    atexit.register(px.stop)
    cm = Camera()
    
    while True:
        cm.get_image()