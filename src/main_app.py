import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from coord_crawler import format_id,show_carnet,StudentDownloader
from easygui       import msgbox
import csv_creator
from perm_store import *

db = PermStore()

class SearchWindow(Gtk.Window):

    def __init__(self,old_window,name):
        self.old_window = old_window
        self.name       = name
        Gtk.Window.__init__(self, title="Hello World")

        self.connect("delete-event", Gtk.main_quit)

        self.set_title("Permisos coordinación")
        self.set_default_size(320,200)

        # Grid
        grid = Gtk.Grid()
        self.grid = grid
        self.add(grid)
        grid.props.halign = Gtk.Align.CENTER

        grid.insert_row(0)
        grid.insert_row(1)
        grid.insert_row(2)
        grid.insert_column(0)
        grid.insert_column(1)
        grid.insert_column(2)
        grid.insert_column(3)
        grid.insert_column(4)

        grid.set_row_spacing(10)
        grid.set_column_spacing(30)

        # Widgets
        button2 = Gtk.Button(label="←")

        label = Gtk.Label()
        label.set_text("Vista de búsqueda")
        label.set_justify(Gtk.Justification.LEFT)

        inv_box = Gtk.Box(spacing=20)

        # attach (child, left, top, width, height)
        # grid.attach(label  ,2,0,2,2)
        # grid.attach(button1,2,3,2,2)
        # grid.attach(button2,0,0,1,1)
        grid.attach(label  ,2,0,1,1)
        grid.attach(button2,0,0,1,1)
        grid.attach(inv_box,4,2,2,2)


        button1.connect("clicked", self.on_button1_clicked)
        button2.connect("clicked", self.on_button2_clicked)




    def on_button1_clicked(self, widget):
        pass

    def on_button2_clicked(self, widget):
        # self.hide()
        self.old_window.show()
        self.destroy()

class StudentWindow(Gtk.Window):
    """
        Ventana para ver un estudiante
    """
    def __init__(self,old_window,std_data,std_perms):
        self.old_window = old_window
        Gtk.Window.__init__(self, title="Permisos coordinación")

        self.connect("delete-event", Gtk.main_quit)

        self.set_default_size(320,200)

        # Grid
        grid = Gtk.Grid()
        self.grid = grid
        self.add(grid)
        grid.props.halign = Gtk.Align.CENTER

        grid.insert_row(0)
        grid.insert_row(1)
        grid.insert_row(2)
        grid.insert_column(0)
        grid.insert_column(1)
        grid.insert_column(2)
        grid.insert_column(3)
        grid.insert_column(4)

        grid.set_row_spacing(10)
        grid.set_column_spacing(30)

        # Widgets
        button_ret = Gtk.Button(label="←")

        print("=============")
        print(std_data)
        label = Gtk.Label()
        label.set_text("Estudiante " + str(std_data['carnet']))
        label.set_justify(Gtk.Justification.LEFT)

        inv_box = Gtk.Box(spacing=20)
 
        grid.attach(label     ,2,0,1,1)
        grid.attach(button_ret,0,0,1,1)
        grid.attach(inv_box   ,4,2,2,2)


        button_ret.connect("clicked", self.go_back)




    def on_button1_clicked(self, widget):
        pass

    def go_back(self, widget):
        self.old_window.show()
        self.destroy()



class InitWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Permisos coordinacion")
        self.set_default_size(320,200)

        grid = Gtk.Grid()
        self.grid = grid
        self.add(grid)
        grid.props.halign = Gtk.Align.CENTER

        grid.insert_column(0)
        grid.insert_row(0)
        grid.insert_row(1)
        grid.insert_row(2)
        grid.set_row_spacing(10)
        grid.set_column_spacing(30)

        # Widgets
        label = Gtk.Label()
        label.set_text("Bienvenidos al sistema de permisos.\nSeleccione una opcion")
        label.set_justify(Gtk.Justification.CENTER)



        button1 = Gtk.Button(label="Descargar permisos")
        button2 = Gtk.Button(label="Iniciar programa de permisos")

        grid.attach(label,0,0,2,2)
        grid.attach(button1,0,5,2,2)
        grid.attach(button2,0,25,2,2)
        grid.attach(button2,0,25,2,2)

        button1.connect("clicked", self.on_button1_clicked)
        button2.connect("clicked", self.on_button2_clicked)

    def on_button1_clicked(self, widget):
        #new_win = SearchWindow(self,"carnet")
        #response = new_win.show_all()
        pass

    def on_button2_clicked(self, widget):
        self.hide()
        new_win = MainWindow()
        response = new_win.show_all()

class LoginWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Permisos coordinación")
        self.set_default_size(320,200)
        grid = Gtk.Grid()
        self.grid = grid
        self.add(grid)
        grid.props.halign = Gtk.Align.CENTER

        grid.insert_column(0)

        grid.insert_row(0)
        grid.insert_row(1)
        grid.insert_row(2)
        
        grid.set_row_spacing(10)
        grid.set_column_spacing(30)

        label = Gtk.Label()
        label.set_text("Ingrese sus credenciales para acceder al sistema de expendientes.")
        label.set_justify(Gtk.Justification.CENTER)

        username_entry = Gtk.entry()
        password_entry = Gtk.entry()

        grid.attach(label,0,0,2,2)
        grid.attach(username_entry,0,5,2,2)
        grid.attach(password_entry,0,25,2,2)




class MainWindow(Gtk.Window):
    """
        Ventana principal de búsqueda de permisos y estudiantes
    """
    def __init__(self):
        Gtk.Window.__init__(self, title="Hello World")
        self.connect("delete-event", Gtk.main_quit)

        self.set_title("Permisos coordinación")
        self.set_default_size(320,200)

        grid = Gtk.Grid()
        self.grid = grid
        self.add(grid)
        grid.props.halign = Gtk.Align.CENTER
        grid.set_row_spacing(10)
        grid.set_column_spacing(50)

        grid.insert_row(0)
        grid.insert_row(1)
        grid.insert_row(2)
        grid.insert_row(3)
        grid.insert_column(0)
        grid.insert_column(1)
        grid.insert_column(2)
        button1 = Gtk.Button(label="Buscar por carnet")
        button2 = Gtk.Button(label="Buscar por materia")
        button3 = Gtk.Button(label="Permisos de generales")
        button4 = Gtk.Button(label="Permisos de extra creditos")
        button5 = Gtk.Button(label="Permisos de PP")
        self.student_entry = Gtk.Entry()

        inv_box = Gtk.Box(spacing=4)

        inv_box.pack_start(button1,True,True,0)
        inv_box.pack_end(self.student_entry,True,True,2)

        # grid.attach(inv_box,1,5,1,1)



        label = Gtk.Label()
        label.set_text("Quedan permisos por procesar.")
        label.set_justify(Gtk.Justification.LEFT)



        # grid.attach(button1,0,20,2,2)
        # grid.attach(student_entry,2,20,1,1)
        grid.attach(inv_box,1,20,1,1)

        grid.attach(label  ,1,0,2,2)
        grid.attach(button2,1,25,2,3)
        grid.attach(button3,1,30,2,3)
        grid.attach(button4,1,35,2,3)
        grid.attach(button5,1,40,2,3)


        button1.connect("clicked", self.on_student_clicked)



    def on_student_clicked(self, widget):
        formated_carnet = format_id(self.student_entry.get_text())

        if formated_carnet:
            formated_carnet = int(formated_carnet)
            student_data    = db.get_student(formated_carnet)
            student_perms   = db.get_student_perms(formated_carnet,Trimestre.septiembreDiciembre,2016)
            print(student_data )
            print(student_perms)

            if (not student_data):
                msgbox("El estudiante " + show_carnet(formated_carnet) + " no existe en la bd")
                return

            if (not student_perms):
                msgbox("El estudiante " + show_carnet(formated_carnet) + " no ha solicitado permisos")
                return

            self.hide()
            new_win = StudentWindow(self,student_data[0],student_perms)
            # new_win = SearchWindow(self,"carnet")
            response = new_win.show_all()
        else:
            msgbox("Formato inválido, intente con 0000000,00-00000 ó 00-00000@usb.ve")


win = InitWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()