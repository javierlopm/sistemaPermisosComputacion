# -*- coding: utf-8 -*-
import csv

PERM_HEADER = ["COD_ASIGNATURA"
              ,"ANIO_CARNET" 
              ,"NUM_CARNET"
              ,"SIGLO"
              ,"ANIOP"
              ,"MESIP"
              ,"MESFP"
              ,"BLOQUE"
              ,"SECCION"
              ,"NRO_CREDITOS"
              ,"PERMISO"
              ,"RENGLON"
              ,"NOTA_ASIGNATURA"
              ,"IND_NOTA_SIN_EFECTO"]

GEN_HEADER = ["ANIO_CARNET"
             ,"NUM_CARNET"
             ,"SIGLO"
             ,"ANIOP"
             ,"MESIP"
             ,"MESFP"
             ,"SITUACION"
             ,"SITUACIONINSCRIP"
             ,"GENERAL"
             ,"LIMITE CR"
             ,"NOTA_X_CREDITO_PONDERADO"
             ,"TOTAL_CREDITOS"
             ,"PP"]



class CsvCreator():
    def __init__(self,gen_file,perm_files,trim,anio):
        self.f1 = open(gen_file  ,"w")
        self.f2 = open(perm_files,"w")
        self.perm_writer  = csv.writer(self.f2,delimiter=',')
        self.gen_writer   = csv.writer(self.f1,delimiter=',')

        self.anio = anio

        self.perm_writer.writerow(PERM_HEADER)
        self.gen_writer.writerow(GEN_HEADER)

        # Pick trimester E-M, A-J, verano(J-S) S-D
        if trim == 0:
            self.trim = (1,3)
        elif trim == 1:
            self.trim = (4,7)
        elif trim == 2:
            self.trim = (7,9)
        else:
            self.trim = (9,12)

    def write_gen(self,asig_code="",limite_cred="",pp=""):
        new_row = [ student_id[0:2]
                  , student_id[2:]
                  , "1" # Siglo
                  , self.anio
                  , self.trim[0]
                  , self.trim[1]
                  , "" # Situación
                  , "" # Situación ins
                  , asig_code # General
                  , limite_cred # Limite Cred
                  , "" # nota_X_credito_ponderado
                  , "" # total_cred
                  , "" ] # pp
        self.gen_writer.writerow(new_row)

    def write_perm(self,asig_code,student_id,num_cred=""):
        #
        # student_id must have ddddddd format
        #
        new_row = [ asig_code
                  , student_id[0:2]
                  , student_id[2:]
                  , "1" # Siglo
                  , self.anio
                  , self.trim[0]
                  , self.trim[1]
                  , "" # Bloque
                  , "" # Secci'on
                  , num_cred # Num Creditos
                  , "?" # Permiso s/n
                  , "" # Renglon
                  , "" # Nota_asig
                  , "" ] # Ind_notaSinEfect

        self.perm_writer.writerow(new_row)
    
    def end_writer(self):
        self.f1.close()
        self.f2.close()

perm_file = "perm.csv"
gen_file  = "gen.csv"
trim      = 3
year      = 16

dace_csv = CsvCreator(gen_file,perm_file,trim,year)

dace_csv.write_perm("CI4722","1110552","8")
dace_csv.write_perm("CI5438","1110552","8")

dace_csv.end_writer()