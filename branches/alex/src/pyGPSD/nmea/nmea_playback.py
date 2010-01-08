#!/usr/bin/env python
#
# NMEA Toolkit Playback tool
# Copyright (C) 2008 Tim Savage
#
# This file is part of the NMEA Toolkit.
#
# The NMEA Toolkit is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or at your option)
# any later version.
#
# The NMEA Toolkit is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# the NMEA Toolkit.  If not, see <http://www.gnu.org/licenses/>.

__version__ = '0.2'
__author__ = 'tim+python-gpsd@poweredbypenguins.org (Tim Savage)'

import socket
import sys
import time
import optparse


def workLoop(s, f, options):
    while True:
        # Wait for connections
        print 'Waiting for connection...'
        s.listen(1)

        conn, addr = s.accept()
        print 'Connected to', addr

        # Stream data to client
        while True:
            data = f.readline()
            delay = options.delay
            if not data:
                f.seek(0)
            else:
                # Check for a comment
                if data.startswith('#'):
                    continue

                # Handle the plain case
                if not options.plain:
                    adata = data.split(':', 1)

                    # Check this is plain row
                    if len(adata) == 2:
                        # Attempt to get delay
                        try:
                            delay = float(adata[0])
                        except:
                            pass
                        else:
                            data = adata[1]
                
                try:
                    conn.send(data)
                except socket.error:
                    break;
                time.sleep(delay)


def get_options():
    p = optparse.OptionParser(version="%prog " + __version__)
    p.add_option('-a', '--host', default='localhost',
        help='host to bind socket')
    p.add_option('-p', '--port', type='int', default=11000,
        help='port to bind socket')
    p.add_option('-f', '--file', default='gps.dump',
        help='file to use for input')
    p.add_option('-x', '--plain', action='store_true', default=False,
        help="file does not contain time deltas")
    p.add_option('-d', '--delay', type='float', default=0.2,
        help="delay between plain messages")
    return p.parse_args()


def main():
    result = 0
    options, args = get_options()

    # Open record file
    try:
        f = open(options.file, 'r')
    except IOError:
        print >> sys.stderr, "File not found: ", options.file
    else:
        print 'GPS record opened'

        # Open Port
        try:
            # Create listening socket
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((options.host, options.port))
            print 'Socket bound to %s:%d' % (options.host, options.port)
        except socket.error, sex:
            print sys.stderr, "Unable to open socket:", sex
            result = 1
        else:
            # Start work loop
            try:
                workLoop(s, f, options)
            except KeyboardInterrupt:
                pass
            except:
                print >> sys.stderr, "Unknown error occured:", sys.exc_value
                result = 2

            # Clean up
            s.close()

    return result


if __name__ == '__main__':
    sys.exit(main())
