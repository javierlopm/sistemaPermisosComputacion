import sqlite3
from enum import Enum

# Enums para tipos de permisos
class TipoPermiso(Enum):
    pp              = 0
    dos_generales   = 1
    limite_creditos = 2
    permiso_materia = 3
    # extra_plan_id      = 3
    # extra_plan_general = 3
    # otro_extraplan     = 3

# Enums para trimestres
class Trimestre(Enum):
    eneroMarzo  = 0
    abrilJulio  = 1
    julioAgosto = 2
    septiembreDiciembre = 3

# Strings auxiliares para insertar en la base de datos
std_insert = """INSERT OR REPLACE INTO estudiante(carnet,nombre,telefono,correo) 
                VALUES (?,?,?,?)"""
per_insert = "INSERT INTO permiso(fk_carnet,tipo,trimestre,anio)    VALUES (?,?,?,?)"
num_cred   = "INSERT INTO permiso_creditos(id_permiso,num_creditos) VALUES (?,?)"
perm_mat   = "INSERT INTO permiso_materia(id_permiso,materia)       VALUES (?,?)"


# Strings para consultas
mat_qry    = """SELECT * 
                FROM permiso p
                CROSS JOIN permiso_materia pa 
                WHERE pa.materia  == (?) AND
                      p.trimestre == (?) AND
                      p.anio      == (?)"""

num_cred_qry = """SELECT *
                  FROM permiso p 
                  CROSS JOIN permiso_creditos pc"""

pending_qry= """SELECT * 
                FROM permiso 
                WHERE aprobado IS NULL"""

perm_type_qry = """s"""

std_perms_qry = """ 
    SELECT *
    FROM permiso p
    LEFT JOIN permiso_creditos pc ON p.id_permiso == pc.id_permiso
    LEFT JOIN permiso_materia  pm ON p.id_permiso == pm.id_permiso
    LEFT JOIN estudiante       e  ON p.fk_carnet  == e.carnet 
        WHERE e.carnet    == (?) AND
              p.trimestre == (?) AND0   
              p.anio      == (?) """




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
        c.execute(per_insert,(carnet,tipoPermiso.value,trim.value,anio))

        lastrowid = c.lastrowid

        if tipoPermiso == TipoPermiso.limite_creditos:
            c.execute(num_cred,(lastrowid,extra))
        elif tipoPermiso == TipoPermiso.permiso_materia:
            c.execute(perm_mat,(lastrowid,extra))

        self.conn.commit()
        c.close()



    def get_cred_perm(self):
        # Procedimiento que obtiene todo los permisos de extra/infra creditos
        return _run_simple_query(num_cred)


    def get_missign_perms(self):
        # Procedimiento que obtiene los permisos faltantes
        return _run_simple_query(pending_qry)

    def get_course_perms(self,materia):
        return _run_with_args(mat_qry,(materia,trimestre.value,anio))

    def get_student_perms(self,carnet,trimestre,anio):
        # Procedimiento que obtiene todos los permisos de un estudiante dado su
        # carnet y trimestre
        return _run_with_args(std_perms_qry,(carnet,trimestre.value,anio))



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


    # editar permiso individual
    # negar todos los pendientes de una materia
    # borrar trimestre y anio
