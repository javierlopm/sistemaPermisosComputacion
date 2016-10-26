import sqlite3
from enum import Enum

# Enums para tipos de permisos
class TipoPermiso(Enum):
    pp              = 'p'
    dos_generales   = 'g'
    limite_creditos = 'l'
    permiso_materia = 'm'

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

# Strings auxiliares para insertar en la base de datos
std_insert = "INSERT OR REPLACE INTO estudiante(carnet,nombre,telefono,correo) VALUES (?,?,?,?)"
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

type_qry = """SELECT *
              FROM permiso
              WHERE tipo      = (?) AND 
                    trimestre = (?) AND
                    anio      = (?)"""

pending_qry= """SELECT * 
                FROM permiso 
                WHERE aprobado  = 'p' AND 
                      trimestre = (?) AND
                      anio      = (?) """

std_perms_qry = """ 
    SELECT *
    FROM permiso p
        WHERE fk_carnet = (?) AND
              trimestre = (?) AND
              anio      = (?) """

del_all_perm = "DELETE FROM estudiante"
del_all_std  = "DELETE FROM permiso"


class PermStore():
    """Wrapper de la base de datos de estudiantes y permisos"""
    def __init__(self):
        conn    = sqlite3.connect('permisos.db')
        init_db = open('Sql/create_db.sql', 'r').read()
        c = conn.cursor()
        c.executescript(init_db)
        c.close()

        self.conn = conn 
    
    def insert_student(self,carnet,nombre,telefono,correo):
        c = self.conn.cursor()
        c.execute(std_insert,(carnet,nombre,telefono,correo))

        self.conn.commit()
        c.close()

    def insert_perm(self,carnet,tipoPermiso,trim,anio,extra=None):
        c = self.conn.cursor()

        if tipoPermiso == TipoPermiso.limite_creditos:
            c.execute(per_int,(carnet,tipoPermiso.value,trim.value,anio,extra))
        elif tipoPermiso == TipoPermiso.permiso_materia:
            c.execute(per_str,(carnet,tipoPermiso.value,trim.value,anio,extra))
        else:
            c.execute(per_insert,(carnet,tipoPermiso.value,trim.value,anio))

        self.conn.commit()
        c.close()

    def update_perm_state(self,perm_id,new_state=None):
        c = self.conn.cursor()
        c.execute(updt_perm,(new_state.value,perm_id))
        self.conn.commit()
        c.close()

    def get_type_perm(self,type_,trimestre,anio):
        # Procedimiento que obtiene todo los permisos de un tipo dado
        return self._run_with_args(type_qry,(type_,trimestre.value,anio))


    def get_missign_perms(self,trimestre,anio):
        # Procedimiento que obtiene los permisos por aprobar
        return self._run_with_args(pending_qry,(trimestre.value,anio))

    def get_course_perms(self,materia,trimestre,anio):
        return self._run_with_args(extra_str_qry,(TipoPermiso.permiso_materia.value
                                            ,trimestre.value
                                            ,anio,materia))

    def get_student_perms(self,carnet,trimestre,anio):
        # Procedimiento que obtiene todos los permisos de un estudiante dado su
        # carnet y trimestre
        return self._run_with_args(std_perms_qry,(carnet,trimestre.value,anio))

    def test(self):
        self.insert_student(1110552
                           ,"Javier López"
                           ,"04129349938"
                           ,"javierloplom@gmail.com")

        self.insert_student(1110584
                           ,"Carlos Martínez"
                           ,"0424222222"
                           ,"1110584@usb.ve")

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
        print(self.get_missign_perms(Trimestre.septiembreDiciembre,2016))
        self.delete_all()
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