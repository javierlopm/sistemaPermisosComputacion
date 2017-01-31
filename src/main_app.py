#! /usr/bin/python3
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk,GdkPixbuf,Gdk

from coord_crawler import format_id,show_carnet,StudentDownloader
from easygui       import msgbox,ccbox,filesavebox
import os.path
import sys
from csv_creator import CsvCreator
from perm_store import *
from copy import deepcopy
import subprocess
db = PermStore()
RATIO = 0.75

# TODO
# Advertencia al cargar permisos con datos en tabla de permisos
# Comentar codigo
# Hacer informe y manuales


class Col(Enum):
    carnet    = 0 
    trimestre = 1 
    anio      = 2 
    tipo      = 3 
    valor     = 4 
    estado    = 5 


def purge(dir, pattern):
    import os, re
    for f in os.listdir(dir):
        if re.search(pattern, f):
            os.remove(os.path.join(dir, f))

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

    def is_main(self):
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

        from re import sub,DOTALL
        # Inicio de lista de datos
        liststore = Gtk.ListStore(str, str)
        for elem in std_data.items():
            # if len
            if elem[0]=="comentario":
                comment = sub("(.{32})", "\\1\n", elem[1], 0, DOTALL)
                continue
            liststore.append([ elem[0],str(elem[1]) ] )

        liststore.append([ "comentario" , comment ] )
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
        str_image = 'graphs_manager/grafosPNG/'+show_carnet(std_data['carnet'])+".png"
        str_image = str_image if os.path.isfile(str_image) else "graphs_manager/grafosPNG/noFile.png"

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

    def is_main(self):
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

            if  (typ == TipoPermiso.permiso_materia) or (typ == TipoPermiso.sin_requisito) or (typ == TipoPermiso.extraplan) or (typ == TipoPermiso.xplan_gen_gen) or (typ == TipoPermiso.xplan_d_gen):
                extra_field = elem['string_extra']
            elif (typ == TipoPermiso.limite_creditos) or (typ == TipoPermiso.pp):
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
        self.fst_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=0)
        main_box.pack_start(self.fst_box,True,True,0)

        # scrollable view para permisos
        scrollable = Gtk.ScrolledWindow(vexpand=True)
        scrollable.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)


        main_box.pack_start(scrollable,True,True,0)

        # Obtener premisos de tipo materia y con código
        if perm_type == TipoPermiso.permiso_materia and code:
            self.std_perms = db.get_course_perms(code)
        # Mostrar lista de permisos calculada en otra vista
        elif perm_type == None:
            self.std_perms = self.old_window.pending
        # Mostrar lista de permisos con un estado dado
        elif perm_type.name in get_all_names(EstadoPermiso):
            self.std_perms = db.get_with_state(perm_type)
        # Mostrar lista de permisos de un tipo cualquiera
        else:
            self.std_perms = db.get_type_perm(perm_type)

        self.count   =  len(list(filter(is_pendiente,self.std_perms)))
        self.count_a =  len(list(filter(is_aprobado,self.std_perms)))

        treeview = self.poblate_table()
        scrollable.add(treeview)


        self.update_missing_perms(self.count,self.count_a)


    def update_missing_perms(self,new_val,new_val_a):
        if self.missing_count:
            self.missing_count.destroy()
            self.aprobado_count.destroy()

        missing_count = Gtk.Label()
        extra_s = "s" if new_val != 1 else ""
        missing_count.set_text(str(new_val)+" permiso" + extra_s + " pendiente" + extra_s )
        missing_count.set_justify(Gtk.Justification.CENTER)
        self.missing_count = missing_count

        aprobado_count = Gtk.Label()
        extra_s = "s" if new_val_a != 1 else ""
        aprobado_count.set_text(str(new_val_a)+" permiso" + extra_s + " aprobado" + extra_s )
        aprobado_count.set_justify(Gtk.Justification.CENTER)
        self.aprobado_count = aprobado_count

        self.fst_box.pack_start(missing_count,True,True,0)
        self.fst_box.pack_start(aprobado_count,True,True,0)
        missing_count.show()
        aprobado_count.show()

    def other_updates(self,old,new):
        if old != new:
            if old==EstadoPermiso.pendiente and new!=EstadoPermiso.pendiente:
                self.count -= 1
            elif old!=EstadoPermiso.pendiente and new==EstadoPermiso.pendiente:
                self.count += 1
            else:
                return None

            if old==EstadoPermiso.aprobado and new!=EstadoPermiso.aprobado:
                self.count_a -= 1
            elif old!=EstadoPermiso.aprobado and new==EstadoPermiso.aprobado:
                self.count_a += 1
            else:
                return None
            self.update_missing_perms(self.count,self.count_a)

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
        button3 = Gtk.Button(label="Borrar permisos actuales")

        grid.attach(label,0,0,2,2)
        grid.attach(button1,0,5,2,2)
        grid.attach(button2,0,25,2,2)
        grid.attach(button3,0,45,2,2)

        button1.connect("clicked", self.on_button1_clicked)
        button2.connect("clicked", self.on_button2_clicked)
        button3.connect("clicked", self.on_button3_clicked)

    def on_button1_clicked(self, widget):
        new_win = LoginWindow()
        response = new_win.show_all()
        pass

    def on_button2_clicked(self, widget):
        self.hide()
        new_win = MainWindow()
        response = new_win.show_all()

    def on_button3_clicked(self, widget):
        msg = "Se eliminarán todos los permisos no expotados a csv "
        msg +=  "¿Desea continuar?"
        title = "Por favor confirme"
        if ccbox(msg, title):
            db.delete_all()
            msgbox("Eliminado con éxito")
        else:
            return

