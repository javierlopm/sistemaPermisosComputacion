#!/usr/bin/python3.5
#!/usr/bin/python3.4

# Nombre: Daniel Leones
# Carné: 09-10977
# Fecha: 18/09/2016
# Descripción: Procesa los archivos xml producidos por la libreria MuPDf 1.9.2.
# Se apoya en las etiquetas "table:table-cell" y "table:table-row".
# La salida es un archivo.csv conforme al siguiente formato :
# (COD_ASIGNATURA,BLOQUE,LUNES,MARTES,MIERCOLES,JUEVES,VIERNES)

import fitz # Usando MuPDf 1.9.2
import xml.sax
import re
from decimal import Decimal
from os.path import isfile
from os import remove
import sys
import getopt

class Ofertas( xml.sax.ContentHandler ):
    def __init__(self, listaMaterias):
        self.tuplas = []
        self.fila = []
        self.posCaracteres = []
        self.cabeceraDias = []
        self.celda = ""
        self.listaMaterias = listaMaterias
        self.cabeceraLista = False
        self.existeCarrera = False
        self.patronHoras = "^\d{1,2}(-\d{1,2})?$"
        self.patronDias = "(L[Uu][Nn](\.?|es)?|M[Aa][Rr](\.?|tes)?|" + \
        "M[Ii][Ee](\.?|rcoles)?|[Jj][Uu][Ee](\.?|ves)?|V[Ii][Ee](\.?|es)?)"
        self.patronMateria = "\w\w\s*-?\s*\d\d\d\d"
        self.patronBloque = "^\(?(A|B|C|D)\)?$"
        self.patronCarrera = "0?800"

   # Call when an element starts
    def startElement(self, tag, attributes):
        if tag == "char":
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

                #print("Celda", self.celda)
                self.filtrarTexto(self.celda.strip())

            self.celda = ""
            self.posCaracteres = []

        if tag == "block":
            # if self.fila and ((not self.existeCarrera) \
            #      or self.fila[0] in self.listaMaterias):
            #     print("Aceptada" , self.fila)
            #     self.tuplas.append(self.fila)

            if self.fila:
                #print(self.fila)
                if  self.fila[0] in self.listaMaterias:
                    #print("Aceptada" , self.fila)
                    self.tuplas.append(self.fila)
            self.fila = []
            self.celda = ""
            self.posCaracteres = []


   # Call when a character is read
    def characters(self, content):
        pass

    # Encuentra los dias de semana y guarda sus posiciones en la página.
    def filtroCabecera(self,txt, posCaracteres):
        searchDias = re.search(self.patronDias, txt, re.I)
        if searchDias:
            longPalabra = len(txt)
            # print("posCaracteres", txt , posCaracteres)
            self.cabeceraDias.append((searchDias.group()[0:2],Decimal(posCaracteres[0][0]),\
                                      Decimal(posCaracteres[longPalabra-1][1])))

        # if len(self.cabeceraDias) == 5:
        #     print("Cabecera Lista: ", self.cabeceraDias)
        return len(self.cabeceraDias) == 5

    def filtrarTexto(self,txt):
        searchMat = re.search(self.patronMateria, txt, re.I)
        if searchMat:
            #print(searchMat)
            self.fila.append(self.normalizarMateria(searchMat.group()))
        elif re.search(self.patronBloque, txt, re.I):
            #print(re.search(self.patronBloque, txt, re.I))
            self.fila.append(txt)

        elif re.search(self.patronHoras, txt):
            #print(re.search(self.patronHoras, txt))
            #print(self.fila[0])
            for (dia,limInf,limSup) in self.cabeceraDias:
                # print(limInf, "posIniTxt <=", dia, "posIniDia ", Decimal(self.posCaracteres[0][0]), \
                #       "posFinTxt", Decimal(self.posCaracteres[-1][0]),"<= posFinDia", limSup )
                if (limInf - 3) <= Decimal(self.posCaracteres[0][0]) \
                    and Decimal(self.posCaracteres[-1][1]) <= (limSup + 3):
                    self.fila.append((txt,dia))
                    #print((txt,dia))
                    break

        # elif self.existeCarrera and re.search(self.patronCarrera, txt):
        #     #print(self.fila)
        #     self.tuplas.append(self.fila)
        #     self.fila = []

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

def procesarPDF(nombreArchivoEntrada, listaMaterias, fdSalida):
    doc = fitz.open(nombreArchivoEntrada)
    # create an XMLReader
    parser = xml.sax.make_parser()
    # turn off namepsaces
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)
    Handler = Ofertas(listaMaterias)
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
    for fil in Handler.tuplas:    #Eliminar residuos de la cabecera
        if fil:
            #print(fil)
            if len(fil) > 2:
                #print("Fila", fil, fil[1:])
                if isinstance(fil[1],tuple):
                    acum = fil[0] + ',A'
                    #print("Seleccion1", fil[1:])
                    horariosOrdenados = fil[1:]
                else:
                    #print("Seleccion2", fil[2:])
                    acum = ",".join(fil[:2])
                    horariosOrdenados = fil[2:]
                acum += componerHorarioCSV(horariosOrdenados)
            else:
                acum = fil[0] + ',A,,,,,'

            fdSalida.append(acum.split(','))
            acum = ""


def usoAyuda():
    print("""Uso: prog -f nombre_archivo_salida -m archivo_materias_requeridas
                    archivo1.pdf archivo2.xls ... archivoN
    prog [-h, --help] """)

def obtArgs(entrada):
    nomArchivoSalida = ""
    nomArchivoMaterias = ""
    try:
        opts, args = getopt.getopt(entrada, "f:m:h", ["help"])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err) # will print something like "option -a not recognized"
        usoAyuda()
        sys.exit(2)

    for o, a in opts:
        if o == "-f":
            nomArchivoSalida = a
        elif o == "-m":
            nomArchivoMaterias = a
        elif o in ("-h", "--help"):
            usoAyuda()
            sys.exit()
        else:
            assert False, "unhandled option"

    if not nomArchivoMaterias:
      print("Se requiere el parametro -m")
      sys.exit(2)

    return (nomArchivoSalida, nomArchivoMaterias, args)


if ( __name__ == "__main__"):
    (nomArchivoSalida, nomArchivoMaterias, args) = obtArgs(sys.argv[1:])
    nomArchivoEntrada = 'Oferta_Pregrado_1.pdf'

    listaMaterias = []
    for materia in open(nomArchivoMaterias, 'r'):
        if (not materia.isspace()) and materia[0] != '#':
            listaMaterias.append(materia.rstrip(' \t\n\r'))

    fdSalida = []
    procesarPDF(args[0],listaMaterias,fdSalida)

    if isfile(nomArchivoSalida):
        remove(nomArchivoSalida)

    if nomArchivoSalida:
        f = open(nomArchivoSalida, 'a')
        f.write("COD_ASIGNATURA,BLOQUE,L,M,MI,J,V\n")
    else:
        print("COD_ASIGNATURA,BLOQUE,L,M,MI,J,V")


    for fila in fdSalida:
        if nomArchivoSalida:
            f.write(','.join(fila) + "\n")
        else:
            print(','.join(fila))

    if nomArchivoSalida:
        f.close()

    # doc = fitz.open('pruebas/doc2.pdf')
    # page = doc.loadPage(0)
    # xmlText = page.getText(output = "xml")
    # f = open('xmlPDF.txt', 'w')
    # f.write(xmlText)
    # f.close()

