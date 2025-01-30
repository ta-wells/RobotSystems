
import logging
from logdecorator import log_on_start, log_on_end, log_on_error
from picarx_improved import Picarx
import atexit
import time

from bus_structure import Bus_Structure

import concurrent.futures

logging.getLogger().setLevel(logging.DEBUG)

px = Picarx()



class Sensor():
    """
    Sensor class for line following
    """
    
    def __init__(self):
        pass
        
        
    def read(self):
        logging.debug("Got data")    
        return px.grayscale.read()
    

    def read_producer(self,Reading_Bus_class,delay):
        #producer function that writes grayscale data
        while True:
            Reading_Bus_class.write(px.grayscale.read())
            logging.info("Got data") 
            time.sleep(delay)
    
class Interpreter():

    def __init__(self,sensitivity=200,polarity=1):
        self.sensitivity = sensitivity
        self.polarity = polarity

    def process(self,Reading):
        #Identify if there is a sharp or not sharp change

        #Use edge location and sign to determine left or right and centered or not centered

        #Make robust to different lighting conditions, option to target darker or lighter
        #Bruh

        #Might need to calibrate this first, we will see

        #Start by finding edges, directionality may need to be changed later


        #Positive values should be to the left

        #Low numbers mean black, so negative readings mean the thing is to the left

        Left = Reading[0]-50
        Middle = Reading[1]-180
        Right = Reading[2]

        edgeleft = Left-Middle #Difference between left reading and middle
        edgeright = Right-Middle #Difference between right and middle
        edgehigh = Left-Right

        threshold = self.sensitivity #Set threshold based on sensitivity value
        
        large_const = 1/2000 #Constant used to scale large edge
        med_const = 1/2000 #Constant use for off by a medium amount
        close_const = 1/1000 #Constant used for very close

        #TODO: Before moving on we need to adjust using the polarity setting 

        
        if abs(edgehigh)>threshold:
            #If the extremes are over, we know that we are far off
            Distance = edgehigh*large_const*-1 #built in lef tor right logic
                
        else:
           
            Distance = edgeleft*med_const*-1
            #Add logic for left or right
       
            
        return Distance

    def process_consumer_producer(self,Reading_Bus_class,Distance_Bus_Class,delay):
        #Consumer-producer function for reading grayscale sensor and publishing distance

        while True:
            #get reading from bus
            Reading = Reading_Bus_class.read()

            Left = Reading[0]-50
            Middle = Reading[1]-180
            Right = Reading[2]

            edgeleft = Left-Middle #Difference between left reading and middle
            edgeright = Right-Middle #Difference between right and middle
            edgehigh = Left-Right

            threshold = self.sensitivity #Set threshold based on sensitivity value
            
            large_const = 1/2000 #Constant used to scale large edge
            med_const = 1/2000 #Constant use for off by a medium amount
            close_const = 1/1000 #Constant used for very close
            if abs(edgehigh)>threshold:
            #If the extremes are over, we know that we are far off
                Distance = edgehigh*large_const*-1 #built in lef tor right logic
                
            else:
            
                Distance = edgeleft*med_const*-1
                #Add logic for left or right

            Distance_Bus_Class.write(Distance)
            time.sleep(delay)
            

class Control():

    def __init__(self,kp=60,target = 0,sat=25):
        self.kp = kp
        self.sat = sat
        self.target = target
    
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

    def proportional_control_consumer_producer(self,Distance_Bus_Class,Angle_Bus_Class,delay):
        #Consumer-producer function for reading Distance sensor and publishing Angle based on P-control
        while True:
            distance = Distance_Bus_Class.read()

            #Lets implement a simple proportional controller for now
            err = self.target-distance
            angle_set = err*self.kp
            #Saturate, though technically this is done for us
            if angle_set>25:
                angle_set=25
            if angle_set <-25:
                angle_set = -25
            logging.info("Got Angle") 
            logging.info(angle_set)
            Angle_Bus_Class.write(angle_set)
            time.sleep(delay)




# if __name__=='__main__':

#     atexit.register(px.stop)


#     sn = Sensor()
#     int = Interpreter()
#     con = Control()
#     time.sleep(1)
#     while True:
        
#         #Read Grayscale module, comment out list for sim
#         Reading = sn.read()
#         #Reading = [2571,3085,3599]

#         logging.debug("Got Reading:")
#         logging.debug(Reading) 
#         Dist = int.process(Reading)
#         logging.debug("Got Dist:")
#         logging.debug(Dist) 

#         Angle = con.proportional_control(Dist)
#         logging.debug("Got Angle:")
#         logging.debug(Angle)
        
#         #TODO: Put these back in when following a line
#         px.set_dir_servo_angle(Angle)
#         px.forward(40)

#         time.sleep(.05)

if __name__=='__main__':

    atexit.register(px.stop)
    sn = Sensor()
    int = Interpreter()
    con = Control()

    #Set up bus
    Reading_bus_class = Bus_Structure()
    Distance_bus_class = Bus_Structure()
    Angle_bus_class = Bus_Structure()

    #Set up delay, this is a bit confusing
    sn_delay = .05
    int_delay = .05
    con_delay = .05
    #Code from lab manual
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        eSensor = executor.submit(sn.read_producer, Reading_bus_class,
            sn_delay)
        eInterpreter = executor.submit(int.process_consumer_producer,
            Reading_bus_class, Distance_bus_class,int_delay)
        eController = executor.submit(con.proportional_control_consumer_producer,
            Distance_bus_class,Angle_bus_class,con_delay)
    eSensor.result()
    

    # while True:
        
    #     px.set_dir_servo_angle(Angle)
    #     px.forward(40)
    #     time.sleep(.05)