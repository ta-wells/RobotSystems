
import logging
from logdecorator import log_on_start, log_on_end, log_on_error
from picarx_improved import Picarx
import atexit
import time

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
    
class Interpreter():

    def __init__(self,sensitivity=1,polarity=1):
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

        Left = Reading[0]
        Middle = Reading[1]
        Right = Reading[2]

        edgeleft = Left-Middle #Difference between left reading and middle
        edgeright = Right-Middle #Difference between right and middle
        edgehigh = Left-Right

        threshold = self.sensitivity #Set threshold based on sensitivity value
        
        large_const = 1/4000 #Constant used to scale large edge
        med_const = 1/2000 #Constant use for off by a medium amount
        close_const = 1/100 #Constant used for very close

        #TODO: Before moving on we need to adjust using the polarity setting 

        if abs(edgeleft)>threshold or abs(edgeright)>threshold or abs(edgehigh)>threshold:
            #If one edge is over the threshold, we know there is an edge somewhere
            if abs(edgehigh)>threshold:
                #If the extremes are over, we know that we are far off
                Distance = self.sensitivity*edgehigh*large_const #built in lef tor right logic
                
            else:
                #Otherwise we are close
                if edgeright<threshold:
                    Distance = self.sensitivity*edgeright*med_const
                else:
                    Distance = self.sensitivity*edgeleft*med_const*1
                #Add logic for left or right
        else:
            #Otherwise we are close to lined up
            #Add logic for left or right based on average close reading maybe
            Distance = self.sensitivity*edgeleft*close_const #Left or right logic built in
            
        return Distance


    def control(self,Distance,kp=.1,target = 0,sat=25):

        #Lets implement a simple proportional controller for now
        err = target-Distance
        angle_set = target*kp
        #Saturate, though technically this is done for us
        if angle_set>25:
            angle_set=25
        if angle_set <-25:
            angle_set = -25

        return angle_set




if __name__=='__main__':

    atexit.register(px.stop)


    sn = Sensor()
    int = Interpreter()
    
    while True:

        #Read Grayscale module, comment out list for sim
        Reading = sn.read()
        #Reading = [2571,3085,3599]

        logging.debug("Got Reading:")
        logging.debug(Reading) 
        Dist = int.process(Reading)
        logging.debug("Got Dist:")
        logging.debug(Dist) 
        time.sleep(.01)