class LoginWindow(Gtk.Window):

    def __init__(self):
        self.mod_dict = {
            "Todos" : 1,
            "Solo permisos de generales" : 2,
            "Permisos sin los de generales" : 3
        }

        self.processing = False

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
        self.username_entry.set_text("coord-comp")
        self.password_entry = Gtk.Entry()
        self.password_entry.set_visibility(False)

        mod_label = Gtk.Label()
        mod_label.set_text("Seleccione la modalidad de permisos.")
        mod_label.set_justify(Gtk.Justification.CENTER)

        mod_store = Gtk.ListStore(str)
        modalities = ["Todos", "Solo permisos de generales", "Permisos sin los de generales"]
        self.mod_combo = Gtk.ComboBoxText()
        self.mod_combo.set_entry_text_column(0)
        self.mod_combo.connect("changed", self.on_mod_combo_changed)
        for modality in modalities:
            self.mod_combo.append_text(modality)
        self.mod_combo.set_active(0)


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
        main_box.pack_start(self.mod_combo       ,True,True,0)
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
        if self.processing:
            return

        self.processing = True

        tree_iter = self.mod_combo.get_active_iter()
        usr = self.username_entry.get_text()
        psw = self.password_entry.get_text()

        from check_answers import AnswersChecker

        if tree_iter != None and usr != "" and psw != "":
            model = self.mod_combo.get_model()
            mod = model[tree_iter][0]

            ans_checker = AnswersChecker(usr, psw, self.mod_dict[mod])
            status = ans_checker.answers_downloader()

            if status:
                msgbox("Permisos descargados.")


            self.destroy()
        else:
            msgbox("Existen campos sin llenar.")

        self.processing = False


    def on_cancel_button_clicked(self, widget):
        self.destroy()


