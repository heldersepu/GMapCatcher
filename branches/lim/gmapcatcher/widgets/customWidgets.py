# -*- coding: utf-8 -*-
## @package gmapcatcher.widgets.customWidgets
# This is a collection of Custom Widgets

import gtk
import gobject
import mapPixbuf
from gmapcatcher.mapConst import *
from inputValidation import allow_only_numbers

import warnings
warnings.filterwarnings("ignore")

ternary = lambda a, b, c: (b, c)[not a]


## A simple right justify label
def lbl(text):
    l = gtk.Label(text)
    l.set_justify(gtk.JUSTIFY_RIGHT)
    return l


## Pack a given container in a nice frame
def myFrame(strName, container, spacing=5):
    frame = gtk.Frame(strName)
    vbox = gtk.VBox(False, spacing)
    vbox.set_border_width(spacing)
    vbox.pack_start(container)
    frame.add(vbox)
    return frame


## A Spin button that allows numbers only
def SpinBtn(value=0, lower=MAP_MIN_ZOOM_LEVEL,
            upper=MAP_MAX_ZOOM_LEVEL, step=1, maxChars=2, isInt=True):
    a_zoom = gtk.Adjustment(value, lower, upper, step)
    spin = gtk.SpinButton(a_zoom)
    spin.connect('insert-text', allow_only_numbers, maxChars, isInt)
    return spin


## An entry box that allows numbers only
def myEntry(strText, maxChars=8, isInt=True):
    dEntry = gtk.Entry()
    dEntry.set_text(strText)
    dEntry.connect('insert-text', allow_only_numbers, maxChars, isInt)
    return dEntry


## Prompt user to select a Folder
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


## Prompt user to select a File
def FileChooser(strPath='.', strTitle="Select File"):
    strFileName = False
    dialog = gtk.FileChooserDialog(strTitle, None,
                                    gtk.FILE_CHOOSER_ACTION_OPEN,
                                    (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                    gtk.STOCK_OK, gtk.RESPONSE_OK))
    dialog.set_default_response(gtk.RESPONSE_OK)
    dialog.set_current_folder(strPath)
    if dialog.run() == gtk.RESPONSE_OK:
        strFileName = dialog.get_filename()
    dialog.destroy()
    return strFileName


## Prompt user to select a File
def FileSaveChooser(strPath='.', strTitle="Select File"):
    strFileName = False
    dialog = gtk.FileChooserDialog(strTitle, None,
                                    gtk.FILE_CHOOSER_ACTION_SAVE,
                                    (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                    gtk.STOCK_SAVE, gtk.RESPONSE_OK))
    dialog.set_default_response(gtk.RESPONSE_CANCEL)
    dialog.set_current_folder(strPath)
    dialog.set_do_overwrite_confirmation(True)
    if dialog.run() == gtk.RESPONSE_OK:
        strFileName = dialog.get_filename()
    dialog.destroy()
    return strFileName


## Display a Tooltip
def myToolTip(widget, x, y, keyboard_mode, tooltip, title, desc, filename=None):
    table = gtk.Table(2, 2)
    table.set_row_spacings(2)
    table.set_col_spacings(6)
    table.set_border_width(4)

    pixbuf = mapPixbuf.getImage(filename)
    image = gtk.image_new_from_pixbuf(pixbuf)
    image.set_alignment(0, 0)
    table.attach(image, 0, 1, 0, 2)

    titleLabel = gtk.Label()
    titleLabel.set_markup("<b>%s</b>" % title)
    titleLabel.set_alignment(0, 0)
    table.attach(titleLabel, 1, 2, 0, 1)

    descLabel = gtk.Label(desc)
    descLabel.props.wrap = True
    table.attach(descLabel, 1, 2, 1, 2)

    tooltip.set_custom(table)
    table.show_all()
    return True


## Create a gtk Menu with the given items
def gtk_menu(listItems, activate_action):
    myMenu = gtk.Menu()
    for thestr in listItems:
        # An empty item inserts a separator
        if thestr != "-":
            if thestr == "":
                menu_items = gtk.MenuItem()
            else:
                menu_items = gtk.MenuItem(thestr)
        myMenu.append(menu_items)
        menu_items.connect("activate", activate_action, thestr)
        menu_items.show()
    return myMenu


def legal_warning(parent, servicename, feature):
    msgtype = ternary(STRICT_LEGAL, gtk.MESSAGE_INFO, gtk.MESSAGE_WARNING)
    buttons = ternary(STRICT_LEGAL, gtk.BUTTONS_CANCEL, gtk.BUTTONS_OK_CANCEL)
    additional = ternary(STRICT_LEGAL, "",
        "If you insist on doing so, you break its term of use. \n\n"
        "Continue or cancel?")
    dialog = gtk.MessageDialog(parent,
        gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
        msgtype, buttons,
        (("This map service (%s) doesn't allow %s. " + additional) % (servicename, feature)))
    response = dialog.run()
    dialog.destroy()
    return response == gtk.RESPONSE_OK and not STRICT_LEGAL


## A looping ProgressBar
class ProgressBar(gtk.ProgressBar):
    timer = 0

    def progress_timeout(pbobj):
        pbobj.pulse()
        return True

    def __init__(self, strText):
        super(ProgressBar, self).__init__()
        self.set_text(strText)

    def off(self):
        try:
            if self.timer != 0:
                gobject.source_remove(self.timer)
                self.timer = 0
        finally:
            self.hide()

    def on(self):
        try:
            self.timer = gobject.timeout_add(100, self.progress_timeout)
        finally:
            self.show()
