#!/usr/bin/python3

# Nombre: Daniel Leones
# Carné: 09-10977
# Fecha: 7/12/2016
# Descripción: procesa los archivos xml producidos por la libreria MuPDf 1.9.2.
# Se apoya en las etiquetas "<span>" y "<char>".
# En caso que se haya un archivo de salida, su formato será CSV conforme al
# siguiente formato :
# COD_ASIGNATURA,BLOQUE,LUNES,MARTES,MIERCOLES,JUEVES,VIERNES, ESPECIAL
# En otro caso, se devuelve una [fila1,fila2,..., filaN] al estilo CSV de acuerdo
# al formato anterior.
# El procesador reconoce los estilos:
#   Códigos, Bloques o sección, horarios. (Estilo computo)
#   Código, Nombre Asignatura, Bloque, Lunes, Martes, Miercoles,
#        Jueves, Viernes, Carrera. (Estilo general)
# Al reconocer alguno de estos, será notificado por la salida estandar.

# Se utilizan expresiones regulares para reconocer el contenido relevantes.
# Las variables *self.patrónX* contiene los patrones utilizados.
# Las posiciones se guardan se comparar contra las posiciones de los elementos reconocidos.
# Esquema:
# -----limSup (posición + paddingRecon)-----
#       -----posSup-----
#       elemento por asignar
#       -----posInf-----
# -----limInf (posición - paddingRecon) -----
#

import fitz     # Usando MuPDf 1.9.2
import xml.sax
import re
import sys
from decimal import Decimal
from os.path import isfile
from os import remove
from funcionesAuxiliares import dividirStr, obtArgs, cargarMaterias, \
                                  componerHorarioCSV, normalizarMateria,  \
                                  ordenarDias, usoAyuda

