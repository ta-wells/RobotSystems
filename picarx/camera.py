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
    
    def process_photo(im,current):
        #Code from https://einsteiniumstudios.com/beaglebone-opencv-line-following-robot.html
        
        # Convert to grayscale
        gray = cv2.cvtColor(current, cv2.COLOR_BGR2GRAY)
        # Gaussian blur
        blur = cv2.GaussianBlur(gray,(5,5),0)
        # Color thresholding

        ret,thresh = cv2.threshold(blur,60,255,cv2.THRESH_BINARY_INV)

        # Find the contours of the frame

        contours,hierarchy = cv2.findContours(thresh.copy(), 1, cv2.CHAIN_APPROX_NONE)

        # Find the biggest contour (if detected)
        if len(contours) > 0:
            c = max(contours, key=cv2.contourArea)
            M = cv2.moments(c)

            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])

    
            cv2.line(current,(cx,0),(cx,720),(255,0,0),1)
            cv2.line(current,(0,cy),(1280,cy),(255,0,0),1)


            cv2.drawContours(current, contours, -1, (0,255,0), 1)

            if cx >= 120:
                logging.info("Turn Left")

            if cx < 120 and cx > 50:
                logging.info("On Track")

            if cx <= 50:
                logging.info("Turn Right")

        else:

            logging.info("I don't see the line")
    
    
  
        



if __name__=='__main__':

    atexit.register(px.stop)
    cam = Camera()
    
    
    last_turn = 0
    last_angle = 0


    while True:
        current = cam.take_photo()
        cam.process_photo(current)
        time.sleep(1)

