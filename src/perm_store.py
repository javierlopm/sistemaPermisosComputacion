import sqlite3
from enum import Enum    

# Enums para tipos de permisos
class TipoPermiso(Enum):
    pp              = 'p'
    dos_generales   = 'g'
    limite_creditos = 'l'
    permiso_materia = 'm'
    general_extra   = 'e'
    sin_requisito   = 'r'

# Enums para trimestres
class Trimestre(Enum):
    eneroMarzo          = 'e'
    abrilJulio          = 'a'
    julioAgosto         = 'j'
    septiembreDiciembre = 's'

class EstadoPermiso(Enum):
    aprobado  = 'a'
    negado    = 'n'
    pendiente = 'p'

def is_pendiente(row):
    return row['aprobado'] == "p"

def get_all_names(a_class):
    return [e.name for e in a_class]

# Strings auxiliares para insertar en la base de datos
std_insert = "INSERT OR REPLACE INTO estudiante(carnet,nombre,telefono,correo,comentario) VALUES (?,?,?,?,?)"
per_insert = "INSERT INTO permiso(fk_carnet,tipo,trimestre,anio)               VALUES (?,?,?,?)"
per_int = "INSERT INTO permiso(fk_carnet,tipo,trimestre,anio,int_extra)      VALUES (?,?,?,?,?)"
per_str = "INSERT INTO permiso(fk_carnet,tipo,trimestre,anio,string_extra)   VALUES (?,?,?,?,?)"

updt_perm = "UPDATE permiso SET aprobado = (?) WHERE id_permiso = (?)"


# Strings para consultas
extra_str_qry    = """
    SELECT * 
    FROM permiso p
    WHERE tipo         = (?) AND
          trimestre    = (?) AND
          anio         = (?) AND
          string_extra = (?) """

extra_str_qry_no_trim    = """
    SELECT * 
    FROM permiso p
    WHERE tipo         = (?) AND
          string_extra = (?) """

type_qry = """SELECT *
              FROM permiso
              WHERE tipo      = (?) AND 
                    trimestre = (?) AND
                    anio      = (?)"""

type_qry_no_trim = "SELECT * FROM permiso WHERE tipo = (?)"

pending_qry= """SELECT * 
                FROM permiso 
                WHERE aprobado  = 'p'"""

state_qry = """SELECT * 
               FROM permiso 
               WHERE aprobado  = (?) AND
                     trimestre = (?) AND
                     anio      = (?)"""

std_perms_qry = """ 
    SELECT *
    FROM permiso p
        WHERE fk_carnet = (?) AND
              trimestre = (?) AND
              anio      = (?) """

std_all_perms_qry = """ 
    SELECT *
    FROM permiso p
        WHERE fk_carnet = (?)"""

std_qry = """SELECT *
             FROM estudiante
             WHERE carnet = (?)"""

del_all_perm = "DELETE FROM estudiante"
del_all_std  = "DELETE FROM permiso"

single_perm = """ SELECT * FROM permiso WHERE id_permiso = (?)"""

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

