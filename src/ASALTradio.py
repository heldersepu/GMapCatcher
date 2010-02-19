## @package src.ASALTradio
# Widget that for the ASALT vehicle

import pyGPSD.nmea.serial as serial
import time




class ASALTradio():

    def send(self, data, type):
       start_char = struct.pack(c,\xAA)
       switch(type){
           case '1':
              print "send coordinate type"
              size = data[1]
              self.ser.write(start_char)
       	      self.ser.write(struct.pack(c,'1'))
       	      self.ser.write(struct.pack(c,data[0]))
       	      self.ser.write(struct.pack(c,size))
       	      for coord in data[2:size+2]:
       	          self.ser.write(struct.pack(d,coord[0]))
       	          self.ser.write(struct.pack(d,coord[1]))
       	          self.ser.write(struct.pack(I,coord[2]))
       	          time.sleep(0.1)
       	          
       	   case '2':	      
       	      self.ser.write(start_char)
       	      self.ser.write(struct.pack(c,'2'))
       	   default:
       	      print "ASALTRadio send: invalid type"
       }
    
    
    
       coord1 = "%3.10f" % data[0]
       coord2 = "%3.10f" % data[1]
       if(self.ser.isOpen()):
          self.ser.write(coord1)
          self.ser.write(" ")
          self.ser.write(coord2)
          self.ser.write("\r\n")
	

    def receive(self):
       

    def query(self):
        send(NULL, '2')


    def __init__(self):
	self.ser = serial.Serial()
	self.ser.baudrate = 19200
	self.ser.port = 0 
	self.ser.open()

    
    

