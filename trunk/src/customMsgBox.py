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
    def __init__(self, strMessage):

        gtk.Window.__init__(self)
        self.set_border_width(10)
        self.set_size_request(200, 200)
        self.set_title(' Automatic Updates ')

        #myNotebook = self.__create_notebook(parent)
        self.add(gtk.Label('Automatic Updates Coming soon!! '))
        self.connect('delete-event', self.on_delete)
        self.show_all()
    
    def on_delete(self,*params):
        return False
        
if __name__ == "__main__":
    updateMsgBox("Test")
    gtk.main()