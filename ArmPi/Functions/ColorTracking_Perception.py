#!/usr/bin/python3
# coding=utf8
import sys
sys.path.append('/home/pi/ArmPi/')
import cv2
import time
import Camera
import threading
from LABConfig import *
from ArmIK.Transform import *
from ArmIK.ArmMoveIK import *
import HiwonderSDK.Board as Board
from CameraCalibration.CalibrationConfig import *

if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)

AK = ArmIK()

import logging
logging.getLogger().setLevel(logging.INFO)


#Set ranges for different colors to track
range_rgb = {
    'red': (0, 0, 255),
    'blue': (255, 0, 0),
    'green': (0, 255, 0),
    'black': (0, 0, 0),
    'white': (255, 255, 255),
}

__target_color = ('red',)
# Set detection color
def setTargetColor(target_color):
    global __target_color

    #print("COLOR", target_color)
    __target_color = target_color
    return (True, ())

# Use opencv to find color contours, and get the contour with the max area
# contours: a list of ocntours to compare
def getAreaMaxContour(contours):
    contour_area_temp = 0
    contour_area_max = 0
    area_max_contour = None

    for c in contours:  # Loop through all contours
        contour_area_temp = math.fabs(cv2.contourArea(c))  # Find contour area
        if contour_area_temp > contour_area_max:
            contour_area_max = contour_area_temp
            if contour_area_temp > 300:  # Make sure that the area is over 300
                area_max_contour = c

    return area_max_contour, contour_area_max  # Returns the largest contour. Note: Terrible variable names

# The angle at which the gripper closes when clamping
#Change this to grip something smaller


# Move to initial position


#Buzzer, turn this off if you find it annoying
def setBuzzer(timer):
    Board.setBuzzer(0)
    Board.setBuzzer(1)
    time.sleep(timer)
    Board.setBuzzer(0)

#Make the board LED turn the color that it is tracking?
def set_rgb(color):
    if color == "red":
        Board.RGB.setPixelColor(0, Board.PixelColor(255, 0, 0))
        Board.RGB.setPixelColor(1, Board.PixelColor(255, 0, 0))
        Board.RGB.show()
    elif color == "green":
        Board.RGB.setPixelColor(0, Board.PixelColor(0, 255, 0))
        Board.RGB.setPixelColor(1, Board.PixelColor(0, 255, 0))
        Board.RGB.show()
    elif color == "blue":
        Board.RGB.setPixelColor(0, Board.PixelColor(0, 0, 255))
        Board.RGB.setPixelColor(1, Board.PixelColor(0, 0, 255))
        Board.RGB.show()
    else:
        Board.RGB.setPixelColor(0, Board.PixelColor(0, 0, 0))
        Board.RGB.setPixelColor(1, Board.PixelColor(0, 0, 0))
        Board.RGB.show()

count = 0
track = False
_stop = False
get_roi = False
center_list = []
first_move = True
__isRunning = False
detect_color = 'None'
action_finish = True
start_pick_up = False
start_count_t1 = True


