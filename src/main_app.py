import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk,GdkPixbuf,Gdk

from coord_crawler import format_id,show_carnet,StudentDownloader
from easygui       import msgbox,ccbox,filesavebox
import os.path
import csv_creator
from perm_store import *
from copy import deepcopy

db = PermStore()
RATIO = 0.75

class Col(Enum):
    carnet    = 0 
    trimestre = 1 
    anio      = 2 
    tipo      = 3 
    valor     = 4 
    estado    = 5 

def triggerCoordDownloader(username, password):
    pass

def extend_instance(obj, cls):
    """Apply mixins to a class instance after creation"""
    base_cls = obj.__class__
    base_cls_name = obj.__class__.__name__
    obj.__class__ = type(base_cls_name, (base_cls, cls),{})

class HeaderBarWindow(Gtk.Window):
    """ Clase de todas las ventanas con boton de retorno """
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
        if self.old_window.is_main():
            self.old_window.refresh_main_lab()
        self.old_window.show()
        self.destroy()

    def is_main():
        return False


class StudentWindow(Gtk.Window):
    """
        Ventana para ver un estudiante
    """
    def __init__(self,old_window,std_data):
        self.old_window   = old_window
        Gtk.Window.__init__(self, title="Permisos coordinación")

        self.connect("delete-event", Gtk.main_quit)

        self.set_default_size(640,200)
        self.set_position(Gtk.WindowPosition.CENTER)

        self.wrapper_grid = Gtk.Grid()
        self.outter_grid  = Gtk.Grid()
        grid = Gtk.Grid()
        grid.props.halign = Gtk.Align.CENTER

        self.add(self.wrapper_grid)

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

    def go_back(self, widget):
        if hasattr(self.old_window,'last_val'):
            print("calling")
            self.old_window.refresh()

        if self.old_window.is_main():
            self.old_window.refresh_main_lab()

        self.old_window.show()
        self.destroy()

    def is_main():
        return False


class WithPermTable():
    def poblate_table(self):
        self.new_val = None
        # Inicio de lista de datos

        # Fill combo with EstadoPermiso
        liststore_status = Gtk.ListStore(str)
        [liststore_status.append((e,)) for e in get_all_names(EstadoPermiso)]


        # tipo, trim, anio, extra_field, aprobado
        liststore      = Gtk.ListStore(int,str,int,str,str,str,int,int)
        self.liststore = liststore

        for i,elem in enumerate(self.std_perms):
            typ = TipoPermiso(elem['tipo'])
            extra_field = ""

            if  (typ == TipoPermiso.permiso_materia):
                extra_field = elem['string_extra']
            elif (typ == TipoPermiso.limite_creditos):
                extra_field = str(elem['int_extra'])

            liststore.append([elem['fk_carnet']
                             ,Trimestre(elem['trimestre']).name
                             ,elem['anio']
                             ,typ.name
                             ,extra_field
                             ,EstadoPermiso(elem['aprobado']).name
                             ,i
                             ,elem['id_permiso']])

        treeview = Gtk.TreeView(model=liststore)
        self.treeview = treeview
        treeview.connect("row-activated", self.clicked_cell)

        renderer_text = Gtk.CellRendererText()
        column_text0 = Gtk.TreeViewColumn("Carnet",    renderer_text, text=Col.carnet.value)
        column_text0.set_clickable(True)
        column_text1 = Gtk.TreeViewColumn("Trimestre", renderer_text, text=Col.trimestre.value)

        # Sirve para ordernar...
        # column_text1.set_clickable(True)
        # column_text1.connect("clicked", self.whatIam)

        column_text2 = Gtk.TreeViewColumn("Año"      , renderer_text, text=Col.anio.value)
        column_text3 = Gtk.TreeViewColumn("Tipo"     , renderer_text, text=Col.tipo.value)
        column_text4 = Gtk.TreeViewColumn("Valor"    , renderer_text, text=Col.valor.value)

        renderer_combo = Gtk.CellRendererCombo()
        renderer_combo.set_property("editable", True)
        renderer_combo.set_property("model", liststore_status)
        renderer_combo.set_property("text-column", 0)
        renderer_combo.set_property("has-entry", False)
        renderer_combo.connect("edited", self.on_combo_changed)

        column_combo = Gtk.TreeViewColumn("Aprobado", renderer_combo, text=5)

        treeview.append_column(column_text0)
        treeview.append_column(column_text1)
        treeview.append_column(column_text2)
        treeview.append_column(column_text3)
        treeview.append_column(column_text4)
        treeview.append_column(column_combo)
        return treeview

    def on_combo_changed(self, widget, path, text):
        self.other_updates(EstadoPermiso(self.liststore[path][5][0])
                          ,EstadoPermiso(text[0]))

        i = self.liststore[path][6]
        db.update_perm_state(self.std_perms[i]['id_permiso'], EstadoPermiso(text[0]))
        self.liststore[path][Col.estado.value] = text
        self.old_window.new_val = EstadoPermiso(text[0])

    def clicked_cell(self,tree,path,col):
        pass

    def other_updates(self,stuff1,stuff2):
        pass


