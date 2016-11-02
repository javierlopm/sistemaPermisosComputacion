# -*- coding: utf-8 -*-
from __future__ import print_function
from easygui import *
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import subprocess
import getpass
from perm_store import PermStore, TipoPermiso, Trimestre

# from csv_creator   import *
from coord_crawler import *

#dirname = raw_input("Introduzca el nombre de la carpeta: ")

# perm_file = "perm.csv"
# gen_file  = "gen.csv"
# trim      = 3
# year      = 16


# dace_csv = CsvCreator(gen_file,perm_files,trim,year)

SCOPE = ["https://spreadsheets.google.com/feeds"]
SECRETS_FILE = "client_secret.json"

all_perms_dict = {
    5   : 'm',
    6   : 'm',
    7   : 'm',
    8   : 'm',
    13  : 'm',
    14  : 'r',
    9   : 'g',
    11  : 'l',
    12  : 'p',
    10  : 'e'
}

onlyg_perms_dict = {
    5 : 'x',
    6 : 'z',
    7 : 'g',
    8 : 'e'
}

nogen_perms_dict = {
    5   : 'm',
    6   : 'm',
    7   : 'm',
    8   : 'l',
    9   : 'p',
    10  : 'm'
}

trimestre_dict = {
    "Enero - Marzo"          : 'e',
    "Abril - Julio"          : 'a',
    "Julio - Agosto"         : 'j',
    "Septiembre - Diciembre" : 's'
}

mod_dict = {
    1 : "1YyiA_-5n1u0aY9tXWCpjDFQIWkpOXGo-_MqfL5cakN8",
    2 : "19brVUZXLWxu49JjleeEiR4rzGJdZcUDVXoJMgA1x7bw",
    3 : "1kkVCFP3zwq3PO6sNR12l2VloxNXA98lM6zGWGHfeom0"
}

graphs_command = "cd graphs_manager && java createPngGraph "

# Authenticate using the signed key
credentials = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', SCOPE)

gc = gspread.authorize(credentials)

perm_storer = PermStore()

def carnetToInt(carnet):
    spl = carnet.split('-')
    return int(spl[0])*100000 + int(spl[1])

def parseCoursesId(c_string, pasantia):
    if pasantia:
        if "larga" in c_string: return ["EP3420"]
        elif "corta" in c_string: return ["EP1420"]
        elif "Primera" in c_string: return ["EP1308"]
        elif "Segunda" in c_string: return ["EP2308"]
        elif "Tercera" in c_string: return ["EP3308"]
    else:
        spl = c_string.split(',')
        prelist = []
        for e in spl:
            if ' ' in e:
                aux = e.split(' ')
                for el in aux:
                    if el != '':
                        prelist.append(el)
            else:
                prelist.append(e)
        lis = []
        for elem in prelist:
            if '-' in elem:
                splaux = elem.split('-')
                he = ""
                for em in splaux:
                    he += em
                lis.append(he)
            else:
                lis.append(elem)
        return lis 

