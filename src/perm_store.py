import sqlite3
from enum import Enum

std_insert = "INSERT OR REPLACE INTO estudiante(carnet,nombre,telefono,correo) VALUES (?,?,?,?)"
per_insert = "INSERT INTO permiso(fk_carnet,tipo,trimestre,anio)    VALUES (?,?,?,?)"
num_cred   = "INSERT INTO permiso_creditos(id_permiso,num_creditos) VALUES (?,?)"
perm_mat   = "INSERT INTO permiso_materia(id_permiso,materia)       VALUES (?,?)"

mat_qry    = """SELECT * 
                FROM permiso p
                CROSS JOIN permiso_materia pa 
                WHERE pa.materia == (?)"""

num_cred_qry = """SELECT *
                  FROM permiso p 
                  CROSS JOIN permiso_creditos pc"""

pending_qry= """SELECT * 
                FROM permiso 
                WHERE aprobado IS NULL"""

perm_type_qry = """s"""

std_perms_qry = """s"""


class TipoPermiso(Enum):
    pp              = 0
    dos_generales   = 1
    limite_creditos = 2
    permiso_materia = 3
    # extra_plan_id      = 3
    # extra_plan_general = 3
    # otro_extraplan     = 3

class Trimestre(Enum):
    eneroMarzo  = 0
    abrilJulio  = 1
    julioAgosto = 2
    septiembreDiciembre = 3

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

    def get_course_perms(self,materia):
        c = self.conn.cursor()
        c.execute(mat_qry,(materia,) )
        rows  = c.fetchall()
        c.close()
        return rows

    def get_cred_perm(self):
        c = self.conn.cursor()
        c.execute(num_cred)
        rows  = c.fetchall()
        c.close()
        return rows

    def get_missign_perms(self):
        c = self.conn.cursor()
        c.execute(pending_qry)
        rows  = c.fetchall()
        c.close()
        return rows

    # editar permiso individual
    # negar todos los pendientes de una materia
