import gtk
from mapConst import *
from inputValidation import allow_only_numbers


def lbl(text):
    l = gtk.Label(text)
    l.set_justify(gtk.JUSTIFY_RIGHT)
    return l

def _frame(strName, container, spacing = 5):
    frame = gtk.Frame(strName)
    vbox = gtk.VBox(False, spacing)
    vbox.set_border_width(spacing)
    vbox.pack_start(container)
    frame.add(vbox)
    return frame

def _SpinBtn(value=0, lower=MAP_MIN_ZOOM_LEVEL,
             upper=MAP_MAX_ZOOM_LEVEL, step=1, maxChars=2):
    a_zoom = gtk.Adjustment(value, lower, upper, step)
    spin = gtk.SpinButton(a_zoom)
    spin.connect('insert-text', allow_only_numbers, maxChars)
    return spin

def _myEntry(strText, maxChars=8, isInt=True):
    myEntry = gtk.Entry()
    myEntry.set_text(strText)
    myEntry.connect('insert-text', allow_only_numbers, maxChars, isInt)
    return myEntry

## Folder chooser dialog
def FolderChooser():
    strFileName = False
    dialog = gtk.FileChooserDialog("Select Folder", None,
                                   gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                                   (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                    gtk.STOCK_OK, gtk.RESPONSE_OK))
    dialog.set_default_response(gtk.RESPONSE_OK)
    if dialog.run() == gtk.RESPONSE_OK:
        strFileName = dialog.get_filename()
    dialog.destroy()
    return strFileName
