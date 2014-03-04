#!/usr/bin/env python
#
# Python GPSD
# Copyright (C) 2008 Tim Savage
#
# Python GPSD is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or at your option)
# any later version.
#
# Python GPSD is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# python GPSD.  If not, see <http://www.gnu.org/licenses/>.

import dbus
from dbus.mainloop.glib import DBusGMainLoop
import dbus.service
import gobject
#import nmea
import nmea.gps
import optparse
import sys


__version__ = '0.1'


GPSD_BUS_NAME = 'org.poweredbypenguins.gpsd'

GPSD_OBJECT_PATH = '/org/poweredbypenguins/gpsd'
GPSD_IFACE_NAME = GPSD_BUS_NAME + '.gpsd'

class GpsdObject(dbus.service.Object):
    def __init__(self, bus):
        super(GpsdObject, self).__init__(bus, GPSD_OBJECT_PATH)


GPS_OBJECT_PATH = '/org/poweredbypenguins/gpsd/GPS%d'
GPS_IFACE_NAME = GPSD_BUS_NAME + '.gps'

class GpsObject(dbus.service.Object):
    def __init__(self, port, bus, object_path):
        super(GpsObject, self).__init__(bus, object_path)
        self.gps_device = nmea.gps.Gps(port, callbacks={
            'fix_update': self.__fix_update,
            'transit_update': self.__transit_update,
            'satellite_update': self.__satellite_update,
            'satellite_status_update': self.__satellite_status_update
        })

        # Register IO Callback
        gobject.io_add_watch(
            port,
            gobject.IO_IN,
            self.gps_device.handle_io)

    def __fix_update(self, gps_device):
        self.fix_update(
            gps_device.fixMode,
            gps_device.fixType,
            gps_device.fixQuality)

    def __transit_update(self, gps_device):
        self.transit_update(
            gps_device.position.get_value(),
            gps_device.track,
            gps_device.speed)

    def __satellite_update(self, gps_device):
        #print 'Satellite update'
        pass

    def __satellite_status_update(self, gps_device):
        #print 'Satellite status update'
        pass

    @dbus.service.method(dbus_interface=GPS_IFACE_NAME,
        out_signature='dd')
    def position(self):
        return self.gps_device.position.get_value()

    @dbus.service.signal(dbus_interface=GPS_IFACE_NAME,
        signature='syy')
    def fix_update(self, mode, type, quality):
        return (mode, type, quality)

    @dbus.service.signal(dbus_interface=GPS_IFACE_NAME,
        signature='(dd)di')
    def transit_update(self, position, track, speed):
        return(position, track, speed)


def gps_object(options, bus, index=0):
    """  Create gps port and dbus object """

    # Create GPS port
    port = gps_port(options)
    if port is None:
        return None

    # Create GPS object
    return GpsObject(port, bus, GPS_OBJECT_PATH % index)


def gps_port(options):
    """ Create instance of a gps port """
    if options.type == 'serial':
        from nmea.serialport import SerialPort
        return SerialPort(
            device=options.device,
            baud=options.baud,
            timeout=options.timeout)
    elif options.type == 'tcp':
        from nmea.tcpport import TcpPort
        return TcpPort(
            host=options.host,
            port=options.port,
            timeout=options.timeout)
    else:
        return None


def get_options():
    """ Setup options structure """
    p = optparse.OptionParser(version='%prog ' + __version__)
    p.add_option('-t', '--type', default='tcp', choices=['serial', 'tcp'],
        help='type of port to use: serial or tcp')
    p.add_option('--timeout', type='int', default=3,
        help='port read timeout (in seconds)')

    g = optparse.OptionGroup(p, 'Serial Backend')
    g.add_option('--device', default='/dev/gps',
        help='device file of serial port connected to GPS')
    g.add_option('--baud', type='int', default=4800)
    p.add_option_group(g)

    g = optparse.OptionGroup(p, 'TCP Backend')
    g.add_option('--host', default='localhost')
    g.add_option('--port', type='int', default=11000)
    p.add_option_group(g)

    options, arguments = p.parse_args()
    return options


def main():
    options = get_options()

    # Setup main loop
    mainLoop = DBusGMainLoop(set_as_default=True)

    # Attach to bus and register name
    bus = dbus.SessionBus()
    if bus.name_has_owner(GPSD_BUS_NAME):
        print >> sys.stderr, "GPSD name already registered on the BUS"
        return 1
    else:
        bus.request_name(GPSD_BUS_NAME)

    # Create device object
    gps_object0 = gps_object(options, bus)

    # Start event loop
    loop = gobject.MainLoop()
    try:
        loop.run()
    except KeyboardInterrupt:
        pass

    return 0


if __name__ == '__main__':
    sys.exit(main())
