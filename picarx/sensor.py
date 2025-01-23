
import logging
from logdecorator import log_on_start, log_on_end, log_on_error
from picarx_improved import Picarx

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

    def __init__(self,sensitivity=1000,polarity=1):
        self.sensitivity = sensitivity
        self.polarity = polarity

    def process(self,Reading):
        #Identify if there is a sharp or not sharp change

        #Use edge location and sign to determine left or right and centered or not centered

        #Make robust to different lighting conditions, option to target darker or lighter
        #Bruh

        #Might need to calibrate this first, we will see

        #Start by finding edges, directionality may need to be changed later
        Left = Reading[0]
        Middle = Reading[1]
        Right = Reading[2]

        edgeleft = Left-Middle #Difference between left reading and middle
        edgeright = Right-Middle #Difference between right and middle
        edgehigh = Left-Right

        threshold = self.sensitivity #Set threshold based on sensitivity value
        
        #TODO: Before moving on we need to adjust using the polarity setting 

        if abs(edgeleft)>threshold or abs(edgeright)>threshold or abs(edgehigh)>threshold:
            #If one edge is over the threshold, we know there is an edge somewhere
            if abs(edgehigh)>threshold:
                #If the extremes are over, we know that we are far off
                Distance = 1000
                #Add logic for left or right
            else:
                #Otherwise we are close
                Distance = 10
                #Add logic for left or right
        else:
            #Otherwise we are close to lined up
            #Add logic for left or right based on average close reading maybe
            pass




if __name__=='__main__':

    sn = Sensor()
    int = Interpreter()
    
    #Read Grayscale module, comment out list for sim
    
    #Reading = sn.read()
    Reading = [2571,3085,3599]


    logging.debug(Reading) 
    int.process(Reading)
