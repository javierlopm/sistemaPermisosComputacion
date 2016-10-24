#!/usr/bin/python3.5
#!/usr/bin/python3.4

# Nombre: Daniel Leones
# Carné: 09-10977
# Fecha: 18/09/2016
# Descripción: Procesa los archivos xml producidos por la libreria MuPDf 1.9.2.
# Se apoya en las etiquetas "span", "char".
# La salida es un archivo.csv conforme al siguiente formato :
# (COD_ASIGNATURA,BLOQUE,LUNES,MARTES,MIERCOLES,JUEVES,VIERNES)

import fitz # Usando MuPDf 1.9.2
import xml.sax
import re
from decimal import Decimal
from os.path import isfile
from os import remove
from procesadorPDF import OfertasGeneral, obtArgs, usoAyuda, componerHorarioCSV
import sys
import getopt

class OfertasDace( OfertasGeneral ):
    def __init__(self):
        # Se omite pasar la lista de materias requeridas dado que en el
        #documento se conoce cuales son las de carrera por su código
        self.listaMat = []
        OfertasGeneral.__init__(self,self.listaMat)
        self.listaHorarios = []
        self.listaBloque = []
        self.listaMaterias = []
        self.patronMateria = "(\w\w\d\d\d\d|\w\w\w\d\d\d)"
        self.paddReconHorario = 5

   # Call when an element starts
    def startElement(self, tag, attributes):
        if tag == "char":
            self.celda += attributes["c"]

        if tag == "span":
            self.posCaracteres = \
                (attributes['bbox'].split(" ")[0],
                 attributes['bbox'].split(" ")[1],
                 attributes['bbox'].split(" ")[2],
                 attributes['bbox'].split(" ")[3])

   # Call when an elements ends
    def endElement(self, tag):
        #Se omite las lineas de contorno del documento
        if tag == "span" and self.celda[0] != '-':
            #print("Celda", self.celda)
            if not self.cabeceraLista:
                self.cabeceraLista = \
                    self.filtroCabecera(self.celda, self.posCaracteres)

            self.filtrarTexto(self.celda.strip(),self.posCaracteres)
            self.celda = ""
            self.posCaracteres = []

    # Encuentra los dias de semana en la página y guarda sus posiciones.
    def filtroCabecera(self,txt, posCaracteres):
        searchDias = re.search(self.patronDias, txt, re.I)
        if searchDias:
            #print(searchDias)
            longPalabra = len(txt)
            #print("posCaracteres", txt , posCaracteres)
            self.cabeceraDias.append((searchDias.group()[0:2],
                                      Decimal(posCaracteres[0]),
                                      Decimal(posCaracteres[2])))

        # if len(self.cabeceraDias) == 5:
        #     print("Cabecera Lista: ", self.cabeceraDias)
        return len(self.cabeceraDias) == 5

    def filtrarTexto(self,txt, posCaracteres):
        searchMat = re.search(self.patronMateria, txt, re.I)
        if searchMat:
            #print(searchMat)
            self.listaMaterias.append((searchMat.group(),
                       Decimal(posCaracteres[1]),Decimal(posCaracteres[3])))
        elif re.search(self.patronBloque, txt, re.I):
            #print(re.search(self.patronBloque, txt, re.I))
            self.listaBloque.append((txt,Decimal(posCaracteres[1]),
                                     Decimal(posCaracteres[3])))

        elif self.cabeceraLista and re.search(self.patronHoras, txt):
            #print(re.search(self.patronHoras, txt))
            for (dia,limInf,limSup) in self.cabeceraDias:
                # print(dia + ':', limInf - self.paddReconHorario, "limInf <=",
                #   "posIniDia ", Decimal(self.posCaracteres[0]),
                #   "posFinTxt", Decimal(self.posCaracteres[0]),"<= posFinDia",
                #   limSup + self.paddReconHorario)
                if (limInf - self.paddReconHorario) <= Decimal(posCaracteres[0]) \
                    and Decimal(posCaracteres[2]) <= (limSup + self.paddReconHorario):
                    self.listaHorarios.append((txt,dia.upper(),
                        Decimal(posCaracteres[1]),Decimal(posCaracteres[3])))
                    #print((txt,dia.upper(),Decimal(posCaracteres[1]),Decimal(posCaracteres[3])))
                    break

    def procesarPDF(self,codigoCarr,nombreArchivoEntrada, fdSalida):
        doc = fitz.open(nombreArchivoEntrada)
        # create an XMLReader
        parser = xml.sax.make_parser()
        # turn off namepsaces
        parser.setFeature(xml.sax.handler.feature_namespaces, 0)
        # override the default ContextHandler
        parser.setContentHandler( self )

        # Procesar las páginas del PDF. Se examina por
        # codigo de carrera cada página. Al encontrar el encontrarlo,
        # se extrae el texto del documento en archivo XML; luego se procesa.
        for num in range(doc.pageCount):
            page = doc.loadPage(num)
            if page.searchFor(codigoCarr):
                xmlText = page.getText(output = "xml")
                f = open('textPDFXML.xml', 'w')
                f.write(xmlText)
                f.close()
                # Procesar el archivo XML
                parser.parse('textPDFXML.xml')


        remove('textPDFXML.xml')

        tuplas = []
        for ((mat,mtechoAlto,mtechoBajo),(bloq,btechoAlto,btechoBajo)) \
            in zip(self.listaMaterias,self.listaBloque):
            #print(([mat,bloq],btechoAlto,btechoBajo))
            tuplas.append(([mat,bloq],btechoAlto,btechoBajo))


        for (fila,ftechoAlto,ftechoBajo) in tuplas:
            listaHoras = []
            listaHorasBorrar = []
            for (horas,dia,htechoAlto, htechoBajo) in self.listaHorarios:
                # print(horas,dia,ftechoAlto,htechoAlto - Decimal(0.3),
                #     htechoBajo + Decimal(0.3), ftechoBajo)
                #print("Itera", horas,dia, ftechoAlto,htechoAlto - Decimal(0.3), htechoBajo + Decimal(0.3), ftechoBajo)
                if  (htechoBajo + Decimal(0.3)) >= (ftechoBajo) \
                    and ftechoAlto >= (htechoAlto - Decimal(0.3) ):
                    listaHoras.append((horas,dia))
                    listaHorasBorrar.append((horas,dia,htechoAlto, htechoBajo))

            # Eliminar horarios agregados
            for i in listaHorasBorrar:
                #print("Eliminar", i)
                self.listaHorarios.remove(i)

            if listaHoras:
                #print(componerHorarioCSV(listaHoras)[1:])
                fila += componerHorarioCSV(listaHoras)[1:].split(',')
            else:
                fila += ",,,,"

            #print(fila, listaHoras)
            fdSalida.append(fila)



if ( __name__ == "__main__"):
    (nomArchivoSalida, nomArchivoMaterias, args) = obtArgs(sys.argv[1:])

    listaMaterias = []
    for materia in open(nomArchivoMaterias, 'r'):
        if (not materia.isspace()) and materia[0] != '#':
            listaMaterias.append(materia.rstrip(' \t\n\r'))

    fdSalida = []
    manejador = OfertasDace()
    manejador.procesarPDF("0800",args[0],fdSalida)

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