#
# Clase utilizada para parsing del XML exportado por PyMuPDF.
#
class OfertasGeneral( xml.sax.ContentHandler ):
    def __init__(self, listaMaterias):
        # Acumuladores
        self.filaMatBloq = []
        self.filaHorario = []
        self.celda = ""
        self.posCaracteres = []
        self.cabeceraDias = []
        self.cabeceraDiasTest = []
        # Lista de materias
        self.listaMaterias = listaMaterias
        # Modos de operación
        self.cabeceraLista = False
        self.modoHorario = False
        self.bloque = False
        # Patrones de recocimiento usados por las expresiones regulares
        self.patronHoras = "\d{1,2}(-\d{1,2})?"
        self.patronDias = "(L[Uu][Nn](\.|es)?|M[Aa][Rr](\.|tes)?|" + \
            "M[Ii][Ee](\.|rcoles|r)?|[Jj][Uu][Ee](\.|ves)?|V[Ii][Ee](\.|es|r)?)"
        self.patronMateria = "[A-Z][A-Z]\s*-?\s*\d\d\d\d"
        self.patronBloque1 = "^\(?[A-Z]\)?$"
        self.patronBloque2 = "\(?[Bb][Ll][Oo][Qq][Uu]?[Ee]?\s+[A-Z]\)?"
        self.patronSeccion = "\(?Sec.?i?ó?n?(\s)+\d\)?"
        self.corresSecBloq = { '1' : 'A', '2' : 'B', '3' : 'C', '4' : 'D', '5' : 'E'}
        self.patronHorario = self.patronDias + "((\s*(-|–)\s*)" + self.patronDias + ")?" \
            + "\s+" + self.patronHoras
        self.patronHorario2 = "(" + self.patronDias + "\s+" + self.patronHoras + \
            "(\s+(-|–)?\s+)?){1,}"
        self.patronDiasFrac = self.patronDias + "(\s*-\s*" + self.patronDias + ")?"

    # Función: endElement
    # Argumentos:
    #   tag:        String, nombre de la etiqueta proveniente del documento XML.
    #   atributes:  String, atributos de la etiqueta XML.
    # Salida: Ninguna
    #
    # Descripción: ejecutar una acción por cada etiqueta inicial
    def startElement(self, tag, attributes):
        if tag == "char":
            # Se acumulan las caracteres a través del atributo.
            self.celda += attributes["c"]

        # Guardar las posiciones para comparaciones. Esta etiqueta anida <char>
        # directamente.
        if tag == "span":
            self.posCaracteres = \
                (attributes['bbox'].split(" ")[0],
                 attributes['bbox'].split(" ")[1],
                 attributes['bbox'].split(" ")[2],
                 attributes['bbox'].split(" ")[3])

    # Función: endElement
    # Argumentos:
    #   tag: String, nombre etiqueta proveniente del documento XML.
    # Salida: Ninguna
    #
    # Descripción: ejecutar una acción por cada etiqueta final
    def endElement(self, tag):
        if tag == "span":
            # Leer cabecera
            if not self.cabeceraLista:
                self.cabeceraLista = \
                    self.filtroCabecera(self.celda, self.posCaracteres)

            # Modos de procesamiento del texto
            if self.modoHorario:
                self.filtrarTextoEstiloComputo(self.celda.strip())
            else:
                self.filtrarTexto(self.celda.strip())

            self.celda = ""
            self.posCaracteres = []

    # Función: characters
    # Argumentos:
    #   content: String
    # Salida: Ninguna
    #
    # Descripción: ejecutar una acción al encontrar al menos un caracter.
    def characters(self, content):
        pass

    # Función: filtroCabecera
    # Argumentos:
    #   txt: String
    #   posCaracterres: una tupla (String,String,String,String)
    # Salida: Booleano, Detener y seguir el análisis de la cabecera
    #
    # Descripción: procesa la cabecera de los dias de semana en la página y
    # guarda sus posiciones. Se imprime los dias reconocidos.
    def filtroCabecera(self,txt, posCaracteres):
        searchDias = re.search(self.patronDias, txt, re.I)
        if searchDias:
            self.cabeceraDias.append((searchDias.group()[0:2],
                                      Decimal(posCaracteres[0]),
                                      Decimal(posCaracteres[2])))
            self.cabeceraDiasTest.append(searchDias.group())
            if len(self.cabeceraDias) == 5:
                print("Reconocimiento:\n\t", self.cabeceraDiasTest, end='\n\n')
                return True

        if re.search("horarios?" , txt, re.I):
            self.modoHorario = True
            print("Reconocimiento:\n\tModo horario (estilo computo):",
                  self.modoHorario, end='\n\n')
            return True

        return False

    # Función: filtrarTextoEstiloComputo
    # Argumentos:
    #   txt: String
    # Salida: Ninguna
    #
    # Descripción: procesa cadenas de código de materias, bloque y horarios
    # de acuerdo al estilo del departamento de cómputo.
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
        if searchBloq2:
            self.filaMatBloq.append((dividirStr(searchBloq2.group(),' ()')[1],
                              Decimal(self.posCaracteres[1]),
                              Decimal(self.posCaracteres[3])))
            self.bloque = True

        # En caso de no haber bloques sino Sección, se lee e interpreta como bloque
        elif not self.bloque and searchSeccion:
            self.filaMatBloq.append((self.corresSecBloq[
                             dividirStr(searchSeccion.group(),' ()')[1]],
                             Decimal(self.posCaracteres[1]),
                             Decimal(self.posCaracteres[3])))
            self.bloque = False

        # Reconocer horarios de acuerdo a: Dia-Dia Hora ó Dia Hora.
        if searchHorario or searchHorario2:
            for hor in self.normalizarHorario(
                              dividirStr(txt)):
                txt = dividirStr(hor)
                dias = dividirStr(txt[0],"-")
                # Garantizar que solo los digitos de las horas
                txt =  txt[1][0:4]
                # Los horarios se almacenan en la forma (dia,posInf,posSup)
                # donde dias son las primeras 2 letras del día.
                if len(dias) > 1:
                    self.filaHorario.append((txt,dias[0][0:2].upper(),
                              Decimal(self.posCaracteres[1]),
                              Decimal(self.posCaracteres[3])))
                    self.filaHorario.append((txt,dias[1][0:2].upper(),
                              Decimal(self.posCaracteres[1]),
                              Decimal(self.posCaracteres[3])))
                else:
                    self.filaHorario.append((txt,dias[0][0:2].upper(),
                              Decimal(self.posCaracteres[1]), Decimal(self.posCaracteres[3])))

    # Función: filtrarTexto
    # Argumentos:
    #   txt: String
    # Salida: Ninguna
    #
    # Descripción: procesa cadenas de código de materias, bloque y horarios
    # de acuerdo al estilo del departamento de cómputo.
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
            for (dia,limInf,limSup) in self.cabeceraDias:
                if (limInf - 3) <= Decimal(self.posCaracteres[0]) \
                    and Decimal(self.posCaracteres[2]) <= (limSup + 3):
                    self.filaHorario.append((txt,dia,
                                     Decimal(self.posCaracteres[1]),
                                    Decimal(self.posCaracteres[3])))
                    #print((txt,dia))
                    break
        return

    # Función: subdividirFilas
    # Argumentos:
    #   ninguno
    # Salida: [[String]]
    #
    # Descripción: ensamblar las asignaturas, bloques y horarios reconocidos.
    def subdividirFilas(self):
        nuevaFila = []
        tuplas = []
        materiaValida = False
        pSupFila = None
        pInfFila = None
        # Token para reconocer final de la lista
        self.filaMatBloq.append(('$',0,0))
        for (item, pSup, pInf) in self.filaMatBloq:
            # Partir fila de asignatura 
            if re.search(self.patronMateria, item, re.I) or item == '$':
                if nuevaFila and (nuevaFila[0] in self.listaMaterias):
                    # Acoplar horarios a la fila a partir.
                    for (hora,dia,pSupH,pInfH) in self.filaHorario:
                        if pSupFila <= pSupH and pInfFila  >= pInfH:
                            nuevaFila.append((hora,dia))

                    tuplas.append(nuevaFila)

                nuevaFila = []
                nuevaFila.append(item)
                pSupFila = pSup - 6
                pInfFila = pInf + 12
            elif pSupFila <= pSup and pInfFila  >= pInf:
                nuevaFila.append(item)

        return tuplas

    # Función: subdividirFilas
    # Argumentos:
    #   ninguno
    # Salida: [[String]]
    #
    # Descripción: ensamblar las asignaturas, bloques y horarios reconocidos.
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

