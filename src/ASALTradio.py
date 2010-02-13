## @package src.ASALTradio
# Widget that for the ASALT vehicle

import pyGPSD.nmea.serial as serial





class ASALTradio():

    def send(self, str):
       coord1 = "%3.10f" % str[0]
       coord2 = "%3.10f" % str[1]
       if(self.ser.isOpen()):
          self.ser.write(coord1)
          self.ser.write(" ")
          self.ser.write(coord2)
          self.ser.write("\r\n")
	

    def receive(self):
       


	def __init__(self):
		self.ser = serial.Serial()
		self.ser.baudrate = 57600
		self.ser.port = 0 
		self.ser.open()

    
    

