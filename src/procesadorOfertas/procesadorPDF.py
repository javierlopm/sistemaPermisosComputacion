#!/usr/bin/python3.5
#!/usr/bin/python3.4

# Nombre: Daniel Leones
# Carné: 09-10977
# Fecha: 26/10/2016
# Descripción: Procesa los archivos xml producidos por la libreria MuPDf 1.9.2.
# Se apoya en las etiquetas "<span>" y "<char>".
# En caso que se haya un archivo de salida, su formato será CSV conforme al
# siguiente formato :
# COD_ASIGNATURA,BLOQUE,LUNES,MARTES,MIERCOLES,JUEVES,VIERNES
# En otro caso, se devuelve una [fila1,fila2,..., filaN] al estilo CSV de acuerdo
# al formato anterior.

import fitz # Usando MuPDf 1.9.2
import xml.sax
import re
import sys
from decimal import Decimal
from os.path import isfile
from os import remove
from funcionesAuxiliares import dividirStr, obtArgs, cargarMaterias, \
                                  componerHorarioCSV, normalizarMateria,  \
                                  ordenarDias, usoAyuda

class OfertasGeneral( xml.sax.ContentHandler ):
    def __init__(self, listaMaterias):
        self.filaMatBloq = []
        self.filaHorario = []
        self.posCaracteres = []
        self.cabeceraDias = []
        self.celda = ""
        self.listaMaterias = listaMaterias
        self.cabeceraLista = False
        self.existeCarrera = False
        self.modoHorario = False
        self.bloque = False
        self.patronHoras = "\d{1,2}(-\d{1,2})?"
        self.patronDias = "(L[Uu][Nn](\.|es)?|M[Aa][Rr](\.|tes)?|" + \
            "M[Ii][Ee](\.|rcoles|r)?|[Jj][Uu][Ee](\.|ves)?|V[Ii][Ee](\.|es|r)?)"
        self.patronMateria = "[A-Z][A-Z]\s*-?\s*\d\d\d\d"
        self.patronBloque1 = "^\(?[A-Z]\)?$"
        self.patronBloque2 = "\(?[Bb][Ll][Oo][Qq][Uu]?[Ee]?(\s)+[A-Z]\)?"
        self.patronSeccion = "\(?Sec.?i?ó?n?(\s)+\d\)?"
        self.patronCarrera = "0?800"
        self.corresSecBloq = { '1' : 'A', '2' : 'B', '3' : 'C', '4' : 'D', '5' : 'E'}
        self.patronHorario = self.patronDias + "((\s*(-|–)\s*)" + self.patronDias + ")?" \
            + "\s+" + self.patronHoras
        self.patronHorario2 = "(" + self.patronDias + "\s+" + self.patronHoras + \
            "(\s+(-|–)?\s+)?){1,}"
        self.patronDiasFrac = self.patronDias + "(\s*-\s*" + self.patronDias + ")?"

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
        if tag == "span":
            #print("Celda", self.celda, self.posCaracteres)
            #print("Celda", self.celda)
            if not self.cabeceraLista:
                self.cabeceraLista = \
                    self.filtroCabecera(self.celda, self.posCaracteres)
            else:
                if re.search("Carreras?", self.celda, re.I):
                    #print("existeCarrera END")
                    self.existeCarrera = True

                #print("Celda", self.celda)
                if self.modoHorario:
                    self.filtrarTextoEstiloComputo(self.celda.strip())
                else:
                    self.filtrarTexto(self.celda.strip())

            self.celda = ""
            self.posCaracteres = []

    # def verificarFila(fila, patronHoras, patronMateria, patronBloque):
    #     nuevaFila = fila.split(',')
    #     cent = len(nuevafila) < 6

    #     for item in nuevafila:
    #         if re.search(item,patronHoras)
    #             cent = True and cent
    #         elif re.search(item,patronMateriam re:i)

   # Call when a character is read
    def characters(self, content):
        pass

    # Encuentra los dias de semana y guarda sus posiciones en la página.
    def filtroCabecera(self,txt, posCaracteres):
        searchDias = re.search(self.patronDias, txt, re.I)
        if searchDias:
            # print("posCaracteres", txt , posCaracteres)
            self.cabeceraDias.append((searchDias.group()[0:2],
                                      Decimal(posCaracteres[0]),
                                      Decimal(posCaracteres[2])))

            return len(self.cabeceraDias) == 5
        elif re.search("horarios?" , txt, re.I):
            self.modoHorario = True
            return True

        # if len(self.cabeceraDias) == 5:
        #     print("Cabecera Lista: ", self.cabeceraDias)

    def filtrarTextoEstiloComputo(self,txt):
        searchMat = re.search(self.patronMateria, txt, re.I)
        searchBloq2 = re.search(self.patronBloque2, txt, re.I)
        searchHorario = re.search(self.patronHorario, txt, re.I)
        searchHorario2 = re.search(self.patronHorario2, txt, re.I)
        searchSeccion = re.search(self.patronSeccion, txt, re.I)

        if searchMat:
            self.filaMatBloq.append((normalizarMateria(searchMat.group()),
                              Decimal(self.posCaracteres[1]),
                              Decimal(self.posCaracteres[3])))
            #print(searchHorario2)
            #print(searchBloq2)
        elif searchBloq2:
            #print(dividirStr(searchBloq2.group())[1])
            self.filaMatBloq.append((dividirStr(searchBloq2.group())[1],
                              Decimal(self.posCaracteres[1]),
                              Decimal(self.posCaracteres[3])))
            self.bloque = True
        elif not self.bloque and searchSeccion:
            #print(searchSeccion)
            self.filaMatBloq.append((self.corresSecBloq[
                             dividirStr(searchSeccion.group(),' ()')[1]],
                             Decimal(self.posCaracteres[1]),
                             Decimal(self.posCaracteres[3])))
            self.bloque = False

        elif searchHorario or searchHorario2:
            #print(self.normalizarHorario(dividirStr(txt)))
            for hor in self.normalizarHorario(
                              dividirStr(txt)):
                #print("hor", hor)
                txt = dividirStr(hor)
                dias = dividirStr(txt[0],"-")
                # Garantizar que solo los digitos de las horas
                txt =  txt[1][0:4]
                #print(dias, txt)
                if len(dias) > 1:
                    #print((txt,dias[0][0:2].upper()), "   ", (txt,dias[1][0:2].upper()))
                    self.filaHorario.append((txt,dias[0][0:2].upper(),
                              Decimal(self.posCaracteres[1]),
                              Decimal(self.posCaracteres[3])))
                    self.filaHorario.append((txt,dias[1][0:2].upper(),
                              Decimal(self.posCaracteres[1]),
                              Decimal(self.posCaracteres[3])))
                else:
                    #print((txt,dias[0][0:2].upper()))
                    self.filaHorario.append((txt,dias[0][0:2].upper(),
                              Decimal(self.posCaracteres[1]), Decimal(self.posCaracteres[3])))

    def filtrarTexto(self,txt):
        searchMat = re.search(self.patronMateria, txt, re.I)
        if searchMat:
            self.filaMatBloq.append((normalizarMateria(searchMat.group()),
                                Decimal(self.posCaracteres[1]),
                                Decimal(self.posCaracteres[3])))

        elif re.search(self.patronBloque1, txt, re.I):
                self.filaMatBloq.append((txt,
                              Decimal(self.posCaracteres[1]),
                              Decimal(self.posCaracteres[3])))

        elif re.search(self.patronHoras, txt):
            #print(re.search(self.patronHoras, txt))
            #print(self.fila[0])
            for (dia,limInf,limSup) in self.cabeceraDias:
                # print(limInf, "posIniTxt <=", dia, "posIniDia ", Decimal(self.posCaracteres[0][0]), \
                #       "posFinTxt", Decimal(self.posCaracteres[-1][0]),"<= posFinDia", limSup )
                if (limInf - 3) <= Decimal(self.posCaracteres[0]) \
                    and Decimal(self.posCaracteres[2]) <= (limSup + 3):
                    self.filaHorario.append((txt,dia,
                                     Decimal(self.posCaracteres[1]),
                                    Decimal(self.posCaracteres[3])))
                    #print((txt,dia))
                    break

        # elif self.existeCarrera and re.search(self.patronCarrera, txt):
        #     #print(self.fila)
        #     self.tuplas.append(self.fila)
        #     self.fila = []

    def subdividirFilas(self):
        nuevaFila = []
        tuplas = []
        materiaValida = False
        pSupFila = None
        pInfFila = None
        self.filaMatBloq.append(('$',0,0))
        for (item, pSup, pInf) in self.filaMatBloq:
            #print("Mi item", item)
            if re.search(self.patronMateria, item, re.I) or item == '$':
                if nuevaFila and nuevaFila[0] in self.listaMaterias:
                    for (hora,dia,pSupH,pInfH) in self.filaHorario:
                        if pSupFila <= pSupH and pInfFila  >= pInfH:
                            nuevaFila.append((hora,dia))

                    #print("Nueva Fila", nuevaFila)
                    tuplas.append(nuevaFila)

                nuevaFila = []
                nuevaFila.append(item)
                pSupFila = pSup - 5
                pInfFila = pInf + 12
            elif pSupFila <= pSup and pInfFila  >= pInf:
                nuevaFila.append(item)

            #print("pSupFila", pSupFila - 5, "<=", pSup, "pInfFila", pInfFila + 5, ">=", pInf)
        # print("Tuplas")
        # for item in tuplas:
        #     print(item)
        return tuplas


    def normalizarHorario(self,txt):
        hor = ""
        nuevoTxt = []
        fragmentado = False
        for item in txt:
            if item != "" and item != "-":
                if re.search('^\s*' + self.patronHoras + '\s*$', item, re.I):
                    hor += ' ' + item.strip()
                else:
                    hor += item
                #print(hor, "||", item)
                # Reconocer horarios completos
                if re.search(self.patronHorario, hor, re.I):
                    #print("frag completo")
                    nuevoTxt.append(hor)
                    hor = ""
                # Parte de dias fraccionado.
                elif re.search(self.patronDiasFrac, hor, re.I):
                    #print("frag")
                    hor = "".join(dividirStr(hor))

        return nuevoTxt

