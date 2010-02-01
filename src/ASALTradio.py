#!/usr/bin/env python

import pyGPSD.nmea.serial as serial


ser = serial.Serial()
ser.baudrate = 57600
ser.port = 0 


ser.open()

if(ser.isOpen()):
	while(1):
		ser.write("AK")