class StudentAllPerms(StudentWindow):
    """Clase de ventana para ver todos los permisos de un estudiante"""
    def __init__(self,old_window,std_data,std_perms):
        StudentWindow.__init__(self,old_window,std_data)
        extend_instance(self,WithPermTable)
        self.std_perms = std_perms
        treeview       = self.poblate_table()
        self.wrapper_grid.attach(treeview,0,1,1,1)


 
class SearchWindow(HeaderBarWindow):
    """ 
        Clase para todas las búsquedas de permisos
    """
    def __init__(self,old_window,perm_type=None,code=None):
        HeaderBarWindow.__init__(self,old_window)
        extend_instance(self,WithPermTable)

        self.perm_type  = perm_type
        self.set_default_size(320,500)
        self.missing_count = None

        main_box     = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(main_box)

        try:
            window_title = perm_type.name
        except Exception as e:
            window_title = "Permisos pendientes"

        description = Gtk.Label()
        description.set_text(window_title)
        description.set_justify(Gtk.Justification.CENTER)
        main_box.pack_start(description,True,True,0)

        # Box for label with count
        self.fst_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,spacing=0)
        main_box.pack_start(self.fst_box,True,True,0)

        # scrollable view para permisos
        scrollable = Gtk.ScrolledWindow()
        scrollable.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        main_box.pack_start(scrollable,True,True,0)


        # Obtener premisos
        if perm_type == TipoPermiso.permiso_materia:
            self.std_perms = db.get_course_perms(code)
        elif perm_type == None:
            self.std_perms = self.old_window.pending
        else:
            self.std_perms = db.get_type_perm(perm_type)

        self.count =  len(list(filter(is_pendiente,self.std_perms)))

        treeview = self.poblate_table()
        scrollable.add(treeview)

        self.update_missing_perms(self.count)


    def update_missing_perms(self,new_val):
        if self.missing_count:
            self.missing_count.destroy()

        missing_count = Gtk.Label()
        extra_s = "s" if new_val != 1 else ""
        missing_count.set_text(str(new_val)+" permiso" + extra_s + " pendiente" + extra_s )
        missing_count.set_justify(Gtk.Justification.CENTER)
        self.missing_count = missing_count

        self.fst_box.pack_start(missing_count,True,True,0)
        missing_count.show()

    def other_updates(self,old,new):
        if old != new:
            if old==EstadoPermiso.pendiente and new!=EstadoPermiso.pendiente:
                self.count -= 1
            elif old!=EstadoPermiso.pendiente and new==EstadoPermiso.pendiente:
                self.count += 1
            else:
                return None
            self.update_missing_perms(self.count)

    def clicked_cell(self,tree,path,col):
        if col.get_title() == "Carnet":
            
            self.last_path = path
            self.last_val  = EstadoPermiso(self.liststore[self.last_path][Col.estado.value][0])

            student_data    = db.get_student(self.liststore[path][Col.carnet.value])
            student_perms   = db.get_perm(self.liststore[path][7])

            self.hide()
            new_win  = StudentAllPerms(self
                                      ,student_data[0]
                                      ,student_perms)
            new_win.show_all()


    def refresh(self):
        print(self.new_val)
        if self.new_val:
            print("refreshing to" + self.new_val.name )
            self.liststore[self.last_path][Col.estado.value] = self.new_val.name
            print("refreshing from" + self.last_val.name +" to " + self.new_val.name  )
            self.other_updates(self.last_val,self.new_val)

        self.new_val  = None
        self.last_val = None



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
        new_win = LoginWindow()
        response = new_win.show_all()
        pass

    def on_button2_clicked(self, widget):
        self.hide()
        new_win = MainWindow()
        response = new_win.show_all()

class LoginWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Permisos coordinación")
        self.set_default_size(320,200)
        self.set_position(Gtk.WindowPosition.CENTER)
        main_box     = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,  spacing=6)
        self.add(main_box)

        buttons_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,spacing=0)

        main_label = Gtk.Label()
        main_label.set_text("Ingrese sus credenciales para acceder al sistema de expendientes.")
        main_label.set_justify(Gtk.Justification.CENTER)

        username_label = Gtk.Label()
        username_label.set_text("Nombre de usuario:")
        username_label.set_justify(Gtk.Justification.LEFT)

        password_label = Gtk.Label()
        password_label.set_text("Contraseña:")
        password_label.set_justify(Gtk.Justification.LEFT)

        self.username_entry = Gtk.Entry()
        self.password_entry = Gtk.Entry()
        self.password_entry.set_visibility(False)

        mod_label = Gtk.Label()
        mod_label.set_text("Seleccione la modalidad de permisos.")
        mod_label.set_justify(Gtk.Justification.CENTER)

        mod_store = Gtk.ListStore(str)
        modalities = ["Todos", "Solo permisos de generales", "Permisos sin los de generales"]
        mod_combo = Gtk.ComboBoxText()
        mod_combo.set_entry_text_column(0)
        mod_combo.connect("changed", self.on_mod_combo_changed)
        for modality in modalities:
            mod_combo.append_text(modality)
        mod_combo.set_active(0)


        ok_button = Gtk.Button(label="Aceptar")
        cancel_button = Gtk.Button(label="Cancelar")

        ok_button.connect("clicked", self.on_ok_button_clicked)
        cancel_button.connect("clicked", self.on_cancel_button_clicked)

        main_box.pack_start(main_label      ,True,True,0)
        main_box.pack_start(username_label  ,True,True,0)
        main_box.pack_start(self.username_entry  ,True,True,0)
        main_box.pack_start(password_label  ,True,True,0)
        main_box.pack_start(self.password_entry  ,True,True,0)
        main_box.pack_start(mod_label       ,True,True,0)
        main_box.pack_start(mod_combo       ,True,True,0)
        main_box.pack_start(buttons_box     ,True,True,0)
        buttons_box.pack_start(ok_button    ,True,True,0)
        buttons_box.pack_start(cancel_button,True,True,0)


    def on_mod_combo_changed(self, combo):
        tree_iter = combo.get_active_iter()
        if tree_iter != None:
            model = combo.get_model()
            mod = model[tree_iter][0]
            print("Selected: mod=%s" % mod)

    def on_ok_button_clicked(self, widget):
        # SE PRENDIO ESTA MIERDAAAAAAAAAA
        triggerCoordDownloader(self.username_entry.get_text(),self.password_entry.get_text())


    def on_cancel_button_clicked(self, widget):
        self.destroy()




