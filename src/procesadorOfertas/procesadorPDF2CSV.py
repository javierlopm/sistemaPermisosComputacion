#!/usr/bin/python 3.5
# Nombre: Daniel Leones
# Descripción: script para procesar PDFs para formato CSV. Luego se usa en Pentaho
# para integración de datos.

import fitz # Usando MuPDf 1.9.2
import xml.sax
import re
from os import remove

# NOTA FALLA: 328.80003 coincide para M y MI en Interfaces de Usuario
# Datos de las posiciones de los horarios
# 256.80003, 309.84, 307.44, 287.8795, 292.80003 para L
# 292.2, 345.84, 338.04,328.80003  para M
# 331.31953, 381.84 para MI
# 376.31953, 370.91954, 417.95954, 415.44 para J
# 423.6, 453.95954 para V

# Predicados para filtrar la info relevante
def filtrarBloque(txt):
    if txt[0] == '(' and txt[1].isalpha() and txt[2] == ')':
        return True

    return False

def filtrarMateria(txt):
    if len(txt) == 7 and txt[0].isalpha() and txt[1].isalpha() and txt[2] == '-' \
        and txt[3].isdigit():
        return True
    return False

class Ofertas( xml.sax.ContentHandler ):
   def __init__(self):
      self.tuplas = []
      self.filas = []
      self.celda = ""
      self.patronHoras = "^\d{1,2}-\d{1,2}$"
      self.estado = 0
      #(TERC|3)ER AÑO APROBAD
      #"\(?\d{1,2}\)?(\s+[NPR])?"
      self.patronTerminal = "^(\(?\d{1,2}\)?(\s+[NPR])?|(TERC|3)ER\sAÑO(\sAPROBADO)?)$"

   # Call when an element starts
   def startElement(self, tag, attributes):
        if tag == "char":
            self.celda += attributes["c"]
        if tag == "span":
            #print(attributes['bbox'].split(" ")[0])
            self.coorColumna = attributes['bbox'].split(" ")[0]

   # Call when an elements ends
   def endElement(self, tag):
      if tag == "span":
            #print("Celda", self.celda)
            if filtrarMateria(self.celda) and self.estado == 0:
                #print("Materia", self.celda)
                self.filas.append(self.celda)
                self.celda = ""
                self.estado = 1
                return

            if self.estado == 1:
                if filtrarBloque(self.celda):
                    self.filas.append(self.celda[1])
                else:
                    self.filas.append('A')
                self.celda = ""
                self.estado = 2
                return

            searchHorario = re.search(self.patronHoras,self.celda)
            #print("Patron", searchHorario, self.celda)
            if (self.estado == 2 and searchHorario) \
                or (self.estado == 2 and len(self.celda) == 1 \
                    and self.celda[0].isdigit()):
                dia = ''
                if self.coorColumna == "256.80003" \
                    or self.coorColumna == "309.84" \
                    or self.coorColumna == "307.44" \
                    or self.coorColumna == "287.8795" \
                    or self.coorColumna == "292.80003":
                    dia = 'L'
                if self.coorColumna == "292.2" \
                    or self.coorColumna == "345.84" \
                    or self.coorColumna == "338.04" \
                    or self.coorColumna == "328.80003":
                    dia = 'M'
                if self.coorColumna  == "331.31953" \
                    or self.coorColumna  == "381.84" \
                    or self.coorColumna == "362.4":
                    dia = 'MI'
                if self.coorColumna  == "376.31953"  \
                    or self.coorColumna == "370.91954"  \
                    or self.coorColumna == "417.95954" \
                    or self.coorColumna == "415.44" \
                    or self.coorColumna == '405' \
                    or self.coorColumna == "400.80003":
                    dia = 'J'
                if self.coorColumna  == "423.6" or \
                    self.coorColumna  == "453.95954":
                    dia = 'V'
                self.filas.append((self.celda, dia))
                self.celda = ""
                return

            searchTerminal = re.search(self.patronTerminal, self.celda, re.I)
            #print("Patron", searchTerminal, self.celda)
            if searchTerminal: #or filtrarMateria(self.celda):
                #print("Fila", self.filas)
                self.tuplas.append(self.filas)
                self.filas = []
                self.celda = ""
                self.estado = 0
                return

            self.celda = ""
   # Call when a character is read
   def characters(self, content):
        pass