def procesarPDF(nombreArchivoEntrada, listaMaterias, fdSalida):
    doc = fitz.open(nombreArchivoEntrada)
    # create an XMLReader
    parser = xml.sax.make_parser()
    # turn off namepsaces
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)
    Handler = OfertasGeneral(listaMaterias)
    # override the default ContextHandler
    parser.setContentHandler( Handler )

    for num in range(0,doc.pageCount):
        # Procesar los PDFs usando MuPDF. Se extrae el texto del documento en
        # archivo XML.
        page = doc.loadPage(num)
        # Crear un archivo temporal
        try:
            f = open('textPDFXML1.xml', 'w')
            f.write(page.getText(output = "xml"))
        except OSError as ose:
            print("Error de E/S: ", ose)
        else:
            # Procesar el archivo XML
            parser.parse("textPDFXML1.xml")

    f.close()
    remove('textPDFXML1.xml')

    # Ordenar de acuerdo al formato (COD_ASIGNATURA,BLOQUE,L,M,MI,J,V)
    # Concatenar en un solo string e imprimir filas en formato CSV.
    for fil in Handler.subdividirFilas():
        if fil:
            #print(fil)
            if len(fil) > 1:
                #print("Fila", fil, "\nhorario", fil[1:], "\n")
                if isinstance(fil[1],tuple):
                    acum = fil[0] + ',A'
                    #print("Seleccion1", fil[1:])
                    horariosOrdenados = sorted(fil[1:], key=ordenarDias)
                else:
                    #print("Seleccion2", fil[2:])
                    acum = ",".join(fil[:2])
                    horariosOrdenados = sorted(fil[2:], key=ordenarDias)

                if horariosOrdenados:
                    acum += componerHorarioCSV(horariosOrdenados)
                else:
                    acum += ',,,,,'

            elif len(fil) == 1:
                acum = fil[0] + ',A,,,,,'

            fdSalida.append(acum.split(','))
            acum = ""