class MainWindow(Gtk.Window):
    """
        Ventana principal de búsqueda de permisos y estudiantes
    """
    def __init__(self):
        Gtk.Window.__init__(self, title="Permisos coordinación")
        self.set_position(Gtk.WindowPosition.CENTER)
        self.connect("delete-event", Gtk.main_quit)
        self.set_default_size(320,200)

        main_box     = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,  spacing=6)
        self.add(main_box)

        self.fst_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,spacing=0)

        self.label = None

        std_box   = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,spacing=0)
        class_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,spacing=0)

        button1 = Gtk.Button(label="Buscar por carnet ")
        self.student_entry = Gtk.Entry()
        button2 = Gtk.Button(label="Buscar por materia")
        self.class_entry   = Gtk.Entry()
        button3 = Gtk.Button(label="Permisos dos generales")
        button4 = Gtk.Button(label="Permisos de extra créditos")
        button5 = Gtk.Button(label="Permisos de PP")
        button6 = Gtk.Button(label="Permisos pendientes")
        button7 = Gtk.Button(label="Generar archivos csv")

        button8 = Gtk.FileChooserWidget(gtk.FILE_CHOOSER_ACTION_OPEN)


        button2.type = TipoPermiso.permiso_materia
        button3.type = TipoPermiso.dos_generales
        button4.type = TipoPermiso.limite_creditos
        button5.type = TipoPermiso.pp
        button6.type = None


        # First label
        main_box.pack_start(self.fst_box ,True,True,0)
        self.refresh_main_lab()

        # Composite buttons
        std_box.pack_start(button1           ,True,True,0)
        std_box.pack_start(self.student_entry,True,True,0)
        class_box.pack_start(button2         ,True,True,0)
        class_box.pack_start(self.class_entry,True,True,0)

        # All buttons
        main_box.pack_start(std_box  ,True,True,0)
        main_box.pack_start(class_box,True,True,0)
        main_box.pack_start(button3  ,True,True,0)
        main_box.pack_start(button4  ,True,True,0)
        main_box.pack_start(button5  ,True,True,0)
        main_box.pack_start(button6  ,True,True,0)
        main_box.pack_start(button7  ,True,True,0)


        button1.connect("clicked", self.on_student_clicked)
        button2.connect("clicked", self.on_search_view_clicked)
        button3.connect("clicked", self.on_search_view_clicked)
        button4.connect("clicked", self.on_search_view_clicked)
        button5.connect("clicked", self.on_search_view_clicked)
        button6.connect("clicked", self.on_search_view_clicked)
        button7.connect("clicked", self.on_write_csv_clicked)

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

    def on_write_csv_clicked(self, widget):
        pendientes = len(self.pending)
        if pendientes > 0:  
            msg = "Todavía queda(n) {0} permisos por procesar\n".format(pendientes)
            msg +=  "¿Desea continuar?"
            title = "Por favor confirme"
            if ccbox(msg, title):
                pass 
            else:
                return

        # gen = filesavebox("Archivo de generales"
        #                  ,"Introduzca nombre para guardar el archivo de generales"
        #                  ,filetypes=[" *.csv","Archivo separado por comas"])
        # if not gen:
        #     return

        # mat_perms  = filesavebox("Archivo para permiso de materias"
        #                         ,"Introduzca nombre para guardar el archivo para permiso de materias"
        #                         ,filetypes=[" *.csv","Archivo separado por comas"])
        # if not mat_perms:
        #     return

        gen       = "perm_gen.csv"
        mat_perms = "perm_gen.csv"

        print(gen)
        print(mat_perms)



    def is_main(self):
        return True

    def refresh_main_lab(self):
        perms        = db.get_missign_perms()
        self.pending = perms

        count = len(perms)

        if count == 1:
            plural = [" "+str(count),""]
        else:
            plural = ["n "+str(count),"s"]

        if self.label:
            self.label.destroy()

        self.label = Gtk.Label()
        self.label.set_justify(Gtk.Justification.LEFT)
        
        self.label.set_text("Queda{0} permiso{1} por procesar".format(
                                                         plural[0],plural[1]))

        self.fst_box.pack_start(self.label,True,True,0)
        self.label.show()



win = InitWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
