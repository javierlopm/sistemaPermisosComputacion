#!/usr/bin/python 3.5
# Nombre: Daniel Leones
# Descripción: script para procesar PDFs para formato CSV. Luego se usa en Pentaho
# para integración de datos.

import fitz # Usando MuPDf 1.9.2
import xml.sax
import re
from decimal import Decimal
from os.path import isfile
from os import remove

class Ofertas( xml.sax.ContentHandler ):
    def __init__(self):
        self.tuplas = []
        self.fila = []
        self.posCaracteres = []
        self.cabeceraDias = []
        self.celda = ""
        self.cabeceraLista = False
        self.existeCarrera = False
        self.patronHoras = "^\d{1,2}-\d{1,2}$"
        self.patronDias = "(L[Uu][Nn](\.?|es)?|M[Aa][Rr](\.?|tes)?|" + \
        "M[Ii][Ee](\.?|rcoles)?|[Jj][Uu][Ee](\.?|ves)?|V[Ii][Ee](\.?|es)?)"
        self.patronMateria = "^\w\w-?\d\d\d\d$"
        self.patronBloque = "^\(?(A|B|C|D)\)?$"
        self.patronCarrera = "0?800"
        self.estado = 0

   # Call when an element starts
    def startElement(self, tag, attributes):
        if tag == "char":
            if attributes['c'] == ' ':
                if not self.cabeceraLista:
                    self.cabeceraLista = \
                        self.filtroCabecera(self.celda, self.posCaracteres)

                if re.search("Carreras?", self.celda, re.I):
                    #print("existeCarrera Start")
                    self.existeCarrera = True

                self.filtrarTexto(self.celda)
                self.celda = ""
                self.posCaracteres = []
            else:
                self.celda += attributes["c"]
                self.posCaracteres.append(
                    (attributes['bbox'].split(" ")[0], \
                     attributes['bbox'].split(" ")[2]))

   # Call when an elements ends
    def endElement(self, tag):
        if tag == "span":
            #print("Celda", self.celda, self.posCaracteres)
            if not self.cabeceraLista:
                self.cabeceraLista = \
                    self.filtroCabecera(self.celda, self.posCaracteres)
            else:
                if re.search("Carreras?", self.celda, re.I):
                    #print("existeCarrera END")
                    self.existeCarrera = True

                self.filtrarTexto(self.celda)

            self.celda = ""
            self.posCaracteres = []

        if tag == "block":
            if not self.existeCarrera:
                self.tuplas.append(self.fila)
            self.fila = []
            self.celda = ""
            self.posCaracteres = []



   # Call when a character is read
    def characters(self, content):
        pass

    def filtroCabecera(self,txt, posCaracteres):

        if re.search(self.patronDias, txt, re.I):
            longPalabra = len(txt)
            #print("posCaracteres", txt , posCaracteres)
            self.cabeceraDias.append((txt[0:2],Decimal(posCaracteres[0][0]),\
                                      Decimal(posCaracteres[longPalabra-1][1])))

        # if len(self.cabeceraDias) == 5:
        #     print("Cabecera Lista: ", self.cabeceraDias)
        return len(self.cabeceraDias) == 5

    def filtrarTexto(self,txt):

        if (re.search(self.patronMateria, txt, re.I) \
            or re.search(self.patronBloque, txt, re.I)):
            self.fila.append(txt)
        elif re.search(self.patronHoras, txt):
            long = len(txt)
            for (dia,limInf,limSup) in self.cabeceraDias:
                if (limInf - 3) <= Decimal(self.posCaracteres[0][0]) \
                    and Decimal(self.posCaracteres[long-1][1]) <= (limSup + 3):
                    # print("dia", dia, "posIniDia", limInf, "posIniTxt", Decimal(self.posCaracteres[0][0]), \
                    #       "posFinTxt", Decimal(self.posCaracteres[long-1][0]),"posFinDia", limSup )
                    self.fila.append((txt,dia))
                    break

        elif self.existeCarrera and re.search(self.patronCarrera, txt):
            #print(self.fila)
            self.tuplas.append(self.fila)
            self.fila = []

