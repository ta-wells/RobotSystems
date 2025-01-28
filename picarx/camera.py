import logging
from logdecorator import log_on_start, log_on_end, log_on_error
from picarx_improved import Picarx
import atexit

from picamera2 import Picamera2, MappedArray,Preview
import time
import cv2


logging.getLogger().setLevel(logging.DEBUG)


px = Picarx()
cam = Picamera2()
camera_config = picam2.create_still_configuration(main={"size": (1920, 1080)}, lores={"size": (640, 480)}, display="lores")
cam.configure(camera_config)
cam.start_preview(Preview.QTGL)
cam.start()
time.sleep(2)



class Camera():
    """
    Camera class for line following
    """
    def __init__(self):
        pass


    def get_image(self):
        #Get an image from the Picam
        cam.capture_file("test.jpg")
        logging.debug("Got Image")
        #return none 
     


if __name__=='__main__':

    atexit.register(px.stop)
    cm = Camera()
    
    while True:
        cm.get_image()