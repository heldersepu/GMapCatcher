# -*- coding: utf-8 -*-
## @package gmapcatcher.widComboBoxEntry
# ComboBoxEntry widget used to collect data to search

import gtk
from mapConst import *


## This widget is where we collect data to search
class ComboBoxEntry(gtk.ComboBoxEntry):
    DEFAULT_TEXT = "Enter location here!"
    
    def __init__(self, confirm_clicked):
        super(ComboBoxEntry, self).__init__()
        self.connect('changed', self.changed_combo)
        self.connect('key-press-event', self.key_press_combo)
       
        # Launch clean_entry for all the signals/events below
        self.child.connect("button-press-event", self.clean_entry)
        self.child.connect("cut-clipboard", self.clean_entry)
        self.child.connect("copy-clipboard", self.clean_entry)
        self.child.connect("paste-clipboard", self.clean_entry)
        self.child.connect("move-cursor", self.clean_entry)
        self.child.connect("populate-popup", self.populate_popup)
        # Launch the default_entry on the focus out
        self.child.connect("focus-out-event", self.default_entry)
        # Start search after hit 'ENTER'
        self.child.connect('activate', confirm_clicked)
        self.confirm_clicked = confirm_clicked

    ## Clean out the entry box if text = default
    def clean_entry(self, *args):
        if (self.child.get_text() == self.DEFAULT_TEXT):
            self.child.set_text("")
            self.child.grab_focus()

    ## Reset the default text if entry is empty
    def default_entry(self, *args):
        if (self.child.get_text().strip() == ''):
            self.child.set_text(self.DEFAULT_TEXT)

    ## Add a new item to the menu of the EntryBox
    def populate_popup(self, w, menu):
        def menuitem_response(w, string):
            self.conf.match_func = string
        subMenu = gtk.Menu()
        for item in ENTRY_SUB_MENU:
            iMenuItem = gtk.RadioMenuItem(None, item)
            iMenuItem.set_active(item == self.conf.match_func)
            iMenuItem.connect("activate", menuitem_response, item)
            subMenu.append(iMenuItem)

        menuItem = gtk.MenuItem()
        menu.append(menuItem)
        menuItem = gtk.MenuItem('Auto-Completion Method')
        menuItem.set_submenu(subMenu)
        menu.append(menuItem)
        menu.show_all()
        
    ## Show the combo list if is not empty
    def combo_popup(self):
        if self.get_model().get_iter_root() is not None:
            self.popup()

    ## Handles the pressing of arrow keys
    def key_press_combo(self, w, event):
        if event.keyval in [65362, 65364]:
            self.combo_popup()
            return True

    ## Handles the change event of the ComboBox
    def changed_combo(self, *args):
        str = self.child.get_text()
        if (str.endswith(SEPARATOR)):
            self.child.set_text(str.strip())
            self.confirm_clicked(self)
