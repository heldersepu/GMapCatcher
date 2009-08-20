## @package src.customMsgBox
# A custom message box widget.

import pygtk
pygtk.require('2.0')
import gtk


def error_msg(parent, strMessage, buttons=gtk.BUTTONS_OK):
    dialog = gtk.MessageDialog(parent,
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            gtk.MESSAGE_ERROR, buttons, strMessage)
    resp = dialog.run()
    dialog.destroy()
    return resp

class updateMsgBox(gtk.Window):
    def __init__(self, strMessage, strUrl, strDownloadUrl):

        gtk.Window.__init__(self)
        self.connect("destroy", lambda *w: gtk.main_quit())
        self.set_border_width(10)
        self.set_size_request(200, 200)
        self.set_title(' Automatic Updates ')

        self.add(gtk.Label(strMessage))
        #self.add(gtk.Label(strUrl))
        #self.add(gtk.Label(strDownloadUrl))

        self.show_all()
