#!/usr/bin/python3

# Nombre: Daniel Leones
# Carné: 09-10977
# Fecha: 7/12/2016
# Descripción: Procesa los archivos FODT producidos por LibreOffice de acuerdo al siguiente
# comando: ./soffice --headless --convert-to fodt archivo.doc. El comando anterior lo ejecuta el usuario,
# Diseñado para reconocer el estilo de presentación del departamento de cómputo;
# para ello se apoya en las etiquetas "table:table-cell" y table:table-row". La
# salida es un archivo.csv conforme al siguiente formato :
# (COD_ASIGNATURA,BLOQUE,LUNES,MARTES,MIERCOLES,JUEVES,VIERNES, ESPECIAL)
#
# Se utiliza el caracter ';' en las cadenas para distinguir el espacio en blanco.
# Esto es para reorganizar la información dado que libreoffice, en ocasiones, 
# la particiona. 

import xml.sax
import re
import sys
from os.path import isfile
from os import remove
from funcionesAuxiliares import dividirStr, obtArgs, cargarMaterias, \
                                  componerHorarioCSV, normalizarMateria, \
                                    ordenarDias, usoAyuda
#
# Clase usada por xml.sax para procesar el archivo.xml
#
class Ofertas( xml.sax.ContentHandler ):
    def __init__(self, listaMaterias):
        # Acumuladores
        # Fila de asignaturas
        self.filas = []
        # Buffer
        self.celda = ""
        # Lista de filas de asignaturas
        self.tuplas = []
        # Lista de materias
        self.listaMaterias = listaMaterias

        # Patrones usados por expresiones regulares
        self.patronDia = "(L;?[Uu];?[Nn];?(es)?|M;?[Aa];?[Rr];?(tes)?|M;?[Ii];?[Eeé];?([Rr];?|rcoles)?|" \
            + "[Jj];?[Uu];?[Ee];?(ves)?|V;?[Ii];?[Ee];?([Rr];?|nes)?)"
        self.patronDiasFrac = self.patronDia + "(\s*-\s*" + self.patronDia + ")?"
        self.patronHoras = "\d{1,2}(-\d{1,2})?"
        self.patronMateria = "(\w\w\s*-?\s*\d\d\d\d|\w\w\w\s*-?\s*\d\d\d)"
        self.patronHorario = "(" + self.patronDia + "((\s*|;*)-(\s*|;*)" + self.patronDia + ")?" \
         + "(\s+|;)" + self.patronHoras + "(\s+|;)?){1,2}"
        self.patronBloque = "\(?[Bb][Ll][Oo][Qq][Uu]?[Ee]?(\s)+[A-Z]\)?"

   
    # Función: startElement
    # Argumentos: 
    #   tag: String, nombre de la etiqueta proveniente del documento XML.
    # Salida: Ninguna 
    # 
    # Descripción: ejecutar una acción por cada etiqueta inicial 
    def startElement(self, tag, attributes):
        pass

    # Función: endElement
    # Argumentos: 
    #   tag: String, nombre etiqueta proveniente del documento XML.
    # Salida: Ninguna 
    # 
    # Descripción: ejecutar una acción por cada etiqueta final
    def endElement(self, tag):
        if tag == "table:table-row":
            # Descartar materias que no se encuentren en la lista de materias
            if self.filas and self.filas[0] in self.listaMaterias:
                self.tuplas.append(self.filas)
            self.filas = []
            self.celda = ""

        # Someter a analisis de texto a el buffer self.celda
        if tag == "table:table-cell":
            # Reconocer códigos de materias
            searchMateria = re.search(self.patronMateria,self.celda, re.I)
            if searchMateria:
                self.filas.append(normalizarMateria(searchMateria.group()))

            # Reconocer bloques de ofertas
            searchBloque = re.search(self.patronBloque,self.celda, re.I)
            if searchBloque:
                self.filas.append(self.filtrarBloque(searchBloque.group()))

            # Reconocer horarios de acuerdo a: Dia-Dia Hora ó Dia Hora.
            searchHor = re.search(self.patronHorario, self.celda, re.I)
            if searchHor:
                for hor in self.normalizarHorario( \
                                dividirStr(searchHor.group(), ';')):
                    txt = dividirStr(hor)
                    dias = dividirStr(txt[0],"-")
                    # Garantizar que solo los digitos de las horas
                    txt =  txt[1][0:4]
                    if len(dias) > 1:
                       self.filas.append((txt,dias[0][0:2].upper()))
                       self.filas.append((txt,dias[1][0:2].upper()))
                    else:
                       self.filas.append((txt,dias[0][0:2].upper()))
            self.celda = ""

    # Función: characters
    # Argumentos: 
    #   content: String
    # Salida: Ninguna 
    # 
    # Descripción: ejecutar una acción al encontrar al menos un caracter.
    def characters(self, content):
        if not (content.isspace()) and content.isprintable():
            self.celda += ";" + content.strip(' \t\n\r.*()')

    # Función: filtrarBloque
    # Argumentos: 
    #   txt: String
    # Salida: Caracter, letra del bloque
    # 
    # Descripción: al reconocer un bloque, particiona por espacio en blanco. 
    # Almacena la letra del bloque.
    def filtrarBloque(self,txt):
        return dividirStr(txt)[1]

    # Función: normalizarHorario
    # Argumentos: 
    #   txt: String
    # Salida: [String] 
    # 
    # Descripción: reconstruye la información de los horarios.
    # Los horarios se reconstruyen al formato: Dia-Dia Hora ó Dia Hora.
    def normalizarHorario(self,txt):
        hor = ""
        nuevoTxt = []
        for item in txt:
            if re.search('^\s*' + self.patronHoras + '\s*$', item):
                hor += ' ' + item.strip()
            else:
                hor += item
            # Reconocer horarios completos
            if re.search(self.patronHorario, hor, re.I):
                nuevoTxt.append(hor)
                hor = ""
            # Unir dias fraccionados con horas
            elif re.search(self.patronDiasFrac, hor, re.I):
                hor = "".join(dividirStr(hor))
        return nuevoTxt

