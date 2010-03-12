## @package src.ASALTradio
# Widget that for the ASALT vehicle

import pyGPSD.nmea.serial as serial
import time
import struct



class ASALTradio():    
    def __init__(self):
       	global available2
        self.location = None
    	self.ser = serial.Serial()
    	self.ser.baudrate = 19200
    	self.ser.port = 0 
    	self.ser.timeout = 10
	self.ser.open()
    
    def send(self, data, type):
       start_char = struct.pack(c,"\x55")
       if(type == '1'):
              print "send coordinate type"
              size = data[1]
              self.ser.write(start_char)
       	      self.ser.write(struct.pack(c,'1'))
       	      self.ser.write(struct.pack(c,data[0]))
       	      self.ser.write(struct.pack(c,size))
       	      for coord in data[2:size+2]:
       	          self.ser.write(struct.pack('f',coord[0]))
       	          self.ser.write(struct.pack('f',coord[1]))
       	          self.ser.write(struct.pack('I',coord[2]))
       	          time.sleep(0.1)
       elif(type =='2'):	              
       	      self.ser.write(start_char)
       	      self.ser.write(struct.pack('c','2'))
       else:
       	      print "ASALTRadio send: invalid type"
       
    
    
    
       coord1 = "%3.10f" % data[0]
       coord2 = "%3.10f" % data[1]
       if(self.ser.isOpen()):
          self.ser.write(coord1)
          self.ser.write(" ")
          self.ser.write(coord2)
          self.ser.write("\r\n")


    def send_float(self,coords,loop):
       radio = self.ser
       sf = struct.Struct('f')
       si = struct.Struct('I')
       sc = struct.Struct('c')
       size = si.pack(len(coords.positions))
       type_out = si.pack(1)
       loop_out = si.pack(loop)
       radio.write(type_out)
       radio.write(loop_out)
       radio.write(size)
       for strName in coords.positions.keys():
           coord = coords.positions[strName]
           print coord
           c1 = sf.pack(coord[0])
           c2 = sf.pack(coord[1])
           c3 = si.pack(coord[3])
           radio.write(c1)
           radio.write(c2)
           radio.write(c3)

    def parse_status(self, radio):
    	sf = struct.Struct('f')
     	si = struct.Struct('I')
        lat_in = radio.read(4)
	long_in = radio.read(4)
	heading_in = radio.read(4)
	pitch_in = radio.read(4)
	roll_in = radio.read(4)
	status_in = radio.read(4)
	lat = sf.unpack(lat_in)
	long = sf.unpack(long_in)
	heading = sf.unpack(heading_in)
	status = si.unpack(status_in)
	pitch = sf.unpack(pitch_in)
	roll = sf.unpack(roll_in)
	#print lat," ",long," ",heading," ",status
	status_update = lat[0],long[0],pitch[0],roll[0],heading[0],status[0]
	self.location = lat[0],long[0]
	print self.location
	radio.flushInput()
	return status_update    	


    def receive_status(self):
       
       radio = self.ser
       print "receive"
       #available2 = True
       #for i in range(50000):
           #wait = radio.inWaiting()
           #if(wait):
     	   #	print radio.inWaiting()
       try:
          currtime = time.time();
          while True:
          	#wait for characters to appear in buffer
          	if(radio.inWaiting() > 0):
          		break
          	#timeout after 20 seconds
          	if(time.time() >= currtime + 20):
          		return "Timeout, please query again"
          return self.parse_status(radio)
          #if(radio.inWaiting() != 0):
	  #     result = self.parse_status(radio)
	  #     if(35 < result[0] < 40):
	  #        return result
	  #     else:
	  #     	  return "Error, bad data, please query again"
	  #else:
	  #     time.sleep(2)
	  #     result = self.parse_status(radio)
	  #     if(35 < result[0] < 40):
	  #     	   return result
	  #     else:
	  #         return "Error, bad data, please query again"
	       #return "Timeout Error"
       except OSError:
       #except EOFError:
       	       radio.flushInput()
       	       return "ERROR, please query again"
       
    def query(self):
        sc = struct.Struct('c')
        print "sending query\n"
        radio = self.ser
        radio.write(sc.pack('A'))
	radio.write(sc.pack('A'))
	print "sent\n"


    def get_location(self):
    	return self.location



    
    