# Función: procesarPDF
# Argumentos:
#   nombreArchivoEntrada: String, camino hacia 
#   listaMaterias, 
#   fdSalida
# Salida: [[String]], lista de ofertas
#
# Descripción: función principal de procesamiento. Leer cada pagina y capturar
# los datos pertinentes.
def procesarPDF(nombreArchivoEntrada, listaMaterias, fdSalida):
    doc = fitz.open(nombreArchivoEntrada)
    # Crear un lector XML
    parser = xml.sax.make_parser()
    # Desactivar namespaces
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

    # Concatenar en un solo string e imprimir filas en formato CSV.
    for fil in Handler.subdividirFilas():
        if fil:
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

            elif len(fil) == 1:
                acum = fil[0] + ',A,,,,,,Y'

            fdSalida.append(acum.split(','))
            acum = ""

# Programa principal para ejecutar el procesador invidualmente.
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
            f.write("COD_ASIGNATURA,BLOQUE,L,M,MI,J,V,ESPECIALES\n")
        except IsADirectoryError:
            print(nomArchivoSalida ,"es un directorio. Se requiere un archivo")
            sys.exit(2)
        except OSError as ose:
            print("Error de E/S: ", ose)
            sys.exit(2)
    else:
        print("COD_ASIGNATURA,BLOQUE,L,M,MI,J,V,ESPECIALES")

    # Escribir resultados
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
