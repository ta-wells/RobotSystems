
import logging
from logdecorator import log_on_start, log_on_end, log_on_error


logging.getLogger().setLevel(logging.DEBUG)



from picarx_improved import Picarx

class Sensor():
    """
    Sensor class for line following
    """
    
    def __init__(self):
        self.px = Picarx()
        
        
    def read(self):
        logging.debug("Got data")    
        return self.px.grayscale.read()


if __name__=='__main__':

    sn = Sensor()
    Test = sn.read()
    logging.debug(Test) 