if ( __name__ == "__main__"):
    (nomArchivoSalida, nomArchivoMaterias, args) = obtArgs(sys.argv[1:])

    listaMaterias = cargarMaterias(nomArchivoMaterias)

    fdSalida = []
    procesarPDF(args[0],listaMaterias,fdSalida)

    if isfile(nomArchivoSalida):
        remove(nomArchivoSalida)

    if nomArchivoSalida:
        try:
            f = open(nomArchivoSalida, 'a')
            f.write("COD_ASIGNATURA,BLOQUE,L,M,MI,J,V\n")
        except IsADirectoryError:
            print(nomArchivoSalida ,"es un directorio. Se requiere un archivo")
            sys.exit(2)
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

    # doc = fitz.open('pruebas/doc2.pdf')
    # page = doc.loadPage(0)
    # xmlText = page.getText(output = "xml")
    # f = open('xmlPDF.txt', 'w')
    # f.write(xmlText)
    # f.close()

    # x = ['CO2112', ('1-2', 'MA'), ('1-2', 'JU'), ('5-6', 'JU'),
    #  'CO2113', ('3-4', 'MA'), ('3-4', 'JU'),
    #  'CO3121', ('1-2', 'LU'), ('1-2', 'MI')]
    # print(subdividirFilas(x))

    # h = OfertasGeneral([])
    # x = "Lun 5-6 - Mie 5-6"
    # x = "Mie 3-5"
    # print(dividirStr(x))
    # y = dividirStr(x)
    # print(h.normalizarHorario(y))
