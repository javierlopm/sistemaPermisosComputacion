import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk,GdkPixbuf,Gdk

from coord_crawler import format_id,show_carnet,StudentDownloader
from easygui       import msgbox
import os.path
import csv_creator
from perm_store import *
from copy import deepcopy

db = PermStore()
RATIO = 0.75

class HeaderBarWindow(Gtk.Window):

    def __init__(self,return_window):
        Gtk.Window.__init__(self, title="HeaderBar Demo")
        self.set_border_width(10)
        # self.set_default_size(400, 200)
        self.old_window = return_window
        self.set_position(Gtk.WindowPosition.CENTER)
        self.connect("delete-event", Gtk.main_quit)
        hb = Gtk.HeaderBar()
        hb.set_show_close_button(True)
        hb.props.title = "Permisos coordinación"
        self.set_titlebar(hb)

        
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        Gtk.StyleContext.add_class(box.get_style_context(), "linked")

        button = Gtk.Button()
        button.add(Gtk.Arrow(Gtk.ArrowType.LEFT, Gtk.ShadowType.NONE))
        box.add(button)
        button.connect("clicked",self.on_button_ret_clicked)

        hb.pack_start(box)
        
    def on_button_ret_clicked(self, widget):
        self.old_window.show()
        self.destroy()


class SearchWindow(HeaderBarWindow):

    def __init__(self,old_window,perm_type,code=None):
        HeaderBarWindow.__init__(self,old_window)
        self.perm_type  = perm_type
        self.set_default_size(320,200)
        self.missing_count = None

        main_box     = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        # Box for label
        self.fst_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,spacing=0)
        main_box.pack_start(self.fst_box,True,True,0)

        # scrollable view para permisos
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        main_box.pack_start(self.scrolled_view,True,True,0)


        # Obtener premisos
        if perm_type == TipoPermiso.permiso_materia:
            courses = db.get_course_perms(code)
        else:
            courses = db.get_type_perm(perm_type)

        self.update_missing_perms(len(courses))

        # Tipos de permiso
        [liststore_status.append(e) for e in get_all_names(TipoPermiso)]
        # status     = dir(EstadoPermiso)[4:]
        # liststore_status = Gtk.ListStore(str)
        # for item in status:
        #     liststore_status.append([item])


        # Inicio de carga de permisos solicitados
        liststore = Gtk.ListStore(str, str)
        for elem in std_data.items():
            liststore.append([ elem[0],str(elem[1]) ] )
        treeview = Gtk.TreeView(model=liststore)

        renderer_text = Gtk.CellRendererText()
        column_text = Gtk.TreeViewColumn("Dato", renderer_text, text=0)
        treeview.append_column(column_text)

        renderer_spin = Gtk.CellRendererSpin()
        renderer_spin.set_property("editable", False)

        column_spin = Gtk.TreeViewColumn("Valor", renderer_spin, text=1)
        treeview.append_column(column_spin)
        # Inicio de carga de permisos solicitados

    def update_missing_perms(self,new_val):
        if self.missing_count:
            self.missing_count.destroy()

        missing_count = Gtk.Label()
        missing_count.set_text(str(new_val) + " permisos pendientes")
        missing_count.set_justify(Gtk.Justification.CENTER)
        self.missing_count = missing_count

        self.fst_box.pack_start(missing_count,True,True,0)
        missing_count.show()



    def on_button1_clicked(self, widget):
        pass

    def on_button_ret_clicked(self, widget):
        # self.hide()
        self.old_window.show()
        self.destroy()

