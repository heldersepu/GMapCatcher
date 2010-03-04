# -*- coding: utf-8 -*-
# Example valid nmea sentences
#
# $GPRMC,084047,A,2727.9512,S,15305.3444,E,005.8,161.0,231108,,,A*6A
# $GPGGA,084048,2727.9531,S,15305.3447,E,1,07,02.0,-00001.0,M,039.4,M,,*70
# $GPGSA,A,3,07,08,11,13,17,27,28,,,,,,05.3,02.0,04.8*0E
# $GPGSV,3,1,11,07,48,103,46,08,58,171,47,11,22,075,36,13,26,021,45*72
#

import unittest

from parse import *
from _types import *


class SentenceTestCase(unittest.TestCase):
    def setUp(self):
        self.rmc = Sentence("$GPRMC,084047,A,2727.9512,S,15305.3444,E,005.8,161.0,231108,,,A*6A")
        self.gga = Sentence("$GPGGA,084048,2727.9531,S,15305.3447,E,1,07,02.0,-00001.0,M,039.4,M,,*70")
        self.gsa = Sentence("$GPGSA,A,3,07,08,11,13,17,27,28,,,,,,05.3,02.0,04.8*0E")
        self.gsv = Sentence("$GPGSV,3,1,11,07,48,103,46,08,58,171,47,11,22,075,36,13,26,021,45*72")

    def testPrefix(self):
        "Test for a initial $ symbol"
        self.failUnlessRaises(ParseError, Sentence, 'abc')

    def testChecksum(self):
        "Test checksum calculation"
        self.failUnlessRaises(ParseError, Sentence, "$GPRMC,084047,A,2727.9512,S,15305.3444,E,005.8,161.0,231108,,,A")
        self.failUnlessRaises(CheckSumError, Sentence, "$GPRMC,084047,A,2727.9512,S,15305.3444,E,005.8,161.0,231108,,,A*6B")

    def testCheckSource(self):
        self.failUnlessEqual(self.rmc.source, 'GP')

    def testMessageType(self):
        self.failUnlessEqual(self.rmc.message, 'RMC')

    def testCheckLength(self):
        self.failUnlessEqual(len(self.rmc), 12)

    def testGet(self):
        self.failUnlessEqual(self.rmc[0], "084047")

    def testInt(self):
        self.failUnlessEqual(self.rmc.get_int(0), 84047)
        self.failUnlessEqual(self.rmc.get_int(10, 2), 2)
        self.failUnlessRaises(ParseError, self.rmc.get_int, 1)

    def testFloat(self):
        self.failUnlessEqual(self.rmc.get_float(2), 2727.9512)
        self.failUnlessEqual(self.rmc.get_float(10, 2.0), 2.0)
        self.failUnlessRaises(ParseError, self.rmc.get_float, 1)

    def testVelocity(self):
        self.failUnlessEqual(self.rmc.get_velocity(2), 2727.9512)
        self.failUnlessEqual(self.rmc.get_velocity(10, 2.0), 2.0)
        self.failUnlessRaises(ParseError, self.rmc.get_velocity, 1)


class latitudeTestCase(unittest.TestCase):
    def testEmpty(self):
        self.failUnlessEqual(latitude(), 0.0)

    def testOutOfRange(self):
        self.failUnlessRaises(ValueError, latitude, 91.0)
        self.failUnlessRaises(ValueError, latitude, -91.0)

    def testInvalidType(self):
        self.failUnlessRaises(ValueError, latitude, 91)
        self.failUnlessRaises(ValueError, latitude, "91")

    def testStrPositive(self):
        l = latitude(27 + 27.9487 / 60)
        self.failUnlessEqual(str(l), "27°27'56.922000\"N")

    def testStrNegative(self):
        l = latitude(-(27 + 27.9487 / 60))
        self.failUnlessEqual(str(l), "27°27'56.922000\"S")


class longitudeTestCase(unittest.TestCase):
    def testEmpty(self):
        self.failUnlessEqual(longitude(), 0.0)

    def testOutOfRange(self):
        self.failUnlessRaises(ValueError, longitude, 191.0)
        self.failUnlessRaises(ValueError, longitude, -191.0)

    def testInvalidType(self):
        self.failUnlessRaises(ValueError, longitude, 91)
        self.failUnlessRaises(ValueError, longitude, "91")

    def testStrPositive(self):
        l = longitude(153 + 05.3408 / 60)
        self.failUnlessEqual(str(l), "153°05'20.448000\"E")

    def testStrNegative(self):
        l = longitude(-(153 + 05.3408 / 60))
        self.failUnlessEqual(str(l), "153°05'20.448000\"W")


class velocityTestCase(unittest.TestCase):
    def setUp(self):
        self.v = velocity(8.5)

    def testKnots(self):
        self.failUnlessEqual(self.v, 8.5)
        self.failUnlessEqual(self.v.knots(), 8.5)

    def testKmph(self):
        self.failUnlessEqual(self.v.kmph(), 15.742)
        self.failUnlessEqual(self.v.kilometers_per_hour(), 15.742)

    def testMps(self):
        self.failUnlessEqual(self.v.meters_per_second(), 4.372777774)

    def testMph(self):
        self.failUnlessEqual(self.v.mph(), 9.781625325)
        self.failUnlessEqual(self.v.miles_per_hour(), 9.781625325)


if __name__ == '__main__':
    unittest.main()
