import gtk
import fileUtils
from customWidgets import _frame, lbl


class ChangeTheme():
    ## Load the items into the Combo box
    def load_combo(self, myCombo):
        listThemes = fileUtils.get_themes()
        actualTheme = fileUtils.read_gtkrc()
        intTheme = 0
        model = myCombo.get_model()
        model.clear()
        myCombo.set_model(None)
        for l in range(len(listThemes)):
            model.append([listThemes[l]])
            if listThemes[l] == actualTheme:
                intTheme = l
        myCombo.set_model(model)
        myCombo.set_active(intTheme)

    ## All the buttons at the bottom
    def __action_buttons(self):
        def btn_revert_clicked(button):
            self.load_combo(self.cmb_themes)

        def btn_save_clicked(button):
            if self.cmb_themes.get_model():
                cmb_text = self.cmb_themes.get_active_text()
                if cmb_text:
                    fileUtils.write_gtkrc(cmb_text)

        bbox = gtk.HButtonBox()
        bbox.set_layout(gtk.BUTTONBOX_END)
        bbox.set_border_width(10)
        bbox.set_spacing(60)

        button = gtk.Button(stock=gtk.STOCK_REVERT_TO_SAVED)
        button.connect('clicked', btn_revert_clicked)
        bbox.add(button)

        button = gtk.Button(stock=gtk.STOCK_SAVE)
        button.connect('clicked', btn_save_clicked)
        bbox.add(button)
        return bbox

    ## Put all the ChangeTheme Widgets together
    def show(self):
        hbox = gtk.HBox(False, 10)
        vbox = gtk.VBox(False, 10)
        vbox.set_border_width(10)
        hbox.pack_start(lbl("Select new theme and restart GMapCatcher."))
        self.cmb_themes = gtk.combo_box_new_text()

        self.load_combo(self.cmb_themes)
        hbox.pack_start(self.cmb_themes)
        vbox.pack_start(_frame(" Available themes ", hbox), False)

        hpaned = gtk.VPaned()
        hpaned.pack1(vbox, True, True)
        buttons = self.__action_buttons()
        hpaned.pack2(buttons, False, False)
        return hpaned