# Función: procesarDOC
# Argumentos: 
#   nombreArchivoEntrada: String, camino hacia le archivo FODT
#   listaMaterias: [String],
#   fdSalida: [String]
# Salida: [[String]] , lista de ofertas en estilo CSV.
# 
# Descripción: Función principal de procesamiento de horarios.
def procesarDOC(nombreArchivoEntrada,listaMaterias,fdSalida): 
    # Crear un lector XML-
    parser = xml.sax.make_parser()
    # Desactivar namespaces
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)

    # override the default ContextHandler
    Handler = Ofertas(listaMaterias)
    parser.setContentHandler( Handler )
    parser.parse(nombreArchivoEntrada)

    # Ordenar de acuerdo al formato (COD_ASIGNATURA,BLOQUE,HORARIO)
    # Concatenar en un solo string e imprimir filas y
    # escribir filas en un archivo estilo csv.
    acum = ""
    for fil in Handler.tuplas:
        if len(fil) > 1:
            if isinstance(fil[1],tuple):
                acum = fil[0] + ',A'
                horariosOrdenados = sorted(fil[1:], key=ordenarDias)
            else:
                acum = ",".join(fil[:2])
                horariosOrdenados = sorted(fil[2:], key=ordenarDias)

            if horariosOrdenados:
                acum += componerHorarioCSV(horariosOrdenados) + ','
            else:
                acum += ',,,,,,Y'
        else:
            acum = fil[0] + ',A,,,,,,Y'

        fdSalida.append(acum.split(','))
        acum = ""

# Programa principal para pruebas
if ( __name__ == "__main__"):
    # Pasaje de argumentos por la entrada estandar
    (nomArchivoSalida, nomArchivoMaterias, args) = obtArgs(sys.argv[1:])

    # Cargar listas de materias requeridas
    listaMaterias = cargarMaterias(nomArchivoMaterias)

    fdSalida = []
    procesarDOC(args[0],listaMaterias,fdSalida)

    if isfile(nomArchivoSalida):
        remove(nomArchivoSalida)

    # Crear archivo de salida
    if nomArchivoSalida:
        try:
          f = open(nomArchivoSalida, 'a')
          f.write("COD_ASIGNATURA,BLOQUE,L,M,MI,J,V\n")
        except OSError as ose:
            print("Error de E/S: ", ose)
            sys.exit(2)
    else:
        print("COD_ASIGNATURA,BLOQUE,L,M,MI,J,V")


    for fila in fdSalida:
        if nomArchivoSalida:
            try:
                f.write(','.join(fila) + "\n")
            except OSError as ose:
                print("Error de E/S: ", ose)
                sys.exit(2)
        else:
            print(','.join(fila))

    if nomArchivoSalida:
        f.close()

# Pruebas sobre dividirStr
   # print(dividirStr("Mar -Jue  5-6   "))
   # print(dividirStr("    Mar -Jue  5-6   "))
   # print(dividirStr("    5-6   "))
   # print(dividirStr("       "))
   # print(dividirStr(""))
   # prueba = [('9-10', 'MI'), ('9-10', 'JU'), ('9-10', 'LU')]
   # prueba1 = [('9-10', 'MI'), ('9-10', 'JU'), ('9-10', 'LU')]
   # # print(sorted(prueba,key=ordenarDias))
   # horarios = sorted(prueba,key=ordenarDias)
   # print(componerHorarioCSV(horarios))

   #print(Handler.normalizarHorario(['Lun-Mier 5-6', 'Vie', '9-10']))

   # "c:\Program Files (x86)\LibreOffice 5\program\soffice.exe"  -convert-to xml doc4.doc --headless
   # "D:\Archivos de programa\LibreOffice 4\program\soffice.exe" -convert-to xml doc1.doc --headless