class Color_Perception():


    def __init__(self):
        logging.info("Initializing Perception")
        self.get_roi = False #Need to default to false I think
        self.center_list = []
        self.count = 0
        self.start_count_t1 = True
        self.start_pick_up = False
        self.color_list = []
        self.last_x, self.last_y = 0, 0
        self.draw_color = range_rgb["black"]
        self.detect_color = "None"
        self.world_X = 0
        self.world_Y = 0
        self.rotation_angle = 0
        #List of variables to put into buses: start_pick_up,action_finish

    def start(self):
        logging.info("Starting Perception")
        self.isrunning = True
        #Add reset here

    def stop(self):
        logging.info("Stopping Perception")
        self.isrunning = False
        self.stop = True


    def reset(self):
        self.count = 0
        self.stop = False
        self.track = False
        self.get_roi = False
        self.center_list = []
        self.color_list = []
        #first_move = True
        #__target_color = ()
        #detect_color = 'None'
        
        #The problem children
        self.action_finish = True
        self.start_pick_up = False
        
        self.start_count_t1 = True

    def get_image(self,img):
        self.img_copy = img.copy()

    def resize_image(self):
        img_h, img_w = self.img_copy.shape[:2]
        cv2.line(self.img_copy, (0, int(img_h / 2)), (img_w, int(img_h / 2)), (0, 0, 200), 1)
        cv2.line(self.img_copy, (int(img_w / 2), 0), (int(img_w / 2), img_h), (0, 0, 200), 1)
        #If not isrunning, do nothing
        if not self.isrunning:
            return self.img_copy
        self.frame_resize = cv2.resize(self.img_copy, size, interpolation=cv2.INTER_NEAREST)
    
    
    def gaussianBlur(self):
        self.frame_gb = cv2.GaussianBlur(self.frame_resize, (11, 11), 11)
        

    def LAB_convert(self):
        if self.get_roi and not start_pick_up:
            self.get_roi = False
            self.frame_gb = getMaskROI(self.frame_gb, self.roi, size)   #No idea where this function comes from but oh well 
    
        self.frame_lab = cv2.cvtColor(self.frame_gb, cv2.COLOR_BGR2LAB)  # Convert image to LAB space
        self.color_area_max = None
        self.max_area = 0
        self.areaMaxContour_max = 0

    
    def image_contours(self,__target_color):
        
        if not self.start_pick_up: #If we are no picking up an object
            for i in color_range: #No idea where this variables comes from
                if i in __target_color:
                    detect_color = i
                    #frame_mask = cv2.inRange(self.frame_lab, color_range[detect_color][0], color_range[detect_color][1])  #Perform bit operations on the original image and mask
                    #opened = cv2.morphologyEx(frame_mask, cv2.MORPH_OPEN, np.ones((6, 6), np.uint8))  # Open operation
                    #closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, np.ones((6, 6), np.uint8))  # closed operation
                    #contours = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2]  # Find the contours
                    
                    frame_mask = cv2.inRange(self.frame_lab, color_range[i][0], color_range[i][1])  #对原图像和掩模进行位运算
                    opened = cv2.morphologyEx(frame_mask, cv2.MORPH_OPEN, np.ones((6,6),np.uint8))  #开运算
                    closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, np.ones((6,6),np.uint8)) #闭运算
                    contours = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2]  #找出轮廓

                    self.areaMaxContour, self.area_max = getAreaMaxContour(contours)  # Get max area contour
                    
                    if self.areaMaxContour is not None:
                        if self.area_max > self.max_area: #找最大面积
                            self.max_area = self.area_max
                            self.color_area_max = i
                            self.areaMaxContour_max = self.areaMaxContour


    def get_area_location(self):
        if not self.start_pick_up: #If we are no picking up an object    
            if self.max_area > 2500:  # If area over a threshold, then found the max area
                self.rect = cv2.minAreaRect(self.areaMaxContour_max)
                box = np.int0(cv2.boxPoints(self.rect))

                self.roi = getROI(box) #get roi area
                self.get_roi = True

                img_centerx, img_centery = getCenter(self.rect, self.roi, size, square_length)  # Get the center coordinates of the wooden block
                self.world_x, self.world_y = convertCoordinate(img_centerx, img_centery, size) #Convert to real world coordinates
                
                
                cv2.drawContours(self.img_copy, [box], -1, range_rgb[self.color_area_max], 2)
                cv2.putText(self.img_copy, '(' + str(self.world_x) + ',' + str(self.world_y) + ')', (min(box[0, 0], box[2, 0]), box[2, 1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, range_rgb[self.color_area_max], 1) #Draw center point
                self.distance = math.sqrt(pow(self.world_x - self.last_x, 2) + pow(self.world_y - self.last_y, 2)) #Compare distance to last coordinates to decided whether or not to move
                self.last_x, self.last_y = self.world_x, self.world_y
                track = True
                if not start_pick_up:
                    if self.color_area_max == 'red':  #红色最大
                        color = 1
                    elif self.color_area_max == 'green':  #绿色最大
                        color = 2
                    elif self.color_area_max == 'blue':  #蓝色最大
                        color = 3
                    else:
                        color = 0
                    self.color_list.append(color)
                    #logging.info(color)
            else:
                track = False
            return track
    
    def CUMULATIVE_JUDGEMENT(self,start_pick_up):
        self.start_pick_up = start_pick_up
        if not self.start_pick_up: #If we are no picking up an object        
            if self.max_area>2500:
                if self.distance < 0.5:
                    self.center_list.extend((self.world_x, self.world_y))
                    self.count += 1
                    if self.start_count_t1:
                        self.start_count_t1 = False
                        self.t1 = time.time()
                    if time.time() - self.t1 > 1:
                        self.rotation_angle = self.rect[2] #Need to return this
                        self.start_count_t1 = True
                        self.world_X, self.world_Y = np.mean(np.array(self.center_list).reshape(self.count, 2), axis=0)
                        self.count = 0
                        self.center_list = []
                        self.start_pick_up = True
                        #logging.info("Hoi")
                else:
                    self.t1 = time.time()
                    self.start_count_t1 = True
                    self.count = 0
                    self.center_list = []

                if len(self.color_list) == 3:  #多次判断
                    # 取平均值
                    color = int(round(np.mean(np.array(self.color_list))))
                    #logging.info(color)
                    self.color_list = []
                    if color == 1:
                        self.detect_color = 'red'
                        self.draw_color = range_rgb["red"]
                    elif color == 2:
                        self.detect_color = 'green'
                        self.draw_color = range_rgb["green"]
                    elif color == 3:
                        self.detect_color = 'blue'
                        self.draw_color = range_rgb["blue"]
                    else:
                        self.detect_color = 'None'
                        self.draw_color = range_rgb["black"]
            else:
                
                self.draw_color = (0, 0, 0)
                self.detect_color = "None"
        
        logging.info(self.detect_color)  
        logging.info(self.start_pick_up) 
        logging.info(self.start_count_t1) 
        cv2.putText(self.img_copy, "Color: " + self.detect_color, (10, self.img_copy.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.65, self.draw_color, 2)
        
        
        #Need to return worldx, worldy, and rotation angle for now, and get info on start pick up for later use
        return self.detect_color,self.start_pick_up,self.world_X,self.world_Y,self.rotation_angle #Have to return this for now?

class Color_Movement():

    def __init__(self):
        self.coordinate = {
            'red':   (-15 + 0.5, 12 - 0.5, 1.5),
            'green': (-15 + 0.5, 6 - 0.5,  1.5),
            'blue':  (-15 + 0.5, 0 - 0.5,  1.5),
        }

        self.servo1 = 500
        self.__isRunning = True
        self._stop = False



    def initMove(self):
        Board.setBusServoPulse(1, self.servo1 - 50, 300)
        Board.setBusServoPulse(2, 500, 500)
        AK.setPitchRangeMoving((0, 10, 10), -30, -30, -90, 1500)

    def move(self,detect_color,start_pick_up,world_X,world_Y,rotation_angle):
        
        if detect_color != 'None' and start_pick_up:  #如果检测到方块没有移动一段时间后，开始夹取
            #移到目标位置，高度6cm, 通过返回的结果判断是否能到达指定位置
            #如果不给出运行时间参数，则自动计算，并通过结果返回
            set_rgb(detect_color)
            #setBuzzer(0.1)
            result = AK.setPitchRangeMoving((world_X, world_Y, 7), -90, -90, 0)  
            if result == False:
                unreachable = True
            else:
                unreachable = False
                time.sleep(result[2]/1000) #如果可以到达指定位置，则获取运行时间

                if  self.__isRunning:
                    servo2_angle = getAngle(world_X, world_Y, rotation_angle) #计算夹持器需要旋转的角度
                    Board.setBusServoPulse(1, self.servo1 - 280, 500)  # 爪子张开
                    Board.setBusServoPulse(2, servo2_angle, 500)
                    time.sleep(0.5)
                
                if  self.__isRunning:
                    AK.setPitchRangeMoving((world_X, world_Y, 1.5), -90, -90, 0, 1000)
                    time.sleep(1.5)

                if  self.__isRunning:
                    Board.setBusServoPulse(1, self.servo1, 500)  #夹持器闭合
                    time.sleep(0.8)

                if  self.__isRunning:
                    
                    Board.setBusServoPulse(2, 500, 500)
                    AK.setPitchRangeMoving((world_X, world_Y, 12), -90, -90, 0, 1000)  #机械臂抬起
                    time.sleep(1)

                if  self.__isRunning:
                    
                    result = AK.setPitchRangeMoving((self.coordinate[detect_color][0], self.coordinate[detect_color][1], 12), -90, -90, 0)   
                    time.sleep(result[2]/1000)
                
                if  self.__isRunning:
                                       
                    servo2_angle = getAngle(self.coordinate[detect_color][0], self.coordinate[detect_color][1], -90)
                    Board.setBusServoPulse(2, servo2_angle, 500)
                    time.sleep(0.5)

                if  self.__isRunning:
                    
                    AK.setPitchRangeMoving((self.coordinate[detect_color][0], self.coordinate[detect_color][1], self.coordinate[detect_color][2] + 3), -90, -90, 0, 500)
                    time.sleep(0.5)
                
                if  self.__isRunning:
                                        
                    AK.setPitchRangeMoving((self.coordinate[detect_color]), -90, -90, 0, 1000)
                    time.sleep(0.8)

                if  self.__isRunning:
                    
                    Board.setBusServoPulse(1, self.servo1 - 200, 500)  # 爪子张开  ，放下物体
                    time.sleep(0.8)

                if  self.__isRunning:
                    
                    AK.setPitchRangeMoving((self.coordinate[detect_color][0], self.coordinate[detect_color][1], 12), -90, -90, 0, 800)
                    time.sleep(0.8)

                self.initMove()  # 回到初始位置
                time.sleep(1.5)

                detect_color = 'None'
                get_roi = False
                start_pick_up = False
                set_rgb(detect_color)
        else:
            if _stop:
                self._stop = False
                Board.setBusServoPulse(1, self.servo1 - 70, 300)
                time.sleep(0.5)
                Board.setBusServoPulse(2, 500, 500)
                AK.setPitchRangeMoving((0, 10, 10), -30, -30, -90, 1500)
                time.sleep(1.5)
            time.sleep(0.01)
        return start_pick_up

if __name__ == '__main__':
    init()
    start()
    __target_color = ('red', )
    my_camera = Camera.Camera()
    my_camera.camera_open()
    while True:
        img = my_camera.frame
        if img is not None:
            frame = img.copy()
            Frame = run(frame)           
            cv2.imshow('Frame', Frame)
            key = cv2.waitKey(1)
            if key == 27:
                break
    my_camera.camera_close()
    cv2.destroyAllWindows()
