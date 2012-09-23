## @package gmapcatcher.customMsgBox
# A group of custom message box widgets.

import pygtk
pygtk.require('2.0')
import gtk


## Message used to as user confirmation
def user_confirm(parent, strMessage, buttons=gtk.BUTTONS_YES_NO):
    dialog = gtk.MessageDialog(parent,
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            gtk.MESSAGE_QUESTION, buttons, strMessage)
    resp = dialog.run()
    dialog.destroy()
    if resp == -8:
        return True
    else:
        return False


## Message used to display errors
def error_msg(parent, strMessage, buttons=gtk.BUTTONS_OK):
    dialog = gtk.MessageDialog(parent,
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            gtk.MESSAGE_ERROR, buttons, strMessage)
    resp = dialog.run()
    dialog.destroy()
    return resp


def error_msg_non_blocking(strTitle, strMessage):
    strMessage = strMessage.center(50)
    dialog = gtk.MessageDialog(
        parent=None,
        flags=gtk.DIALOG_DESTROY_WITH_PARENT,
        type=gtk.MESSAGE_ERROR,
        buttons=gtk.BUTTONS_OK,
        message_format=strMessage)
    dialog.set_title(strTitle)
    return dialog


## Message used in the updated notifications
class updateMsgBox(gtk.Window):
    def hyperlink(self, strUrl):
        def followLink(*w):
            self.hide()
            import webbrowser
            webbrowser.open(strUrl)
            gtk.main_quit()

        event_box = gtk.EventBox()
        label_URL = gtk.Label()
        label_URL.set_text("<span foreground=\"blue\" underline=\"single\">" +
                        strUrl + "</span>")
        label_URL.set_use_markup(True)
        event_box.add(label_URL)
        event_box.set_events(gtk.gdk.BUTTON_PRESS_MASK)
        event_box.connect("button_press_event", followLink)
        return event_box

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

        link = self.hyperlink(strUrl)
        vbox.pack_start(link)
        vbox.pack_start(self.btn_ok())
        self.add(vbox)

        link.realize()
        link.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.HAND1))
        self.show_all()