class CsvWindow(HeaderBarWindow):
    """ 
        Clase para todas las búsquedas de permisos
    """
    def __init__(self,old_window):
        HeaderBarWindow.__init__(self,old_window)

        self.set_default_size(600,120)

        main_box     = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(main_box)

        # Permisos de generales
        gen_box       = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,spacing=0)
        lab_gen       = Gtk.Label()
        self.gen_perm = Gtk.Entry()
        lab_gen.set_text("Archivo de generales:")
        self.gen_perm.set_text("permisos_generales.csv")

        # Permisos de materias
        all_perm_box  = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,spacing=0)
        lab_all_perm  = Gtk.Label()
        self.all_perm = Gtk.Entry()
        lab_all_perm.set_text("Archivo de materias:")
        self.all_perm.set_text("permisos_materias.csv")

        # Memos
        memo_box  = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,spacing=0)
        lab_memo  = Gtk.Label()
        self.memo = Gtk.Entry()
        lab_memo.set_text("Memo de generales:")
        self.memo.set_text("memo_dace.csv")



        trim_box  = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,spacing=0)

        trim_combo = Gtk.ComboBoxText()
        trim_combo.set_entry_text_column(0)
        trim_combo.connect("changed", self.on_trim_combo_changed)
        for t in Trimestre:
            trim_combo.append_text(t.name)
        trim_combo.set_active(0)

        from datetime import datetime
        year = datetime.now().year

        adjustment = Gtk.Adjustment(2015, 2015, 2199, 1, 10, 0)
        self.spinbutton = Gtk.SpinButton()
        self.spinbutton.set_adjustment(adjustment)
        self.spinbutton.set_numeric(True)
        self.spinbutton.set_value(year)


        button1 = Gtk.Button(label="Generar archivo generales")
        button2 = Gtk.Button(label="Generar archivo materias")
        button_del = Gtk.Button(label="Eliminar csv en este directorio")

        gen_box.pack_start      (lab_gen      ,True,True,0)
        gen_box.pack_start      (self.gen_perm,True,True,0)
        main_box.pack_start     (gen_box      ,True,True,0)
        all_perm_box.pack_start (lab_all_perm ,True,True,0)
        all_perm_box.pack_start (self.all_perm,True,True,0)
        memo_box.pack_start     (lab_memo     ,True,True,0)
        memo_box.pack_start     (self.memo    ,True,True,0)
        trim_box.pack_start     (trim_combo   ,True,True,0)
        trim_box.pack_start     (self.spinbutton,True,True,0)
        main_box.pack_start     (all_perm_box ,True,True,0)
        main_box.pack_start     (memo_box     ,True,True,0)
        main_box.pack_start     (trim_box     ,True,True,0)
        main_box.pack_start     (button1      ,True,True,0)
        main_box.pack_start     (button2      ,True,True,0)
        main_box.pack_start     (button_del   ,True,True,0)

        button1.connect("clicked", self.on_write_press,0)
        button2.connect("clicked", self.on_write_press,1)
        button_del.connect("clicked", self.on_delete_csv)
        # self.gen_perm.connect("focus-in-event", self.on_text_press)
        # self.all_perm.connect("focus-in-event", self.on_text_press)

    def on_delete_csv(self, widget):
        msg = "Se eliminarán todas las tablas csv del directorio del sistema.\n"
        msg +=  "¿Desea continuar?"
        title = "Por favor confirme"
        if ccbox(msg, title):
            purge('.','.*\.csv')
        else:
            return

    def on_trim_combo_changed(self, combo):
            tree_iter = combo.get_active_iter()
            if tree_iter != None:
                model = combo.get_model()
                mod = model[tree_iter][0]
                self.trim_search = Trimestre(mod[0])

    def on_write_press(self,widget,creator_type):
        print("writing to {} and {} and {} for {} and {}".format(
                self.gen_perm.get_text()
                ,self.all_perm.get_text()
                ,self.memo.get_text()
                ,self.trim_search.name
                ,str(self.spinbutton.get_value_as_int())))

        anio = self.spinbutton.get_value_as_int()

        aprobados = db.get_with_state(EstadoPermiso.aprobado
                                     ,self.trim_search
                                     ,anio)
        if len(aprobados) == 0:
            msgbox("No se encontraron permisos en {0} {1}".format(self.trim_search,anio))
        else:
            gen_count  = 0
            memo_count = 0
            mat_count  = 0

            csv = CsvCreator(self.gen_perm.get_text()
                            ,self.all_perm.get_text()
                            ,self.memo.get_text()
                            ,self.trim_search.value
                            ,anio)

            for perm in aprobados:
                t_perm = TipoPermiso(perm['tipo'])
                if creator_type == 0:
                    if  t_perm == TipoPermiso.dos_generales:
                        csv.write_gen(str(perm['fk_carnet']),general="E2")

                        student = db.get_student(perm['fk_carnet'])[0]
                        csv.write_memo(show_carnet(perm['fk_carnet'])
                                      ,student['nombre']
                                      ,TipoPermiso(perm['tipo']).memo_name()
                                      ,Trimestre(perm['trimestre']).memo_name())
                        memo_count += 1
                        gen_count  += 1
                    elif t_perm == TipoPermiso.limite_creditos:
                        csv.write_gen(str(perm['fk_carnet'])
                                     ,limite_cred=str(perm['int_extra']))
                        gen_count += 1 
                    elif t_perm == TipoPermiso.pp:
                        csv.write_gen(str(perm['fk_carnet']),pp=str(perm['int_extra']))
                        gen_count += 1 
                    elif (t_perm in [TipoPermiso.general_extra
                                    ,TipoPermiso.xplan_gen_gen
                                    ,TipoPermiso.xplan_d_gen
                                    ,TipoPermiso.extraplan]):
                        # Escribir en permiso de materia
                        csv.write_perm(perm['string_extra'],str(perm['fk_carnet']))
                        
                        # Escribir memo
                        student = db.get_student(perm['fk_carnet'])[0]
                        csv.write_memo(show_carnet(perm['fk_carnet'])
                                      ,student['nombre']
                                      ,t_perm.memo_name()
                                      ,Trimestre(perm['trimestre']).memo_name())
                        memo_count += 1
                        mat_count  += 1
                else:
                    if t_perm == TipoPermiso.permiso_materia:
                        csv.write_perm(perm['string_extra'],str(perm['fk_carnet']))
                        mat_count += 1                     
                    elif t_perm == TipoPermiso.sin_requisito:
                        csv.write_perm(perm['string_extra'],str(perm['fk_carnet']))
                        mat_count += 1

            csv.end_writer()

            msg_t ="Éxito se procesaron:"
            msg_t += "{} permiso(s) de generales\n".format(gen_count) if gen_count > 0 else ""
            msg_t += "{} permiso(s) de materias\n".format(mat_count)  if mat_count > 0 else ""
            msg_t += "{} memo(s)\n".format(memo_count) if memo_count > 0 else ""

            print("Got {}, {} and {}\n".format(gen_count,mat_count,memo_count))

            if gen_count==0 and mat_count==0 and memo_count==0:
                msg_t = "No se procesó ningún permiso"

            msgbox(msg_t)


    def on_text_press(self,widget,cosa):
        dialog = Gtk.FileChooserDialog("Please choose a file", self,
                 Gtk.FileChooserAction.SAVE,
                 (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                  Gtk.STOCK_SAVE_AS, Gtk.ResponseType.ACCEPT))
        dialog.set_current_folder("~")
        dialog.set_current_folder(widget.get_text())

        filter = Gtk.FileFilter()
        filter.set_name("Comma separated file")
        filter.add_pattern("*.csv")
        dialog.add_filter(filter)

        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            widget.set_text(dialog.get_filename())



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

        name_box   = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,spacing=0)
        std_box   = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,spacing=0)
        class_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,spacing=0)

        button0 = Gtk.Button(label="Buscar por nombres/apellidos")
        self.name_entry = Gtk.Entry()
        button1 = Gtk.Button(label="Buscar por carnet ")
        self.student_entry = Gtk.Entry()
        button2 = Gtk.Button(label="Buscar por materia")
        self.class_entry   = Gtk.Entry()
        button6 = Gtk.Button(label="Permisos pendientes")

        button_csv = Gtk.Button(label="Generar archivos csv")
        button_em  = Gtk.Button(label="Enviar correos")

        # Combo box búsqueda por tipos
        search_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,spacing=0)
        buttonS    = Gtk.Button(label="Buscar tipo")

        typ_store = Gtk.ListStore(str,str)
        [typ_store.append(e) for e in get_all_tuples(TipoPermiso)]

        type_combo = Gtk.ComboBox.new_with_model_and_entry(typ_store)
        type_combo.set_entry_text_column(0)
        self.combo = type_combo

        # Combo box búsqueda por estado de los permisos
        search_boxSE = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,spacing=0)
        buttonSE     = Gtk.Button(label="Buscar con estado")

        state_store = Gtk.ListStore(str,str)
        [state_store.append(e) for e in get_all_tuples(EstadoPermiso)]

        state_combo = Gtk.ComboBox.new_with_model_and_entry(state_store)
        state_combo.set_entry_text_column(0)
        self.combo_s = state_combo



        button2.type = TipoPermiso.permiso_materia
        button6.type = None



        # First label
        main_box.pack_start(self.fst_box ,True,True,0)
        self.refresh_main_lab()

        # Composite buttons
        name_box.pack_start(button0           ,True,True,0)
        name_box.pack_start(self.name_entry,True,True,0)

        std_box.pack_start(button1           ,True,True,0)
        std_box.pack_start(self.student_entry,True,True,0)
        class_box.pack_start(button2         ,True,True,0)
        class_box.pack_start(self.class_entry,True,True,0)
        search_box.pack_start(buttonS,True,True,0)
        search_box.pack_start(type_combo,True,True,0)
        search_boxSE.pack_start(buttonSE,True,True,0)
        search_boxSE.pack_start(state_combo,True,True,0)


        # All buttons
        main_box.pack_start(std_box  ,True,True,0)
        main_box.pack_start(name_box  ,True,True,0)
        main_box.pack_start(class_box,True,True,0)
        main_box.pack_start(search_box,True,True,0)
        main_box.pack_start(search_boxSE,True,True,0)
        main_box.pack_start(button6  ,True,True,0)
        main_box.pack_start(button_csv  ,True,True,0)
        main_box.pack_start(button_em  ,True,True,0)




        button0.connect("clicked", self.on_name_clicked)
        button1.connect("clicked", self.on_student_clicked)
        button2.connect("clicked", self.on_search_view_clicked)
       
        button6.connect("clicked", self.on_search_view_clicked)

        button_csv.connect("clicked", self.on_write_csv_clicked)
        button_em.connect("clicked", self.on_email_send)
        type_combo.connect("changed", self.on_combo_changed,True)
        state_combo.connect("changed", self.on_combo_changed,False)
        buttonS.connect("clicked",    self.on_combo_search,True)
        buttonSE.connect("clicked",   self.on_combo_search,False)

    def on_combo_changed(self, combo,is_type):
        tree_iter = combo.get_active_iter()
        if tree_iter != None:
            model = combo.get_model()
            mod   = model[tree_iter][1]

            if is_type:
                self.active_type = TipoPermiso(mod)
            else:
                self.active_state = EstadoPermiso(mod)

    def on_email_send(self,widget):
        new_win = SendEmailsWindow()
        response = new_win.show_all()

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

    def on_name_clicked(self, widget):
        name =  self.name_entry.get_text()

        result = db.get_by_names(name)

        if result:
            # formated_carnet = format_id(result[0]['carnet'])
            student_perms   = db.get_student_perms(result[0]['carnet'])
            self.hide()
            new_win = StudentAllPerms(self,result[0],student_perms)
            response = new_win.show_all()
        else:
            msgbox("No se encontro a ningún estudiante con nombre {}".format(name))
    
    def on_combo_search(self,widget,is_type):
        mat = None
        self.hide()

        if is_type:
            new_win = SearchWindow(self,self.active_type,mat)
        else:
            new_win = SearchWindow(self,self.active_state,mat)
        new_win.show_all()

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

        self.hide()
        csv_window = CsvWindow(self)
        csv_window.show_all()



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

