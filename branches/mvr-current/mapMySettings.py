import gtk
from customWidgets import _SpinBtn, _frame, lbl


class MySettings():

    def show(self, parent):
        def _size(width, height):
            hbox = gtk.HBox(False, 10)
            hbox.pack_start(lbl("Width:"), False)
            self.s_width = _SpinBtn(width, 450, 1024, 100, 4)
            hbox.pack_start(self.s_width)

            hbox.pack_start(lbl("Height:"), False)
            self.s_height = _SpinBtn(height, 400, 768, 100, 4)
            hbox.pack_start(self.s_height)
            return _frame(" Size ", hbox)

        def _zoom(zoom):
            hbox = gtk.HBox(False, 10)
            self.s_zoom = _SpinBtn(zoom)
            hbox.pack_start(self.s_zoom, False)
            return _frame(" Zoom ", hbox)

        def _center(center):
            hbox = gtk.HBox(False, 0)
            hbox.pack_start(lbl(" (( "), False)
            self.s_center00 = _SpinBtn(center[0][0], 0, 999999, 1, 6)
            hbox.pack_start(self.s_center00, False)
            hbox.pack_start(lbl(" ,  "), False)
            self.s_center01 = _SpinBtn(center[0][1], 0, 999999, 1, 6)
            hbox.pack_start(self.s_center01, False)
            hbox.pack_start(lbl(" ), ( "), False)
            self.s_center10 = _SpinBtn(center[1][0], 0, 256, 32, 3)
            hbox.pack_start(self.s_center10, False)
            hbox.pack_start(lbl(" ,  "), False)
            self.s_center11 = _SpinBtn(center[1][1], 0, 256, 32, 3)
            hbox.pack_start(self.s_center11, False)
            hbox.pack_start(lbl(" )) "), False)
            return _frame(" Center ", hbox)

        def custom_path(conf):
            def get_folder(button):
                fileName = FolderChooser()
                if fileName:
                    self.entry_custom_path.set_text(fileName)

            vbox = gtk.VBox(False, 10)
            vbox.set_border_width(10)
            vbox.pack_start( \
                lbl(" Enter None or leave blank to use default directory. "))
            hbox = gtk.HBox(False, 10)
            myEntry = gtk.Entry()
            if conf.init_path:
                myEntry.set_text(conf.init_path)
            else:
                myEntry.set_text("None")
            hbox.pack_start(myEntry)
            self.entry_custom_path = myEntry
            button = gtk.Button(" ... ")
            button.connect('clicked', get_folder)
            hbox.pack_start(button, False)
            vbox.pack_start(hbox)
            return _frame(" Custom Maps Directory ", vbox)

        def _action_buttons(conf):
            def btn_revert_clicked(button):
                self.s_center00.set_value(conf.init_center[0][0])
                self.s_center01.set_value(conf.init_center[0][1])
                self.s_center10.set_value(conf.init_center[1][0])
                self.s_center11.set_value(conf.init_center[1][1])

                self.s_zoom.set_value(conf.init_zoom)
                self.s_width.set_value(conf.init_width)
                self.s_height.set_value(conf.init_height)

                if conf.init_path:
                    self.entry_custom_path.set_text(conf.init_path)
                else:
                    self.entry_custom_path.set_text("None")

            def btn_save_clicked(button):
                conf.init_center = ((self.s_center00.get_value_as_int()),
                                    (self.s_center01.get_value_as_int())), \
                                   ((self.s_center10.get_value_as_int()),
                                    (self.s_center11.get_value_as_int()))

                conf.init_zoom = self.s_zoom.get_value_as_int()
                conf.init_width = self.s_width.get_value_as_int()
                conf.init_height = self.s_height.get_value_as_int()
                strTemp = (self.entry_custom_path.get_text().lower()).strip()
                if strTemp != "" and strTemp != "none":
                    conf.init_path = self.entry_custom_path.get_text()
                else:
                    conf.init_path = None
                conf.save()

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

        def btn_use_current(button, parent):
            self.s_center00.set_value(parent.center[0][0])
            self.s_center01.set_value(parent.center[0][1])
            self.s_center10.set_value(parent.center[1][0])
            self.s_center11.set_value(parent.center[1][1])
            self.s_zoom.set_value(parent.current_zoom_level)

        hpaned = gtk.VPaned()
        vbox = gtk.VBox()
        vbox.set_border_width(10)

        hbox = gtk.HBox(False, 10)
        conf = parent.conf
        hbox.pack_start(_size(conf.init_width, conf.init_height))
        hbox.pack_start(_zoom(conf.init_zoom), False)
        vbox.pack_start(hbox, False)

        hbox = gtk.HBox(False, 10)
        hbox.pack_start(_center(conf.init_center))
        bbox = gtk.HButtonBox()
        button = gtk.Button("Use Current")
        button.connect('clicked', btn_use_current, parent)
        bbox.add(button)
        hbox.pack_start(bbox)

        vbox.pack_start(hbox, False)
        hbox = gtk.HBox(False, 10)
        hbox.set_border_width(20)
        hbox.pack_start(custom_path(conf))
        vbox.pack_start(hbox, False)
        hpaned.pack1(vbox, True, True)
        hpaned.pack2(_action_buttons(conf), False, False)
        return hpaned
