#!/usr/bin/python3.5
#!/usr/bin/python3.4

# Nombre: Daniel Leones
# Carné: 09-10977
# Fecha: 18/09/2016
# Descripción: Procesa los archivos xml producidos por LibreOffice de acuerdo al siguiente
# comando: ./soffice --headless --convert-to xml archivo.doc. Solamente procesa DOC.
# Para ello se apoya en las etiquetas "table:table-cell" y table:table-row". La
# salida es un archivo.csv conforme al siguiente formato :
# (COD_ASIGNATURA,BLOQUE,LUNES,MARTES,MIERCOLES,JUEVES,VIERNES)

import xml.sax
import re
import subprocess
from os.path import isfile
from os import remove

# Clase usada por xml.sax para procesar el archivo.xml
class Ofertas( xml.sax.ContentHandler ):
    def __init__(self, listaMaterias, corresDiaDistancia):
        self.filas = []
        self.celda = ""
        self.tuplas = []
        self.listaMaterias = listaMaterias
        self.corresDiaDistancia = corresDiaDistancia
        self.ultimoDia = ''
        self.patronDia = "(L[Uu][Nn](es)?|M[Aa][Rr](tes)?|M[Ii][Eeé]([Rr]|rcoles)?|" \
            + "[Jj][Uu][Ee](ves)?|V[Ii][Ee]([Rr]|nes)?)"
        self.patronHoras = "\d{1,2}-\d{1,2}"
        self.patronMateria = "(\w\w\s*-?\s*\d\d\d\d|\w\w\w\s*-?\s*\d\d\d)"
        self.patronHorario = "(" + self.patronDia + "(\s*-\s*" + self.patronDia + ")?" \
         + "(\s+|;)" + self.patronHoras + "(\s+|;)?){1,2}"
        self.patronBloque = "[Bb][Ll][Oo][Qq][Uu]?[Ee]?(\s)+\D"
   # Call when an element starts
    def startElement(self, tag, attributes):
        pass

   # Call when an elements ends
    def endElement(self, tag):
        if tag == "table:table-row":
            if self.filas and self.filas[0] in self.listaMaterias:
                #print("table:table-row", self.filas, end='\n')
                self.tuplas.append(self.filas)
            self.filas = []
            self.celda = ""

        if tag == "table:table-cell":
            #print("table:table-cell", self.celda.encode('UTF-8','replace'))
            searchMateria = re.search(self.patronMateria,self.celda, re.I)
            if searchMateria:
                #print("Materia", searchMateria.group())
                self.filas.append(self.normalizarMateria(searchMateria.group()))

            searchBloque = re.search(self.patronBloque,self.celda, re.I)
            if searchBloque:
                self.filas.append(self.filtrarBloque(self.celda))

            searchHor = re.search(self.patronHorario, self.celda, re.I)

            if searchHor:
                #print("listaHorarios", self.celda , dividirStr(searchHor.group(), ';'))
                for hor in self.normalizarHorario( \
                                dividirStr(searchHor.group(), ';')):
                    #print("hor", hor)
                    txt = dividirStr(hor)
                    dias = dividirStr(txt[0],"-")
                    # Garantizar que solo los digitos de las horas
                    txt =  txt[1][0:4]
                    #print(dias, txt)
                    if len(dias) > 1:
                       self.filas.append((txt,dias[0][0:2].upper()))
                       self.filas.append((txt,dias[1][0:2].upper()))
                    else:
                       self.filas.append((txt,dias[0][0:2].upper()))
            self.celda = ""

   # Call when a character is read
    def characters(self, content):
        if not (content.isspace()) and content.isprintable():
            #print (content.strip(' \t\n\r'))
            self.celda += ";" + content.strip(' \t\n\r.-*()')
        #print("characters", content)

    def filtrarBloque(self,txt):
        return dividirStr(txt)[1]

    def normalizarHorario(self,txt):
        hor = ""
        nuevoTxt = []
        fragmentado = False
        for item in txt:
            if re.search(self.patronHorario, item, re.I):
                nuevoTxt.append(item)
                continue
            elif re.search(self.patronDia + "(\s*-\s*" + self.patronDia + ")?",\
                           item, re.I):
                hor += item
                fragmentado = True
            elif fragmentado and re.search(self.patronHoras, item):
                nuevoTxt.append(hor + ' ' + item)
                fragmentado = False

        return nuevoTxt

    def normalizarMateria(self,txt):
        mat = ""
        for char in txt:
            if char != ' ' and char != '-':
                mat += char
        return mat

