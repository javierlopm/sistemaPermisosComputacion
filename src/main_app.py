import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

culo = 0




class MyWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Hello World")

        self.set_title("Permisos coordinación")
        self.set_default_size(320,200)

        grid = Gtk.Grid()
        self.grid = grid
        self.add(grid)
        grid.props.halign = Gtk.Align.CENTER

        grid.insert_row(0)
        grid.insert_row(1)
        grid.insert_column(0)
        grid.insert_column(1)
        grid.insert_column(2)
        button1 = Gtk.Button(label="Buscar por carnet")
        button2 = Gtk.Button(label="Buscar por materia")
        button3 = Gtk.Button(label="Permisos de generales")
        button4 = Gtk.Button(label="Permisos de extra creditos")
        button5 = Gtk.Button(label="Permisos de PP")

        label = Gtk.Label()
        label.set_text("Quedan "+str(culo)+" permisos por procesar.")
        label.set_justify(Gtk.Justification.LEFT)



        grid.attach(label  ,1,0,2,2)
        grid.attach(button1,1,20,2,2)
        grid.attach(button2,1,25,2,2)
        grid.attach(button3,1,30,2,2)
        grid.attach(button4,1,35,2,2)
        grid.attach(button5,1,40,2,2)


        button1.connect("clicked", self.on_button1_clicked)



    def on_button1_clicked(self, widget):
        self.hide()
        global culo
        new_win = MyWindow()
        culo += 1
        response = new_win.show_all()

    def on_button2_clicked(self, widget):
        print("Goodbye")

win = MyWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()