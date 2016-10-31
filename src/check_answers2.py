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

perms_dict = {
    5   : 'm',
    6   : 'm',
    7   : 'm',
    8   : 'm',
    13  : 'm',
    14  : 'm',
    9   : 'g',
    11  : 'l',
    12  : 'p',
    10  : 'e'
}

trimestre_dict = {
    "Enero - Marzo"          : 'e',
    "Abril - Julio"          : 'a',
    "Julio - Agosto"         : 'j',
    "Septiembre - Diciembre" : 's'
}

graphs_command = "java graphs_manager/createPngGraph "

# Authenticate using the signed key
credentials = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', SCOPE)

gc = gspread.authorize(credentials)

perm_storer = PermStore()

def carnetToInt(carnet):
    spl = carnet.split('-')
    return int(spl[0])*100000 + int(spl[1])

def parseCoursesId(c_string, k):
    if k == 13:
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
                        prelist.append(aux)
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
        return lis 
class AnswersChecker():
    def __init__(self, username, password, modality):
        #self.aranita  = StudentDownloader(username,password,"HTML")
        self.modality = modality

    def answers_downloader(self):
        print("Hojas de cálculo disponibles \n\n")
        for sheet in gc.openall():
            print("{} - {}".format(sheet.title, sheet.id))
            print("▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔")

            for i,line in enumerate(sheet.get_worksheet(0).get_all_values()):
                print(str(i) + ".- " + str(line))

                if i>0:
                    user_id = line[1].split('@')[0]
                    print("Procesando " + user_id)
                    carnet = carnetToInt(user_id)
                    perm_storer.insert_student(carnet, "", line[4], line[3], line[15])
                    for k in range(5,15):
                        if line[k] != "":
                            if perms_dict[k] == 'm':
                                for elem in parseCoursesId(line[k], k):
                                    print("Materia: " + elem)
                                    perm_storer.insert_perm(carnet, TipoPermiso('m'), Trimestre(trimestre_dict[line[2]]), 0, elem)
                            if perms_dict[k] == 'l' or perms_dict[k] == 'p':
                                perm_storer.insert_perm(carnet, TipoPermiso(perms_dict[k]), Trimestre(trimestre_dict[line[2]]), 0, int(line[k]))
                            if perms_dict[k] == 'e' or perms_dict[k] == 'g':
                                perm_storer.insert_perm(carnet, TipoPermiso(perms_dict[k]), Trimestre(trimestre_dict[line[2]]), 0)
                            if perms_dict[k] == 'r':
                                for elem in parseCoursesId(line[k], k):
                                    perm_storer.insert_perm(carnet, TipoPermiso('r'), Trimestre(trimestre_dict[line[2]]), 0, elem)

                    # Store user grades
                    #self.aranita.search_student(user_id)
                    print("Generando grafo para "+user_id)
                    process = subprocess.Popen(graphs_command+user_id,shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    process.communicate()
                    print("Listo")
                    #Create rows in csv with permissons
                    # dace_csv.write_perm(code,user_id,credit_num)
            # 1
            print("\n\n")