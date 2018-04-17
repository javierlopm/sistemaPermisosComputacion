# -*- coding: utf-8 -*-
from __future__ import print_function
from easygui import msgbox
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import subprocess
import getpass
from perm_store import PermStore, TipoPermiso, Trimestre

# from csv_creator   import *
from coord_crawler import *
from comprobante_crawler import StudentCurrentDownloader
from sc_image_downloader import *

#dirname = raw_input("Introduzca el nombre de la carpeta: ")

# perm_file = "perm.csv"
# gen_file  = "gen.csv"
# trim      = 3
# year      = 16


# dace_csv = CsvCreator(gen_file,perm_files,trim,year)

SCOPE = ["https://spreadsheets.google.com/feeds"]
SECRETS_FILE = "client_secret.json"

all_perms_dict = {
    5: 'm',
    6: 't',
    7: 'z',
    8: 't',
    13: 'm',
    14: 'r',
    9: 'g',
    11: 'l',
    12: 'p',
    10: 'e',
    16: 'x'
}

onlyg_perms_dict = {
    5: 'x',
    6: 'z',
    7: 'g',
    8: 'e'
}

nogen_perms_dict = {
    5: 'm',
    6: 't',
    7: 't',
    8: 'l',
    9: 'p',
    10: 'm',
    11: 'r'
}

trimestre_dict = {
    "Enero - Marzo": 'e',
    "Abril - Julio": 'a',
    "Julio - Agosto": 'j',
    "Septiembre - Diciembre": 's'
}

mod_dict = {
    1: "1YyiA_-5n1u0aY9tXWCpjDFQIWkpOXGo-_MqfL5cakN8",  # todos
    2: "1spBf3ei7EunkuYv0CDWRgJG36XNZY5LDi6V1k-8J-CA",  # solo generales
    3: "1PLuTOglJKCilu97LbZnMURnrm62Xp7nWcrg1carCXHc"  # sin generales
}

graphs_command = "cd graphs_manager && java createPngGraph "
perm_storer = PermStore()


def carnetToInt(carnet):
    spl = carnet.split('-')
    return int(spl[0])*100000 + int(spl[1])


def parseCoursesId(c_string, pasantia):
    if pasantia:
        if "larga" in c_string:
            return ["EP3420"]
        elif "corta" in c_string:
            return ["EP1420"]
        elif "Primera" in c_string:
            return ["EP1308"]
        elif "Segunda" in c_string:
            return ["EP2308"]
        elif "Tercera" in c_string:
            return ["EP3308"]
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
        return list(map((lambda x: x.upper()), lis))