def procesarPDF(nombreArchivoEntrada, fdArchivoSalida):
    corresDiaDistancia = { 'L' : 1, 'M' : 2, 'MI' : 3, 'J' : 4, 'V' : 5}
    doc = fitz.open(nombreArchivoEntrada)
    # create an XMLReader
    parser = xml.sax.make_parser()
    # turn off namepsaces
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)
    Handler = Ofertas()
    # override the default ContextHandler
    parser.setContentHandler( Handler )

    for num in range(0,doc.pageCount - 1):
        # Procesar los PDFs usando MuPDF. Se extrae el texto del documento en
        # archivo XML.
        page = doc.loadPage(num)
        xmlText = page.getText(output = "xml")
        f = open('textPDFXML.xml', 'w')
        f.write(xmlText)
        # Procesar el archivo XML
        parser.parse("textPDFXML.xml")

    f.close()
    remove('textPDFXML.xml')

    # Ordenar de acuerdo al formato (COD_ASIGNATURA,BLOQUE,L,M,MI,J,V)
    # Concatenar en un solo string e imprimir filas en formato CSV.
    # Variable para escribir las filas en el archivo destino
    row = ""
    # Variable para marcar el ultimo dia procesado para el horario
    ultimoDia = ''
    nroCampo = 0
    for fil in Handler.tuplas[1:]:    #Quitar cabecera
        if fil:
            for txt in fil:
                nroCampo += 1
                #Comprobar que haya un bloque. Sino se agrega, por defecto, el bloque A
                if nroCampo == 2 and (not txt.isalpha()):
                    row += ',A'
                    continue

                if isinstance(txt, tuple):
                    hor, dia = txt

                    if ultimoDia == '':
                        row += (corresDiaDistancia[dia] * ',') + hor
                    else:
                        row += ((corresDiaDistancia[dia] -  \
                                 corresDiaDistancia[ultimoDia]) * ',') + hor
                    ultimoDia = dia
                    continue

                row += ','+ txt

            if ultimoDia != '' and corresDiaDistancia[ultimoDia] < 5:
                row += ((5 - corresDiaDistancia[ultimoDia]) * ',')

            row = row [1:]    #Remover la primera coma (,)
            fdArchivoSalida.write(row + '\n')
            row = ""
            ultimoDia = ''
            nroCampo = 0

if ( __name__ == "__main__"):
    #Diccionario para distancias entre comas
    corresDiaDistancia = { 'L' : 1, 'M' : 2, 'MI' : 3, 'J' : 4, 'V' : 5}
    doc = fitz.open('OFERTA_ASIGNATURAS_SD2016.pdf')
    # create an XMLReader
    parser = xml.sax.make_parser()
    # turn off namepsaces
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)
    Handler = Ofertas()
    # override the default ContextHandler
    parser.setContentHandler( Handler )

    salida = open('OfertaComp2016.csv', 'a')
    salida.write("COD_ASIGNATURA,BLOQUE,L,M,MI,J,V\n")
    for num in range(0,doc.pageCount - 1):
        #print("Pagina: ", num)
        # Procesar los PDFs usando MuPDF. Se extrae el texto del documento en
        # archivo XML.
        page = doc.loadPage(num)
        xmlText = page.getText(output = "xml")
        f = open('textPDFXML0.xml', 'w')
        f.write(xmlText)
        # Procesar el archivo XML
        parser.parse("textPDFXML0.xml")
    f.close()

    # Ordenar de acuerdo al formato (COD_ASIGNATURA,BLOQUE,L,M,MI,J,V)
    # Concatenar en un solo string e imprimir filas en formato CSV.

    # Variable para escribir las filas en el archivo destino
    row = ""
    # Variable para marcar el ultimo dia procesado para el horario
    ultimoDia = ''
    nroCampo = 0
    for fil in Handler.tuplas[1:]:    #Quitar cabecera
        if fil:
            for txt in fil:
                nroCampo += 1
                #Comprobar que haya un bloque. Sino se agrega, por defecto, el bloque A
                if nroCampo == 2 and (not txt.isalpha()):
                    row += ',A'
                    continue

                if isinstance(txt, tuple):
                    hor, dia = txt

                    if ultimoDia == '':
                        row += (corresDiaDistancia[dia] * ',') + hor
                    else:
                        row += ((corresDiaDistancia[dia] -  \
                                 corresDiaDistancia[ultimoDia]) * ',') + hor
                    ultimoDia = dia
                    continue

                row += ','+ txt

            if ultimoDia != '' and corresDiaDistancia[ultimoDia] < 5:
                row += ((5 - corresDiaDistancia[ultimoDia]) * ',')

            row = row [1:]    #Remover la primera coma (,)
            salida.write(row + '\n')
            row = ""
            ultimoDia = ''
            nroCampo = 0

    salida.close()

    # doc = fitz.open('OFERTA_ASIGNATURAS_SD2016.pdf')
    # page = doc.loadPage(1)
    # xmlText = page.getText(output = "xml")
    # f = open('textPDFXML0.xml', 'w')
    # f.write(xmlText)

