import dbus
from dbus.mainloop.glib import DBusGMainLoop
import gobject
import nmea
import sys


GPSD_BUS_NAME = 'org.poweredbypenguins.gpsd'

GPSD_OBJECT_PATH = '/org/poweredbypenguins/gpsd'
GPSD_IFACE_NAME = GPSD_BUS_NAME + '.gpsd'

GPS_OBJECT_PATH = '/org/poweredbypenguins/gpsd/GPS%d'
GPS_IFACE_NAME = GPSD_BUS_NAME + '.gps'

def transit_update(position, track, speed):
    ll = nmea.latlng(position)
    v = nmea.velocity(speed)
    print "> transit_update - Position:", ll, "\tTrack:", track, "\tSpeed:", v.kmph(), 'km/h'

def main():
    # Setup main loop
    mainLoop = DBusGMainLoop(set_as_default=True)

    # Attach to bus
    bus = dbus.SessionBus()
    print ">> Attached to bus:", bus

    # GPS Device
    gps = bus.get_object(GPSD_BUS_NAME, GPS_OBJECT_PATH % 0)
    print ">> Obtained gps object:", gps

    gps_iface = dbus.Interface(gps, GPS_IFACE_NAME)
    print ">> Obtained gps object interface:", gps_iface

    # Bind transit update
    gps_iface.connect_to_signal('transit_update', transit_update)
    print ">> Bound to transit_update signal."

    # Start event loop
    loop = gobject.MainLoop()
    try:
        loop.run()
    except KeyboardInterrupt:
        pass

    return 0


if __name__ == '__main__':
    sys.exit(main())
