## @file mapGPS.py
# GPS Support

import os
import time

try:
    import gps
    available = True
except ImportError:
    available = False 

class GPS:
    def __init__(self):
        # Open binding to GPS daemon
        self.gps_session = gps.gps()

    ## Get position from GPS
    def get_position(self):
        # Make new reading from GPS device
        self.gps_session.query('admosy')
		
        print self.gps_session.fix.latitude