class StudentWindow(Gtk.Window):
    """
        Ventana para ver un estudiante
    """
    def __init__(self,old_window,std_data):
        self.old_window = old_window
        Gtk.Window.__init__(self, title="Permisos coordinación")

        self.connect("delete-event", Gtk.main_quit)

        self.set_default_size(640,200)
        self.set_position(Gtk.WindowPosition.CENTER)

        self.wrapper_grid = Gtk.Grid()
        self.outter_grid  = Gtk.Grid()
        grid = Gtk.Grid()
        grid.props.halign = Gtk.Align.CENTER

        self.add(self.wrapper_grid)

        # Grid
        # self.grid = grid
        

        grid.insert_row(0)
        grid.insert_row(1)
        grid.insert_row(2)
        grid.insert_row(3)
        grid.insert_row(4)
        grid.insert_column(0)
        grid.insert_column(1)
        grid.insert_column(2)
        grid.insert_column(3)
        grid.insert_column(4)

        grid.set_row_spacing(10)
        grid.set_column_spacing(30)
        self.wrapper_grid.set_row_spacing(10)

        # Widgets
        button_ret = Gtk.Button(label="←")

        label = Gtk.Label()
        label.set_text("Estudiante " + show_carnet(std_data['carnet']) )
        label.set_justify(Gtk.Justification.LEFT)


        # Inicio de lista de datos
        liststore = Gtk.ListStore(str, str)
        for elem in std_data.items():
            liststore.append([ elem[0],str(elem[1]) ] )
        treeview = Gtk.TreeView(model=liststore)

        renderer_text = Gtk.CellRendererText()
        column_text = Gtk.TreeViewColumn("Dato", renderer_text, text=0)
        treeview.append_column(column_text)

        renderer_spin = Gtk.CellRendererSpin()
        renderer_spin.set_property("editable", False)

        column_spin = Gtk.TreeViewColumn("Valor", renderer_spin, text=1)
        treeview.append_column(column_spin)
        #Fin de lista de datos


        # Carga de grafo
        str_image = 'images/'+show_carnet(std_data['carnet'])+".png"
        str_image = str_image if os.path.isfile(str_image) else "images/noFile.png"

        img = Gtk.Image()
        pixbuf    = GdkPixbuf.Pixbuf.new_from_file(str_image)
        scaled_buff =pixbuf.scale_simple(1132*RATIO,291*RATIO,GdkPixbuf.InterpType.BILINEAR)

        img.set_from_pixbuf(scaled_buff)
        # Fin de grafo


        inv_box = Gtk.Box(spacing=20)
        
        self.outter_grid.attach(grid,0,0,1,1)

        grid.attach(label     ,2,0,1,1)
        grid.attach(button_ret,0,0,1,1)
        grid.attach(inv_box   ,4,2,2,2)
        grid.attach(treeview  ,2,3,2,2)

        self.outter_grid.attach(img,1,0,1,1)

        self.wrapper_grid.attach(self.outter_grid,0,0,1,1)

        button_ret.connect("clicked", self.go_back)


    def on_button1_clicked(self, widget):
        pass

    def go_back(self, widget):
        self.old_window.show()
        self.destroy()

class StudentAllPerms(StudentWindow):
    """docstring for StudentAllPerms"""
    def __init__(self,old_window,std_data,std_perms):
        StudentWindow.__init__(self,old_window,std_data)

        self.std_perms = std_perms
        # All type of enums
        # trims      = dir(Trimestre)[4:]
        # perm_types = dir(TipoPermiso)[4:]

        status     = dir(EstadoPermiso)[4:]

        liststore_status = Gtk.ListStore(str)

        for item in status:
            liststore_status.append([item])

        # Inicio de lista de datos
        # tipo, trim, anio, extra_field, aprobado
        liststore = Gtk.ListStore(str,int,str,str,str,int)
        self.liststore = liststore

        print(std_perms)

        for i,elem in enumerate(std_perms):
            typ = TipoPermiso(elem['tipo'])
            extra_field = ""

            if  (typ == TipoPermiso.permiso_materia):
                extra_field = elem['string_extra']
            elif (typ == TipoPermiso.limite_creditos):
                extra_field = str(elem['int_extra'])

            liststore.append([Trimestre(elem['trimestre']).name
                             ,elem['anio']
                             ,typ.name
                             ,extra_field
                             ,EstadoPermiso(elem['aprobado']).name
                             ,i])

        treeview = Gtk.TreeView(model=liststore)

        renderer_text = Gtk.CellRendererText()

        column_text1 = Gtk.TreeViewColumn("Trimestre", renderer_text, text=0)
        column_text2 = Gtk.TreeViewColumn("Año"      , renderer_text, text=1)
        column_text  = Gtk.TreeViewColumn("Tipo"     , renderer_text, text=2)
        column_text3 = Gtk.TreeViewColumn("Valor"    , renderer_text, text=3)

        renderer_combo = Gtk.CellRendererCombo()
        renderer_combo.set_property("editable", True)
        renderer_combo.set_property("model", liststore_status)
        renderer_combo.set_property("text-column", 0)
        renderer_combo.set_property("has-entry", False)
        renderer_combo.connect("edited", self.on_combo_changed)

        column_combo = Gtk.TreeViewColumn("Aprobado", renderer_combo, text=4)

        treeview.append_column(column_text)
        treeview.append_column(column_text1)
        treeview.append_column(column_text2)
        treeview.append_column(column_text3)
        treeview.append_column(column_combo)
        # Fin de la tabla


        # renderer_spin = Gtk.CellRendererSpin()
        # renderer_spin.set_property("editable", False)

        # column_spin = Gtk.TreeViewColumn("Valor", renderer_spin, text=1)
        # treeview.append_column(column_spin)
        #Fin de lista de datos

        self.wrapper_grid.attach(treeview,0,1,1,1)
    # def go_back(self, widget):
    #     self.old_window.show()
    #     self.destroy()      

    def on_combo_changed(self, widget, path, text):
        i = self.liststore[path][5]
        db.update_perm_state(self.std_perms[i]['id_permiso'], EstadoPermiso(text[0]))
        self.liststore[path][4] = text   


class InitWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Permisos coordinacion")
        self.set_default_size(320,140)
        self.set_position(Gtk.WindowPosition.CENTER)


        grid = Gtk.Grid()
        grid.props.halign = Gtk.Align.CENTER
        self.grid = grid
        self.add(grid)

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
        Gtk.Window.__init__(self, title="Permisos coordinación")
        self.set_position(Gtk.WindowPosition.CENTER)
        self.connect("delete-event", Gtk.main_quit)

        self.set_default_size(320,200)

        grid = Gtk.Grid()
        self.grid = grid
        self.add(grid)
        grid.props.halign = Gtk.Align.CENTER
        grid.set_row_spacing(10)
        grid.set_column_spacing(4)

        grid.insert_row(0)
        grid.insert_row(1)
        grid.insert_row(2)
        grid.insert_row(3)
        grid.insert_column(0)
        grid.insert_column(1)
        grid.insert_column(2)

        button1 = Gtk.Button(label="Buscar por carnet")
        button2 = Gtk.Button(label="Buscar por materia")
        button3 = Gtk.Button(label="Permisos dos generales")
        button4 = Gtk.Button(label="Permisos de extra creditos")
        button5 = Gtk.Button(label="Permisos de PP")

        button2.type = TipoPermiso.permiso_materia
        button3.type = TipoPermiso.dos_generales
        button4.type = TipoPermiso.limite_creditos
        button5.type = TipoPermiso.pp

        self.student_entry = Gtk.Entry()
        self.class_entry   = Gtk.Entry()

        # inv_box  = Gtk.Box(spacing=4)
        # inv_box.pack_start(button1,True,True,0)
        # inv_box.pack_end(self.student_entry,True,True,3)

        # inv_box2  = Gtk.Box(spacing=4)
        # inv_box2.pack_start(button2,True,True,0)
        # inv_box2.pack_end(self.class_entry,True,True,3)

        # grid.attach(inv_box,1,5,1,1)



        label = Gtk.Label()
        label.set_text("Quedan permisos por procesar.")
        label.set_justify(Gtk.Justification.LEFT)



        # grid.attach(student_entry,2,20,1,1)
        # grid.attach(inv_box ,1,20,1,1)
        # grid.attach(inv_box2,1,25,1,1)

        # Busqueda estudiante
        grid.attach(button1,1,20,2,2)
        grid.attach(self.student_entry,6,20,2,2)
        
        # Busqueda materia
        grid.attach(button2,1,25,2,2)
        grid.attach(self.class_entry,6,25,2,2)

        # Permisos de dos generales
        grid.attach(label  ,1,0,2,2)
        grid.attach(button3,1,30,2,3)
        grid.attach(button4,1,35,2,5)
        grid.attach(button5,1,40,2,3)

        print(button1)
        button1.connect("clicked", self.on_student_clicked)
        button2.connect("clicked", self.on_search_view_clicked)
        button3.connect("clicked", self.on_search_view_clicked)
        button4.connect("clicked", self.on_search_view_clicked)
        button5.connect("clicked", self.on_search_view_clicked)



    def on_student_clicked(self, widget):
        formated_carnet = format_id(self.student_entry.get_text())

        if formated_carnet:
            formated_carnet = int(formated_carnet)
            student_data    = db.get_student(formated_carnet)
            student_perms   = db.get_student_perms(formated_carnet)
            # print(student_data )
            # print(student_perms)

            if (not student_data):
                msgbox("El estudiante " + show_carnet(formated_carnet) + " no existe en la bd")
                return

            if (not student_perms):
                msgbox("El estudiante " + show_carnet(formated_carnet) + " no ha solicitado permisos")
                return

            self.hide()
            new_win = StudentAllPerms(self,student_data[0],student_perms)
            # new_win = SearchWindow(self,"carnet")
            response = new_win.show_all()
        else:
            msgbox("Formato inválido, intente con 0000000,00-00000 ó 00-00000@usb.ve")

    def on_search_view_clicked(self,widget):
        mat = self.class_entry.get_text()
        if widget.type == TipoPermiso.permiso_materia:
            if mat == "":
                # Revisar además si es una materia válida
                msgbox("Debe incluir una materia")
                return 
        else:
            mat = None
        self.hide()
        new_win = SearchWindow(self,widget.type,mat)
        new_win.show_all()



win = InitWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()