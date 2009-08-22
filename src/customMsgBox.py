## @package src.customMsgBox
# A group of custom message box widgets.

import pygtk
pygtk.require('2.0')
import gtk
import atk


## Message used to display errors
def error_msg(parent, strMessage, buttons=gtk.BUTTONS_OK):
    dialog = gtk.MessageDialog(parent,
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            gtk.MESSAGE_ERROR, buttons, strMessage)
    resp = dialog.run()
    dialog.destroy()
    return resp

def hyperlink(strUrl):
    label_URL = gtk.Label()
    label_URL.set_text("<span foreground=\"blue\" underline=\"single\">" +
                    strUrl +  "</span>")
    label_URL.set_use_markup(True)
    return label_URL


## Message used in the updated notifications
class updateMsgBox(gtk.Window):
    def btn_ok(self):
        button = gtk.Button(stock=gtk.STOCK_OK)
        button.connect("clicked", lambda *w: gtk.main_quit())
        hbox = gtk.HButtonBox()
        hbox.pack_start(button)
        hbox.set_layout(gtk.BUTTONBOX_SPREAD)
        return hbox

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
        vbox.pack_start(hyperlink(strUrl))
        vbox.pack_start(self.btn_ok())
        self.add(vbox)
        self.show_all()
