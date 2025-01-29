import logging
from logdecorator import log_on_start, log_on_end, log_on_error
from picarx_improved import Picarx
import atexit

from vilib import Vilib
import os
import numpy as np

import time
import cv2


MSE_THRESHOLD = 20

logging.getLogger().setLevel(logging.INFO)


Vilib.camera_start(vflip=False,hflip=False)
px = Picarx()
time.sleep(.5)



class Camera():
    """
    Camera class for line following
    """
    def __init__(self):
        self.lastPhoto = ""
        self.currentPhoto = ""

    def take_photo(self):
        #Code from https://smist08.wordpress.com/tag/vilib/
        _time = time.strftime('%Y-%m-%d-%H-%M-%S',time.localtime(time.time()))
        name = 'photo_%s'%_time
        username = os.getlogin()

        path = f"/home/{username}/Pictures/"
        Vilib.take_photo(name, path)
        print('photo save as %s%s.jpg'%(path,name))
        if self.lastPhoto != "":
            os.remove(self.lastPhoto)
        self.lastPhoto = self.currentPhoto
        self.currentPhoto = path + name + ".jpg"
        logging.info("Got Photo")
        return self.currentPhoto
    
    def process_photo(last,current):
        pass
    
    
  
        



if __name__=='__main__':

    atexit.register(px.stop)
    cam = Camera()
    
    
    last_turn = 0
    last_angle = 0


    while True:
        one,two = cam.take_photo()
        time.sleep(1)

