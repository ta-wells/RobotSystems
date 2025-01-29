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
        self.cx_last = 80
        self.kp = 1/8
        self.target = 0

    def take_photo(self):
        #Code from https://smist08.wordpress.com/tag/vilib/
        _time = time.strftime('%Y-%m-%d-%H-%M-%S',time.localtime(time.time()))
        name = 'photo_%s'%_time
        username = os.getlogin()

        path = f"/home/{username}/Pictures/"
        Vilib.take_photo(name, path)
        #print('photo save as %s%s.jpg'%(path,name))
        self.lastPhoto = self.currentPhoto
        self.currentPhoto = path + name + ".jpg"
        logging.info("Got Photo")
        return self.currentPhoto
    
    def process_photo(self):
        const = 80
        
        #Code from https://einsteiniumstudios.com/beaglebone-opencv-line-following-robot.html
        
        
        # Convert to grayscale
        img = cv2.imread(self.currentPhoto)
        crop_img = img[60:120, 0:160]
        gray = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
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

            try: 
                cx = int(M['m10']/M['m00'])
                cy = int(M['m01']/M['m00'])
            except ZeroDivisionError:
                cx = self.cx_last
                cy = 0

            self.cx_last = cx
    
            cv2.line(crop_img,(cx,0),(cx,720),(255,0,0),1)
            cv2.line(crop_img,(0,cy),(1280,cy),(255,0,0),1)


            cv2.drawContours(crop_img, contours, -1, (0,255,0), 1)

            logging.info(cx)

            if cx >= 100:
                logging.info("Turn Left")

            if cx < 100 and cx > 70:
                logging.info("On Track")
                cx = 0

            if cx <= 70:
                logging.info("Turn Right")

        else:
            cx = self.cx_last
            logging.info("I don't see the line")
            dist = cx - const


        
        return dist
    
  
    def proportional_control(self,distance):
        #Lets implement a simple proportional controller for now
        err = self.target-distance
        angle_set = err*self.kp
        #Saturate, though technically this is done for us
        if angle_set>25:
            angle_set=25
        if angle_set <-25:
            angle_set = -25

        return angle_set



if __name__=='__main__':

    atexit.register(px.stop)
    cam = Camera()
    px.set_cam_tilt_angle(-90)  
    
    last_turn = 0
    last_angle = 0


    while True:
        current = cam.take_photo()
        time.sleep(.1)
        dist = cam.process_photo()
        logging.info("Got Dist:")
        logging.info(dist) 
        angle = cam.proportional_control(dist)
        logging.info("Got Angle:")
        logging.info(angle)
        px.set_dir_servo_angle(angle)
        px.forward(40)
        

