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

## Message used in the updated notifications
class updateMsgBox(gtk.Window):
    def __init__(self, strMessage, strUrl, strDownloadUrl):

        gtk.Window.__init__(self)
        self.connect("destroy", lambda *w: gtk.main_quit())
        self.set_border_width(10)
        self.set_size_request(250, 200)
        self.set_title(' Automatic Updates ')

        hbox = gtk.HBox(False, 10)
        hbox.pack_start(gtk.Label(strMessage))

        vbox = gtk.VBox(False)
        vbox.pack_start(hbox)
        vbox.pack_start(gtk.Label(strUrl))
        self.add(vbox)
        self.show_all()