class AnswersChecker():
    def __init__(self, username, password, modality):

        # Expediente & Comprobante
        try:
            self.aranita = StudentDownloader(
               username, password, "graphs_manager/HTML")
            self.aranita_comprobante = StudentCurrentDownloader(
               username, password)
        except Exception as e:
            print("Error con el downloader de Expediente o Comprobante")
            print(e)

        # Authenticate using the signed key
        try:
            credentials = ServiceAccountCredentials.from_json_keyfile_name(
                'client_secret.json', SCOPE)
            self.gc = gspread.authorize(credentials)
            self.do_nothing = False
        except Exception as e:
            self.do_nothing = True
            msgbox(
                "Error conectándose con la descarga del Google Form. Verifique la presencia de la llave secreta.")
            print(e)

        # Community Service
        try:
            self.community_service_downloader = CommunityServiceDownloader()
        except Exception as e:
            print("Error inicializando el downloader de imágenes del SC")
            print(e)

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
        if self.do_nothing:
            try:
                self.aranita.close()
                self.aranita_comprobante.close()
            except:
                pass
            return False

        print("Hojas de cálculo disponibles \n\n")
        sheet = self.gc.open_by_key(mod_dict[self.modality])
        print("{} - {}".format(sheet.title, sheet.id))
        print("▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔")
        print(len(sheet.get_worksheet(0).get_all_values()))
        for i, line in enumerate(sheet.get_worksheet(0).get_all_values()):
            print(str(i) + ".- " + str(line))
            if(line[0] == ""):
                continue
            if i > 0:
                self.process_fn(line)

        try:
           self.aranita.close()
        except:
           print("Aranita closing failed")

        print("\n\n")

        return True

    def process_solo_generales(self, line):
        user_id = line[1].split('@')[0]
        if user_id == "coord-comp":
            return
        carnet = carnetToInt(user_id)

        try:
            (nombre, indice, aprobadas) = self.aranita.search_student(user_id)
            self.aranita_comprobante.search_student(user_id)
        except:
            nombre, indice, aprobadas = ("", 0.0, 0)
            print("Error trying to get student")

        perm_storer.insert_student(
            carnet, nombre, line[4], line[3], indice, aprobadas, line[9])

        for k in range(5, 9):
            if line[k] != "":
                if onlyg_perms_dict[k] == 'e' or onlyg_perms_dict[k] == 'g':
                    perm_storer.insert_perm(carnet, TipoPermiso(
                        onlyg_perms_dict[k]), Trimestre(trimestre_dict[line[2]]), self.year)
                if onlyg_perms_dict[k] == 'x' or onlyg_perms_dict[k] == 'z':
                    for elem in parseCoursesId(line[k], False):
                        perm_storer.insert_perm(carnet, TipoPermiso(onlyg_perms_dict[k]), Trimestre(
                            trimestre_dict[line[2]]), self.year, elem)
        #print(graphs_command+user_id)

        process = subprocess.Popen(
            graphs_command+user_id, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        #print(process.communicate())

    def process_all(self, line):
        user_id = line[1].split('@')[0]
        if user_id == "coord-comp":
            return
        carnet = carnetToInt(user_id)

        try:
            (nombre, indice, aprobadas) = self.aranita.search_student(user_id)
            self.aranita_comprobante.search_student(user_id)
        except Exception as e:
            nombre, indice, aprobadas = ("", 0.0, 0)
            print("Error trying to get student")
            print(e)

        perm_storer.insert_student(
            carnet, nombre, line[4], line[3], indice, aprobadas, line[15])
        for k in range(5, 17):
            pasantias = k == 13
            if line[k] != "" and k != 15:
                if all_perms_dict[k] == 'm' or all_perms_dict[k] == 't':
                    for elem in parseCoursesId(line[k], pasantias):
                        perm_storer.insert_perm(carnet, TipoPermiso(all_perms_dict[k]), Trimestre(
                            trimestre_dict[line[2]]), self.year, elem)
                elif (all_perms_dict[k] == 'l') or (all_perms_dict[k] == 'p'):
                    if all_perms_dict[k] == 'p':
                        print(line[k])
                    perm_storer.insert_perm(carnet, TipoPermiso(all_perms_dict[k]), Trimestre(
                        trimestre_dict[line[2]]), self.year, int(line[k]))
                elif (all_perms_dict[k] == 'e') or (all_perms_dict[k] == 'g'):
                    perm_storer.insert_perm(carnet, TipoPermiso(
                        all_perms_dict[k]), Trimestre(trimestre_dict[line[2]]), self.year)
                elif all_perms_dict[k] == 'r':
                    for elem in parseCoursesId(line[k], pasantias):
                        perm_storer.insert_perm(carnet, TipoPermiso('r'), Trimestre(
                            trimestre_dict[line[2]]), self.year, elem)
                elif all_perms_dict[k] == 'x' or all_perms_dict[k] == 'z':
                    for elem in parseCoursesId(line[k], False):
                        perm_storer.insert_perm(carnet, TipoPermiso(all_perms_dict[k]), Trimestre(
                            trimestre_dict[line[2]]), self.year, elem)

        # SC IMAGE FILE
        if (len(line[-1]) > 0):
            sc_image_id = self.community_service_downloader.get_googledrivefile_id(
                line[-1])
            self.community_service_downloader.download_image(
                sc_image_id, user_id)

        process = subprocess.Popen(
            graphs_command+user_id, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process.communicate()

    def process_sin_generales(self, line):

        user_id = line[1].split('@')[0]
        if user_id == "coord-comp":
            return
        carnet = carnetToInt(user_id)

        try:
            (nombre, indice, aprobadas) = self.aranita.search_student(user_id)
            #print("Descargando el comprobante del estudiante" + user_id)
            self.aranita_comprobante.search_student(user_id)
        except:
            nombre, indice, aprobadas = ("", 0.0, 0)
            print("Error trying to get student")

        perm_storer.insert_student(
            carnet, nombre, line[4], line[3], indice, aprobadas, line[12])
        for k in range(5, 12):
            pasantias = k == 10
            if line[k] != "":
                if nogen_perms_dict[k] == 'm' or nogen_perms_dict[k] == 't':
                    for elem in parseCoursesId(line[k], pasantias):
                        perm_storer.insert_perm(carnet, TipoPermiso(nogen_perms_dict[k]), Trimestre(
                            trimestre_dict[line[2]]), self.year, elem)
                elif (nogen_perms_dict[k] == 'l') or (nogen_perms_dict[k] == 'p'):
                    if nogen_perms_dict[k] == 'p':
                        print(line[k])
                    perm_storer.insert_perm(carnet, TipoPermiso(nogen_perms_dict[k]), Trimestre(
                        trimestre_dict[line[2]]), self.year, int(line[k]))
                elif nogen_perms_dict[k] == 'r':
                    for elem in parseCoursesId(line[k], pasantias):
                        perm_storer.insert_perm(carnet, TipoPermiso('r'), Trimestre(
                            trimestre_dict[line[2]]), self.year, elem)
                        # Store user grades

        # SC IMAGE FILE
        if (len(line[-1]) > 0):
            sc_image_id = self.community_service_downloader.get_googledrivefile_id(
                line[-1])
            self.community_service_downloader.download_image(
                sc_image_id, user_id)

        process = subprocess.Popen(
            graphs_command+user_id, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process.communicate()