class SendEmailsWindow(Gtk.Window):

    def __init__(self):

        self.processing = False

        Gtk.Window.__init__(self, title="Permisos coordinación")
        self.set_default_size(320,200)
        self.set_position(Gtk.WindowPosition.CENTER)
        main_box     = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,  spacing=6)
        self.add(main_box)

        buttons_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,spacing=0)

        main_label = Gtk.Label()
        main_label.set_text("Ingrese sus credenciales para enviar los correos.")
        main_label.set_justify(Gtk.Justification.CENTER)

        username_label = Gtk.Label()
        username_label.set_text("Correo electronico:")
        username_label.set_justify(Gtk.Justification.LEFT)

        password_label = Gtk.Label()
        password_label.set_text("Contraseña:")
        password_label.set_justify(Gtk.Justification.LEFT)

        self.username_entry = Gtk.Entry()
        self.username_entry.set_text("coord-comp@usb.ve")
        self.password_entry = Gtk.Entry()
        self.password_entry.set_visibility(False)



        ok_button = Gtk.Button(label="Aceptar")
        cancel_button = Gtk.Button(label="Cancelar")

        ok_button.connect("clicked", self.on_ok_button_clicked)
        cancel_button.connect("clicked", self.on_cancel_button_clicked)

    

        main_box.pack_start(main_label      ,True,True,0)
        main_box.pack_start(username_label  ,True,True,0)
        main_box.pack_start(self.username_entry  ,True,True,0)
        main_box.pack_start(password_label  ,True,True,0)
        main_box.pack_start(self.password_entry  ,True,True,0)
        main_box.pack_start(buttons_box     ,True,True,0)
        buttons_box.pack_start(ok_button    ,True,True,0)
        buttons_box.pack_start(cancel_button,True,True,0)


    def on_ok_button_clicked(self, widget):
        if self.processing:
            return

        self.processing = True
        gmail_sender = self.username_entry.get_text()
        gmail_passwd = self.password_entry.get_text()


        if gmail_sender != "" and gmail_passwd != "":
            print("pre import")
            import smtplib
            print("post import")

            SUBJECT = 'Solicitud de permisos de coordinacion de Ingenieria de la Computacion'

            # Gmail Sign In

            worked = False
            while (not worked):
                try:
                    print("server")
                    server = smtplib.SMTP('smtp.gmail.com',587,timeout=5)
                    print("ehlo")
                    server.ehlo()
                    print("startssl")
                    server.starttls()
                    print("login")
                    server.login(gmail_sender, gmail_passwd)
                    print("done")
                    worked = True
                except:
                    print("error al iniciar sesion, intentando de nuevo")

            for carnet,permisos in db.get_rejected():
                print("Ahora "+str(show_carnet(carnet)))
                TEXT = "De los permisos solicitados, no se aprobaron los siguientes:\n"
                conjunto_correos = set([])
                for p in permisos:
                    # print(p)
                    otro_correo = p['correo']
                    if otro_correo is not "": conjunto_correos.add(otro_correo)
                    TEXT += TipoPermiso(p['tipo']).mensaje_permiso((p['string_extra'] or "" )+str(p['int_extra'] or ""))
                conjunto_correos.add(show_carnet(carnet) + "@usb.ve")
                TO = list(conjunto_correos)
                print(TO)


                BODY = '\r\n'.join(['From: %s' % gmail_sender,
                                   'Subject: %s' % SUBJECT,
                                   '', TEXT])
                print(BODY)
                worked = False
                while (not worked):
                    try:
                        #print("El correo no se esta mandando porque esto es una prueba")
                        server.sendmail(gmail_sender, TO, BODY)
                        worked = True
                    except:
                        print("Unexpected error:", sys.exc_info()[0])
                        print("ups")

            server.quit()
            self.destroy()
        else:
            msgbox("Existen campos sin llenar.")

        self.processing = False


    def on_cancel_button_clicked(self, widget):
        self.destroy()

win = InitWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