def procesarPDF(nombreArchivoEntrada, fdArchivoSalida):
    corresDiaDistancia = { 'LU' : 1, 'MA' : 2, 'MI' : 3, 'JU' : 4, 'VI' : 5}
    doc = fitz.open(nombreArchivoEntrada)
    # create an XMLReader
    parser = xml.sax.make_parser()
    # turn off namepsaces
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)
    Handler = Ofertas()
    # override the default ContextHandler
    parser.setContentHandler( Handler )

    for num in range(0,doc.pageCount):
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
    for fil in Handler.tuplas[1:]:    #Eliminar residuos de la cabecera
        for txt in fil:
            nroCampo += 1
            #Comprobar que haya un bloque. Sino se agrega, por defecto, el bloque A
            if nroCampo == 2 and (not txt.isalpha()):
                row += ',A'
                continue

            if isinstance(txt, tuple):
                hor, dia = txt

                if ultimoDia == '':
                    row += (corresDiaDistancia[dia] * ',-') + hor
                    row = row[:-1]
                else:
                    row += ((corresDiaDistancia[dia] -  \
                             corresDiaDistancia[ultimoDia]) * ',-') + hor
                    row = row[:-1]
                ultimoDia = dia
                continue

            row += ','+ txt

        if ultimoDia != '' and corresDiaDistancia[ultimoDia] < 5:
            row += ((5 - corresDiaDistancia[ultimoDia]) * ',-')

        row = row [1:]    #Remover la primera coma (,)
        fdArchivoSalida.write(row + '\n')
        row = ""
        ultimoDia = ''
        nroCampo = 0

if ( __name__ == "__main__"):
    #Diccionario para distancias entre comas
    corresDiaDistancia = { 'LU' : 1, 'MA' : 2, 'MI' : 3, 'JU' : 4, 'VI' : 5}
    doc = fitz.open('OfertaSIG.pdf')
    # create an XMLReader
    parser = xml.sax.make_parser()
    # turn off namepsaces
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)
    Handler = Ofertas()
    # override the default ContextHandler
    parser.setContentHandler( Handler )

    if isfile('OfertSIG.csv'):
        remove('OfertSIG.csv')

    salida = open('OfertSIG.csv', 'a')
    salida.write("COD_ASIGNATURA,BLOQUE,L,M,MI,J,V\n")
    #for num in range(0,doc.pageCount - 1):
        #print("Pagina: ", num)
        # Procesar los PDFs usando MuPDF. Se extrae el texto del documento en
        # archivo XML.
    page = doc.loadPage(0)
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
    for fil in Handler.tuplas[1:]:    #Eliminar residuos de la cabecera
        for txt in fil:
            nroCampo += 1
            #Comprobar que haya un bloque. Sino se agrega, por defecto, el bloque A
            if nroCampo == 2 and (not txt.isalpha()):
                row += ',A'
                continue

            if isinstance(txt, tuple):
                hor, dia = txt

                if ultimoDia == '':
                    row += (corresDiaDistancia[dia] * ',-')
                    print("row", row)
                    row += row[:-1] + hor
                    print("row", row)
                else:
                    row += ((corresDiaDistancia[dia] -  \
                             corresDiaDistancia[ultimoDia]) * ',-')
                    row += row[:-1] + hor
                    # row1 = row[:-1]
                    # print("row", row,"|||||", row1)
                ultimoDia = dia
                continue

            row += ','+ txt

        if ultimoDia != '' and corresDiaDistancia[ultimoDia] < 5:
            row += ((5 - corresDiaDistancia[ultimoDia]) * ',-')

        row = row [1:]    #Remover la primera coma (,)
        salida.write(row + '\n')
        print(row) #para debugging
        row = ""
        ultimoDia = ''
        nroCampo = 0

    salida.close()

    # doc = fitz.open('OfertaSIG.pdf')
    # page = doc.loadPage(0)
    # xmlText = page.getText(output = "json")
    # f = open('jsonPDF.txt', 'w')
    # f.write(xmlText)
    # f.close()

#pdftohtml -xml -stdout OfertaSIG.pdf | pdftable -f OfertaSIG%d.csv

