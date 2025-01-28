import logging
from logdecorator import log_on_start, log_on_end, log_on_error
from picarx_improved import Picarx
import atexit

from picamera2 import Picamera2, MappedArray
import time
import cv2


logging.getLogger().setLevel(logging.DEBUG)


px = Picarx()
cam = Picamera2()
time.sleep(.5)
cam.start()

class Camera():
    """
    Camera class for line following
    """
    def __init__(self):
        pass


    def get_image(self):
        #Get an image from the Picam
        frame = cam.capture_array()
        height, width, _ = frame.shape
        middle = (int(width / 2), int(height / 2))
        logging.debug("Got Image:")
        return frame 
     


if __name__=='__main__':

    atexit.register(px.stop)
    cm = Camera()
    
    while True:
        cm.get_image()