class AnswersChecker():
    def __init__(self, username, password, modality):
        try:
            self.aranita  = StudentDownloader(username,password,"HTML")
        except :
            print("aranita startup failed")

        self.modality = modality
        if self.modality == 1:
            self.process_fn = self.process_all
        elif self.modality == 2:
            self.process_fn = self.process_solo_generales
        elif self.modality == 3:
            self.process_fn = self.process_sin_generales

        from datetime import datetime

        self.year = datetime.now().year
        if datetime.now().month >= 10:
            self.year += 1


    def answers_downloader(self):
        print("Hojas de cálculo disponibles \n\n")
        sheet = gc.open_by_key(mod_dict[self.modality])
        print("{} - {}".format(sheet.title, sheet.id))
        print("▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔")

        for i,line in enumerate(sheet.get_worksheet(0).get_all_values()):
            print(str(i) + ".- " + str(line))
            if i > 0:
                self.process_fn(line)

        print("\n\n")

    def process_solo_generales(self, line):
        user_id = line[1].split('@')[0]
        if user_id == "coord-comp": return
        carnet = carnetToInt(user_id)

        try:
            (nombre,indice,aprobadas) = self.aranita.search_student(user_id)
        except :
            nombre,indice,aprobadas = ("",0.0,0)
            print("Error trying to get student")

        perm_storer.insert_student(carnet, "", line[4], line[3], line[9])
        
        for k in range(5,9):
            if line[k] != "":
                if onlyg_perms_dict[k] == 'e' or onlyg_perms_dict[k] == 'g':
                    perm_storer.insert_perm(carnet, TipoPermiso(onlyg_perms_dict[k]), Trimestre(trimestre_dict[line[2]]), self.year)
                if onlyg_perms_dict[k] == 'x' or onlyg_perms_dict[k] == 'z':
                    for elem in parseCoursesId  (line[k], False):
                        perm_storer.insert_perm(carnet, TipoPermiso(onlyg_perms_dict[k]), Trimestre(trimestre_dict[line[2]]), self.year, elem)

        process = subprocess.Popen(graphs_command+user_id,shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process.communicate()

    def process_all(self, line):
        user_id = line[1].split('@')[0]
        if user_id == "coord-comp": return
        carnet = carnetToInt(user_id)


        try:
            (nombre,indice,aprobadas) = self.aranita.search_student(user_id)
        except :
            nombre,indice,aprobadas = ("",0.0,0)
            print("Error trying to get student")

        perm_storer.insert_student(carnet, "", line[4], line[3], line[15])
        for k in range(5,15):
            pasantias = k == 13
            if line[k] != "":
                if all_perms_dict[k] == 'm':
                    for elem in parseCoursesId(line[k], pasantias):
                        perm_storer.insert_perm(carnet, TipoPermiso('m'), Trimestre(trimestre_dict[line[2]]), self.year, elem)
                elif (all_perms_dict[k] == 'l') or (all_perms_dict[k] == 'p'):
                    if all_perms_dict[k] == 'p': print(line[k])
                    perm_storer.insert_perm(carnet, TipoPermiso(all_perms_dict[k]), Trimestre(trimestre_dict[line[2]]), self.year, int(line[k]))
                elif (all_perms_dict[k] == 'e') or (all_perms_dict[k] == 'g'):
                    perm_storer.insert_perm(carnet, TipoPermiso(all_perms_dict[k]), Trimestre(trimestre_dict[line[2]]), self.year)
                elif all_perms_dict[k] == 'r':
                    for elem in parseCoursesId(line[k], pasantias):
                        perm_storer.insert_perm(carnet, TipoPermiso('r'), Trimestre(trimestre_dict[line[2]]), self.year, elem)
                            # Store user grades
        
        process = subprocess.Popen(graphs_command+user_id,shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process.communicate()
        
    def process_sin_generales(self, line):
        user_id = line[1].split('@')[0]
        if user_id == "coord-comp": return
        carnet = carnetToInt(user_id)

        try:
            (nombre,indice,aprobadas) = self.aranita.search_student(user_id)
        except :
            nombre,indice,aprobadas = ("",0.0,0)
            print("Error trying to get student")

        perm_storer.insert_student(carnet, "", line[4], line[3], line[11])
        for k in range(5,11):
            pasantias = k == 10
            if line[k] != "":
                if nogen_perms_dict[k] == 'm':
                    for elem in parseCoursesId(line[k], pasantias):
                        perm_storer.insert_perm(carnet, TipoPermiso('m'), Trimestre(trimestre_dict[line[2]]), self.year, elem)
                elif (nogen_perms_dict[k] == 'l') or (nogen_perms_dict[k] == 'p'):
                    if nogen_perms_dict[k] == 'p': print(line[k])
                    perm_storer.insert_perm(carnet, TipoPermiso(nogen_perms_dict[k]), Trimestre(trimestre_dict[line[2]]), self.year, int(line[k]))
                elif nogen_perms_dict[k] == 'r':
                    for elem in parseCoursesId(line[k], pasantias):
                        perm_storer.insert_perm(carnet, TipoPermiso('r'), Trimestre(trimestre_dict[line[2]]), self.year, elem)
                            # Store user grades

        process = subprocess.Popen(graphs_command+user_id,shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process.communicate()
