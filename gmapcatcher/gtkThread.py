## @package gmapcatcher.gtkThread
# ---

import os
if os.environ.get('MAPS_GTK', 'False') == 'False':
    raise Exception('gtk module', __file__)

import sys
import pygtk
pygtk.require('2.0')
import gtk, gobject
from threading import Timer

## workaround for broken gtk threads in win32
if sys.platform=='win32':
    import time
    def do_gui_operation(function, *args, **kw):
        def idle_func():
            gtk.gdk.threads_enter()
            try:
                function(*args, **kw)
                return False
            finally:
                gtk.gdk.threads_leave()
        gobject.idle_add(idle_func)
    do_gui_operation=gobject.idle_add
    def _sleeper():
        time.sleep(0.001)
        return 1 # don't forget this otherwise the timeout will be removed

    gobject.timeout_add(100,_sleeper)

else:
    gtk.gdk.threads_init()
    do_gui_operation=gobject.idle_add

## may be used as decorator
def gui_callback(function):
    def cb(inGuiThread, *args, **kwargs):
        if inGuiThread:
            function(*args, **kwargs)
        else:
            do_gui_operation(function, *args, **kwargs)
    return cb

## Open the given page in a browser
def webbrowser_open(strPage):
    def openThread():
        import webbrowser
        webbrowser.open(strPage)
    try:
        oThread = Timer(0, openThread)
        oThread.start()
    except:
        pass
