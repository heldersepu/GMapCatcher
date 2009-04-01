import sys
import pygtk
pygtk.require('2.0')
import gtk, gobject

# workaround for broken gtk threads in win32
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
    def _sleeper():
	
        time.sleep(.001)
        return 1 # don't forget this otherwise the timeout will be removed

    gobject.timeout_add(500,_sleeper)

else:
    do_gui_operation=gobject.idle_add
    