def componerHorarioCSV(listaHorarios):
   corresDiaDistancia = { 'LU' : 1, 'MA' : 2, 'MI' : 3, 'JU' : 4, 'VI' : 5} # CORREGIR EL ALCANCE
   ultimoDia = ''
   horarios = ""
   for (hora,dia) in listaHorarios:
      if ultimoDia == '':
         ultimoDia = dia
         horarios += (corresDiaDistancia[dia] * ',') + hora
      else:
         horarios += ((corresDiaDistancia[dia] -  \
                    corresDiaDistancia[ultimoDia]) * ',') + hora
         ultimoDia = dia

   if ultimoDia != '' and corresDiaDistancia[ultimoDia] < 5:
         horarios += ((5 - corresDiaDistancia[ultimoDia]) * ',')

   return horarios

# Función auxiliar para el ordenamiento de los horarios
def ordenarDias(txt):
   # Accede a una variable no local
   corresDiaDistancia = { 'LU' : 1, 'MA' : 2, 'MI' : 3, 'JU' : 4, 'VI' : 5} # CORREGIR EL ALCANCE
   return corresDiaDistancia[txt[1]]

# Funcion auxiliar para dividir cadenas de caracteres por un delimitador
def dividirStr(txt, delim = " "):
   cadena = []
   palabra = ""
   for c in txt:
      if delim == c and (palabra != ""):
         cadena.append(palabra)
         palabra = ""
      else:
         if c != delim:
            palabra += c

   if palabra != "":
      cadena.append(palabra)

   return cadena

# Función principal exportada para otros modulos.
def procesarDOC(nombreArchivoEntrada,listaMaterias,fdSalida):
    corresDiaDistancia = { 'LU' : 1, 'MA' : 2, 'MI' : 3, 'JU' : 4, 'VI' : 5}
    # create an XMLReader
    parser = xml.sax.make_parser()
    # turn off namepsaces
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)

    # override the default ContextHandler
    Handler = Ofertas(listaMaterias, corresDiaDistancia)
    parser.setContentHandler( Handler )
    parser.parse(nombreArchivoEntrada)

    # Ordenar de acuerdo al formato (COD_ASIGNATURA,BLOQUE,HORARIO)
    # Concatenar en un solo string e imprimir filas y
    # escribir filas en un archivo estilo csv.
    acum = ""
    for fil in Handler.tuplas:
        #Eliminar Len si todos las filas deben tener horario
        if len(fil) > 1:
            if isinstance(fil[1],tuple):
                acum = fil[0] + ',A'
                horariosOrdenados = sorted(fil[1:], key=ordenarDias)
            else:
                acum = ",".join(fil[:2])
                horariosOrdenados = sorted(fil[2:], key=ordenarDias)
            acum += componerHorarioCSV(horariosOrdenados)
        else:
            acum = fil[0] + ',A,,,,,'

        #fdSalida.write(acum + '\n') # Salida para archivo
        fdSalida.append(acum.split(','))
        acum = ""

# Programa principal para pruebas
if ( __name__ == "__main__"):
    corresDiaDistancia = { 'LU' : 1, 'MA' : 2, 'MI' : 3, 'JU' : 4, 'VI' : 5}
    listaMateriasComputo = ["CO4411","CO5212", "CO5213", "CO5313", "CO5412",
        "CO5413","CO5422", "CO5423","CO5511","CO5512","CO6315","CO6345",
        "CO6412","CO6531","CO6532","CO6612"]
    listaMateriasPB = ["PB5671" ,"PB5611"]
    # create an XMLReader
    parser = xml.sax.make_parser()
    # turn off namepsaces
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)

    # override the default ContextHandler
    Handler = Ofertas(listaMateriasComputo, corresDiaDistancia)
    parser.setContentHandler( Handler )
    parser.parse("OfertaComputo.xml")

    # Ordenar de acuerdo al formato (COD_ASIGNATURA,BLOQUE,HORARIO)
    if isfile('OfertaDOC.csv'):
        remove('OfertaDOC.csv')

    f = open('OfertaDOC.csv', 'a')
    # Concatenar en un solo string e imprimir filas y
    # escribir filas en un archivo estilo csv.
    f.write("COD_ASIGNATURA,BLOQUE,L,M,MI,J,V\n")
    acum = ""
    #print("Filas", Handler.tuplas[1:])
    for fil in Handler.tuplas:
      #Eliminar Len si todos las filas deben tener horario
      if len(fil) > 1:
         #print("Fila", fil, fil[1:])
         if isinstance(fil[1],tuple):
            acum = fil[0] + ',A'
            #print("Seleccion1", fil[1:])
            horariosOrdenados = sorted(fil[1:], key=ordenarDias)
         else:
            #print("Seleccion2", fil[2:])
            acum = ",".join(fil[:2])
            horariosOrdenados = sorted(fil[2:], key=ordenarDias)
         acum += componerHorarioCSV(horariosOrdenados)
      else:
         acum = fil[0] + ',A'
      print("Al escribir", acum)
      f.write(acum + '\n')
      acum = ""
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

   # "c:\Program Files (x86)\LibreOffice 5\program\soffice.exe"  -convert-to xml OfertaPB.doc