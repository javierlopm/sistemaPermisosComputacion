#!/usr/bin/python3.5
#!/usr/bin/python3.4

# Nombre: Daniel Leones
# Carné: 09-10977
# Fecha: 26/10/2016
# Descripción: Procesa los archivos xml producidos por la libreria MuPDf 1.9.2.
# Se apoya en las etiquetas "<span>" y "<char>". Este procesador es específico
# al formato PDF de lista de materias de DACE.
# En caso que se haya un archivo de salida, su formato será CSV conforme al
# siguiente formato :
# COD_ASIGNATURA,BLOQUE,LUNES,MARTES,MIERCOLES,JUEVES,VIERNES
# En otro caso, se devuelve una [fila1,fila2,..., filaN] al estilo CSV de acuerdo
# al formato anterior.

# Notas:
# Se aprovecha las variables y funciones definidas en procesadorPDF.
# Se redefinen los métodos de OfertasGeneral.

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
        OfertasGeneral.__init__(self,None)
        self.listaHorarios = []
        self.listaBloque = []
        self.listaMaterias = []
        self.patronMateria = "(\w\w\d\d\d\d|\w\w\w\d\d\d)"
        self.paddReconHorario = 5

   # Call when an element starts
    def startElement(self, tag, attributes):
        # Acumulan las caracteres
        if tag == "char":
            self.celda += attributes["c"]

        # Guardar las posiciones para comparaciones. Esta etiqueta anida <char>
        # directamente.
        if tag == "span":
            self.posCaracteres = \
                (attributes['bbox'].split(" ")[0],
                 attributes['bbox'].split(" ")[1],
                 attributes['bbox'].split(" ")[2],
                 attributes['bbox'].split(" ")[3])

   # Call when an elements ends
    def endElement(self, tag):
        # Se procesa el texto acumulado en self.celda.
        # Se omite las lineas separadoras del documento.
        if tag == "span" and self.celda[0] != '-':
            #print("Celda", self.celda)
            if not self.cabeceraLista:
                self.cabeceraLista = \
                    self.filtroCabecera(self.celda, self.posCaracteres)

            self.filtrarTexto(self.celda.strip(),self.posCaracteres)
            self.celda = ""
            self.posCaracteres = []

    # Procesa la cabecera de los dias de semana en la página y guarda sus posiciones.
    def filtroCabecera(self,txt, posCaracteres):
        searchDias = re.search(self.patronDias, txt, re.I)
        if searchDias:
            #print(searchDias)
            #print("posCaracteres", txt , posCaracteres)
            self.cabeceraDias.append((searchDias.group()[0:2],
                                      Decimal(posCaracteres[0]),
                                      Decimal(posCaracteres[2])))

        # if len(self.cabeceraDias) == 5:
        #     print("Cabecera Lista: ", self.cabeceraDias)
        return len(self.cabeceraDias) == 5

    # Procesa cadenas encontradas por materias, bloque u horarios.
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

def procesarDACE(codigoCarr,nombreArchivoEntrada,fdSalida):
    doc = fitz.open(nombreArchivoEntrada)
    # create an XMLReader
    parser = xml.sax.make_parser()
    # turn off namepsaces
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)

    # Procesar las páginas del PDF. Se examina por
    # codigo de carrera cada página. Al encontrar ,se extrae el texto del
    # documento en archivo XML; luego se procesa.
    for num in range(doc.pageCount):
        page = doc.loadPage(num)
        if page.searchFor(codigoCarr):
            #print("pag.", num + 1)
            try:
                f = open('textPDFXML.xml', 'w')
                f.write(page.getText(output = "xml"))
            except OSError as ose:
                print("Error de E/S: ", ose)
            else:
                contenedor = OfertasDace()
                # override the default ContextHandler
                parser.setContentHandler( contenedor )
                # Procesar el archivo XML
                parser.parse('textPDFXML.xml')

            # Juntar listas de materias con lista de bloques. Se conserva
            # las posiciones para comparación de los horarios.
            tuplas = []
            for ((mat,mtechoAlto,mtechoBajo),(bloq,btechoAlto,btechoBajo)) \
                in zip(contenedor.listaMaterias,contenedor.listaBloque):
                #print(([mat,bloq],btechoAlto,btechoBajo))
                tuplas.append(([mat,bloq],btechoAlto,btechoBajo))

            # Acoplar los horarios junto a las materias y los bloques.
            for (fila,ftechoAlto,ftechoBajo) in tuplas:
                listaHoras = []
                listaHorasBorrar = []
                for (horas,dia,htechoAlto, htechoBajo) in contenedor.listaHorarios:
                    # print(horas,dia,ftechoAlto,htechoAlto - Decimal(0.3),
                    #     htechoBajo + Decimal(0.3), ftechoBajo)
                    #print("Itera", horas,dia, ftechoAlto,htechoAlto - Decimal(0.3), htechoBajo + Decimal(0.3), ftechoBajo)

                    # Se compara las posiciones verticales de los horarios y los
                    # bloques y se agregan en una lista para borrarlas de la
                    # lista original.
                    if  (htechoBajo + Decimal(0.3)) >= (ftechoBajo) \
                        and ftechoAlto >= (htechoAlto - Decimal(0.3) ):
                        listaHoras.append((horas,dia))
                        listaHorasBorrar.append((horas,dia,htechoAlto, htechoBajo))

                # Eliminar horarios agregados
                for i in listaHorasBorrar:
                    #print("Eliminar", i)
                    contenedor.listaHorarios.remove(i)

                # Procesar los horarios en formato CSV
                if listaHoras:
                    #print(componerHorarioCSV(listaHoras)[1:])
                    fila += componerHorarioCSV(listaHoras)[1:].split(',')
                else:
                    fila += ['','','','','']
                    #print(fila, listaHoras)

                fdSalida.append(fila)

    f.close()
    remove('textPDFXML.xml')


if ( __name__ == "__main__"):
    (nomArchivoSalida, nomArchivoMaterias, args) = obtArgs(sys.argv[1:])

    fdSalida = []
    procesarDACE("0800",args[0],fdSalida)

    if isfile(nomArchivoSalida):
        remove(nomArchivoSalida)

    if nomArchivoSalida:
        try:
            f = open(nomArchivoSalida, 'a')
            f.write("COD_ASIGNATURA,BLOQUE,L,M,MI,J,V\n")
        except IsADirectoryError:
            print(nomArchivoSalida ,"es un directorio. Eliga un nombre distinto")
            nomArchivoSalida = raw_input("Introduzca el nombre del archivo de salida: ")
        except OSError as ose:
            print("Error de E/S: ", ose)
    else:
        print("COD_ASIGNATURA,BLOQUE,L,M,MI,J,V")


    for fila in fdSalida:
        if nomArchivoSalida:
            try:
                f.write(','.join(fila) + "\n")
            except OSError as ose:
                print("Error de E/S: ", ose)
        else:
            print(','.join(fila))

    if nomArchivoSalida:
        f.close()

