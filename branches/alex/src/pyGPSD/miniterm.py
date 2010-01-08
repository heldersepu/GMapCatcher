#!/usr/bin/env python

# Very simple serial terminal
# (C)2002-2009 Chris Liechti <cliechti@gmx.net>


import sys, threading
import nmea.serial as serial


DEFAULT_PORT = 2
DEFAULT_BAUD = 4800


class Miniterm:
    def __init__(self, port, baudrate, parity, rtscts, xonxoff):
        self.serial = serial.serial_for_url(port, baudrate, parity=parity, 
                                rtscts=rtscts, xonxoff=xonxoff, timeout=1)

    def start(self):
        self.alive = True
        # start serial->console thread
        self.receiver_thread = threading.Thread(target=self.reader)
        self.receiver_thread.setDaemon(1)
        self.receiver_thread.start()

    def stop(self):
        self.alive = False

    def join(self):
        self.receiver_thread.join()

    def reader(self):
        """loop and copy serial->console"""
        while self.alive:
            data = self.serial.read(1)
            sys.stdout.write(data)            
            sys.stdout.flush()


def main():
    try:
        miniterm = Miniterm(DEFAULT_PORT, DEFAULT_BAUD, 'N',
            rtscts=False, xonxoff=False,
        )
    except serial.SerialException, e:
        sys.stderr.write("could not open port %r: %s\n" % (DEFAULT_PORT, e))
        sys.exit(1)

    miniterm.start()
    miniterm.join()


if __name__ == '__main__':
    main()