class PermStore():
    """Wrapper de la base de datos de estudiantes y permisos"""
    def __init__(self):
        conn    = sqlite3.connect('permisos.db')
        conn.row_factory = dict_factory
        init_db = open('Sql/create_db.sql', 'r').read()
        c = conn.cursor()
        c.executescript(init_db)
        c.close()

        self.conn = conn 
    
    def insert_student(self,carnet,nombre,telefono,correo,comentario):
        c = self.conn.cursor()
        c.execute(std_insert,(carnet,nombre,telefono,correo,comentario))

        self.conn.commit()
        c.close()

    def insert_perm(self,carnet,tipoPermiso,trim,anio,extra=None):
        c = self.conn.cursor()
        if tipoPermiso == TipoPermiso.limite_creditos:
            c.execute(per_int,(carnet,tipoPermiso.value,trim.value,anio,extra))
        elif tipoPermiso == TipoPermiso.permiso_materia:
            c.execute(per_str,(carnet,tipoPermiso.value,trim.value,anio,extra))
        elif tipoPermiso == TipoPermiso.sin_requisito:
            c.execute(per_str,(carnet,tipoPermiso.value,trim.value,anio,extra))
        else:
            c.execute(per_insert,(carnet,tipoPermiso.value,trim.value,anio))

        self.conn.commit()
        c.close()

    def update_perm_state(self,perm_id,new_state='p'):
        c = self.conn.cursor()
        c.execute(updt_perm,(new_state.value,perm_id))
        self.conn.commit()
        c.close()

    def get_type_perm(self,type_,trimestre=None,anio=None):
        # Procedimiento que obtiene todo los permisos de un tipo dado
        if trimestre:
            return self._run_with_args(type_qry,(type_.value,trimestre.value,anio))
        else:
            return self._run_with_args(type_qry_no_trim,(type_.value))


    def get_missign_perms(self):
        # Procedimiento que obtiene los permisos por aprobar
        return self._run_simple_query(pending_qry)

    def get_course_perms(self,materia,trimestre=None,anio=None):
        if trimestre:
            return self._run_with_args(extra_str_qry
                                      ,  (TipoPermiso.permiso_materia.value
                                         ,trimestre.value
                                         ,anio,materia))
        else:
            return self._run_with_args(extra_str_qry_no_trim
                                      ,  (TipoPermiso.permiso_materia.value
                                         ,materia))

    def get_student(self,carnet):
        return self._run_with_args(std_qry,(carnet,))

    def get_perm(self,id_perm):
        return self._run_with_args(single_perm,(id_perm,))

    def get_student_perms(self,carnet,trimestre=None,anio=None):
        # Procedimiento que obtiene todos los permisos de un estudiante dado su
        # carnet y trimestre
        if trimestre:
            return self._run_with_args(std_perms_qry,(carnet,trimestre.value,anio))
        else:
            return self._run_with_args(std_all_perms_qry,(carnet,))

    def get_with_state(self,state,trimestre,anio):
        return self._run_with_args(state_qry,
                                    (EstadoPermiso.aprobado.value
                                    ,trimestre.value
                                    ,anio))

    def test(self):
        self.insert_student(1110552
                           ,"Javier López"
                           ,"04129349938"
                           ,"javierloplom@gmail.com"
                           ,"Por favor podrían agregar mi permiso? es de suma importancia para salvar a mi perrito y a mi gato y para resolver la complicada situación de Siria"
                           )

        self.insert_student(1110584
                           ,"Carlos Martínez"
                           ,"0424222222"
                           ,"1110584@usb.ve"
                           ,"")

        # Extra credito
        self.insert_perm(1110552
                        ,TipoPermiso.limite_creditos
                        ,Trimestre.septiembreDiciembre
                        ,2016
                        ,18)

        self.insert_perm(1110552
                        ,TipoPermiso.permiso_materia
                        ,Trimestre.septiembreDiciembre
                        ,2016
                        ,"CI5438")

        self.insert_perm(1110584
                        ,TipoPermiso.permiso_materia
                        ,Trimestre.septiembreDiciembre
                        ,2016
                        ,"CI5438")

        self.insert_perm(1110552
                        ,TipoPermiso.permiso_materia
                        ,Trimestre.septiembreDiciembre
                        ,2016
                        ,"CI4722")

        self.update_perm_state(1,EstadoPermiso.aprobado)
        self.update_perm_state(2,EstadoPermiso.negado)
        
        print("Permisos de estudiante")
        print(self.get_student_perms(1110552,Trimestre.septiembreDiciembre,2016))
        print("Permisos de materia CI5438")
        print(self.get_course_perms("CI5438",Trimestre.septiembreDiciembre,2016))
        print("Permisos de materia CI4722")
        print(self.get_course_perms("CI4722",Trimestre.septiembreDiciembre,2016))
        print("Permisos pendietes")
        print(self.get_missign_perms())
        # self.delete_all()
        print("DONE")


    def delete_all(self):
        c = self.conn.cursor()
        c.execute(del_all_perm)
        c.execute(del_all_std)
        self.conn.commit()
        c.close()



    # Helpers
    def _run_simple_query(self,string):
        c = self.conn.cursor()
        c.execute(string)
        rows  = c.fetchall()
        c.close()
        return rows

    def _run_with_args(self,string,tuple_):
        c = self.conn.cursor()
        c.execute(string,tuple_)
        rows  = c.fetchall()
        c.close()
        return rows

    # negar todos los pendientes de una materia
    # borrar trimestre y anio
