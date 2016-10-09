# -*- coding: utf-8 -*-
from __future__ import print_function
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
from coord_crawler import *

usuario = raw_input("Usuario:")
clave   = getpass.getpass("Clave  :")
#dirname = raw_input("Introduzca el nombre de la carpeta: ")

aranita = StudentDownloader(usuario,clave,"HTML")

SCOPE = ["https://spreadsheets.google.com/feeds"]
SECRETS_FILE = "client_secret.json"

permisos_dict = {
	1 : 5,  #Trimestre a inscribir
	2 : -1,   #Tipo de grafo-
	3 : -1,   #Nº permisos -
	4 : 29,   #Carnet-
	5 : 1,   #nombre
	6 : -1,   #indice-
	7 : 30,   #telefono
	8 : 4,   #creditos aprobados
	9 : 0,   #fecha
	10 : -1,  #trimestre ultimo blabla- 
	11 : 13,  #dos generales
	12 : 33,  #extraplan y general
	13 : 23,#extraplan
	14 : 15,#electiva de area
	15 : 12,#Minimo credito-
	16 : 12,#maximo credito-
	17 : 15 , #electivas libres-
	18 : 8, #Pasantia corta-
	19 : 8, #Pasantia larga-
	20 : 8, #primera etapa proyecto de grado mas topico-
	21 : 8, #etapa de proyecto
	22 : 34, #general adicional
	23 : 25,#asignatura sin requisito
	24 : 0, #materias permisos
	25 : 0, #permiso proyecto a dedicacione xclusiva
	26 : 28  #observaciones jaja
}


# Authenticate using the signed key
credentials = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', SCOPE)

gc = gspread.authorize(credentials)


print("Hojas de cálculo disponibles \n\n")
for sheet in gc.openall():
    print("{} - {}".format(sheet.title, sheet.id))
    print("▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔")

    for i,line in enumerate(sheet.get_worksheet(0).get_all_values()):
	    print(str(i) + ".- " + str(line))
	    if i>0:
	        user_id = line[29 ][:8]

	        

	        new_file = open("estudiantes/pendientes/"+user_id+".txt","w")
	        for i in range(1,27):
	        	if (i==4): new_line = user_id
	        	elif (i==2): new_line="Pasantia"
	        	elif (i==6): new_line=""
	        	elif (i==10): new_line="Otro"
	        	elif (i==12 or i==22 or i==11):
	        		if line[permisos_dict[i]]=="":
	        			new_line="no"
	        		else:
	        			new_line="si"
	        	elif (i==15 or i==16):
	        		if line[permisos_dict[i]]=="":
	        			new_line = "no"
	        		else:
	        			num = int(line[permisos_dict[i]])
	        			if (num < 8 and i == 15) or (num > 16 and i == 16):
	        				new_line = str(num)
	        			else:
	        				new_line = "no"
	        	elif (i==14):
	        		if (permisos_dict[i]==""):
	        			new_line="no"
	        		else:
	        			new_line=line[permisos_dict[i]]
	        	elif (i==18 or i==19 or i==20):
	        		aux = line[permisos_dict[i]]
	        		if aux == "":
	        			new_line = "no"
	        		else:
	        			if ("corta" in aux and i==18) or ("larga" in aux and i==19) or ("Primera" in aux and i==20):
	        				new_line = "si"
	        			elif "Segunda" in aux and i==20:
	        				new_line = "EP-2308, EP-5856"
	        			elif "Tercera" in aux and i==20:
	        				new_line = "EP-3308"
	        	elif (i==3 or i==17 or i==24 or i==25): new_line = "no"
	        	else:
	        		if (line[permisos_dict[i]]==""):
	        			new_line = "no"
	        		else:
	        			new_line = line[permisos_dict[i]]
	        	if (new_line == ""): new_line = "no"
	        	new_file.write(str(new_line)+"\n")
	        aranita.search_student(user_id)
	        new_file.close()
    print("\n\n")        
