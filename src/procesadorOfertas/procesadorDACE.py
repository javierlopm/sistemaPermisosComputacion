#!/usr/bin/python3.5
#!/usr/bin/python3.4

# Nombre: Daniel Leones
# Carné: 09-10977
# Fecha: 7/12/2016
# Descripción: Procesa los archivos xml producidos por la libreria MuPDf 1.9.2.
# Se apoya en las etiquetas "<span>" y "<char>" emitidas por la libreria .
# Este procesador es específico al formato PDF de lista de materias de DACE.
# Si se utiliza -f, su formato será CSV conforme al siguiente formato :
# COD_ASIGNATURA,BLOQUE,LUNES,MARTES,MIERCOLES,JUEVES,VIERNES
# En otro caso, se devuelve una [fila1,fila2,..., filaN] al estilo CSV de acuerdo
# al formato anterior.

# Se utilizan expresiones regulares para reconocer el contenido relevantes. Las variables *self.patrónX*
# contiene los patrones utilizados.
# Las posiciones que se guardan se comparar contras las posiciones de los elementos reconocidos.
# Esquema:
# -----limSup (posición + paddingRecon)-----
#       -----posSup-----
#       elemento por asignar
#       -----posInf-----
# -----limInf (posición - paddingRecon) -----
#

# Notas:
# Se aprovecha las variables y funciones definidas en procesadorPDF.
# Se redefinen los métodos de OfertasGeneral.

import fitz     # Usando MuPDf 1.9.2
import xml.sax
import re       # Expresiones regulares
from decimal import Decimal
from os.path import isfile
from os import remove
from procesadorPDF import OfertasGeneral, obtArgs, usoAyuda, componerHorarioCSV
import sys
import getopt

#
# Clase utilizada para parsing del XML exportado por PyMuPDF.
#
class OfertasDace( OfertasGeneral ):
    def __init__(self):
        # Se omite pasar la lista de materias requeridas dado que en el
        # documento se conoce cuales son las de carrera por su código
        OfertasGeneral.__init__(self,None)
        # Acumuladores.
        self.listaHorarios = []
        self.listaBloque = []
        self.listaMaterias = []
        self.listaEspeciales = []
        # Patrones para las expresiones regulares
        self.patronMateria = "([A-Z]{2}\d\d\d\d|[A-Z]{3}\d\d\d)"
        self.patronDias = "^" + self.patronDias + "$"
        self.patronEspeciales = "^Especial(es)?$"
        # Modo de operación detectado en la cabeceras
        self.existeEspeciales = False
        self.posEspeciales = None
        self.cabeceraTest = []
        self.paddReconHorario = 5

    # Función: endElement
    # Argumentos:
    #   tag:        String, nombre de la etiqueta proveniente del documento XML.
    #   atributes:  String, atributos de la etiqueta XML.
    # Salida: Ninguna
    #
    # Descripción: ejecutar una acción por cada etiqueta inicial
    def startElement(self, tag, attributes):
        # Se acumulan las caracteres a través del atributo.
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


    # Función: endElement
    # Argumentos:
    #   tag: String, nombre etiqueta proveniente del documento XML.
    # Salida: Ninguna
    #
    # Descripción: ejecutar una acción por cada etiqueta final
    def endElement(self, tag):
        # Se procesa el texto acumulado en self.celda.
        # Se omite las lineas separadoras del documento.
        if tag == "span" and self.celda[0] != '-':
            self.filtroCabecera(self.celda.strip(), self.posCaracteres)
            self.filtrarTexto(self.celda.strip(),self.posCaracteres)
            self.celda = ""
            self.posCaracteres = []

    # Función: filtroCabecera
    # Argumentos:
    #   txt: String
    #   posCaracterres: una tupla (String,String,String,String)
    # Salida: Ninguna
    #
    # Descripción: procesa la cabecera de los dias de semana en la página y
    # guarda sus posiciones. Se imprime los dias reconocidos.
    # Por otra parte, si existe y se reconoce el campo "Especial", se imprime en la salida estandar.
    # Se activa el reconocimiento de este campo.
    def filtroCabecera(self,txt, posCaracteres):
        searchDias = re.search(self.patronDias, txt, re.I)
        searchEspeciales = re.search(self.patronEspeciales, txt.strip(), re.I)

        if searchDias and (not self.cabeceraLista):
            # Se guarda las primeras dos letras del dia y su posición en el documento
            # Esto es a fin de acoplar cada horario a cada fila de asignatura.
            self.cabeceraDias.append((searchDias.group()[0:2],
                                      Decimal(posCaracteres[0]) - self.paddReconHorario,
                                      Decimal(posCaracteres[2]) + self.paddReconHorario))
            self.cabeceraTest.append(searchDias.group())
            self.cabeceraLista = len(self.cabeceraDias) == 5
            if self.cabeceraLista:
                print("Reconocimiento: ")
                print("\tCabecera: ", self.cabeceraTest)

        if searchEspeciales and (not self.existeEspeciales):
            # Activar el modo de reconocimiento de campo Especial
            self.existeEspeciales = True
            self.posEspeciales = (Decimal(posCaracteres[0]) - self.paddReconHorario,
                                      Decimal(posCaracteres[2]) + self.paddReconHorario)
            print("\tExiste especiales: ", self.existeEspeciales)

        return

    # Función: filtrarTexto
    # Argumentos:
    #   txt: String
    #   posCaracterres: una tupla (String,String,String,String)
    # Salida: Ninguna
    #
    # Descripción: procesa cadenas de código de materias, bloque y horarios
    # de acuerdo al estilo de la lista general de DACE.
    def filtrarTexto(self,txt, posCaracteres):
        searchMat = re.search(self.patronMateria, txt, re.I)
        if searchMat:
            self.listaMaterias.append((searchMat.group(),
                       Decimal(posCaracteres[1]),Decimal(posCaracteres[3])))
        elif self.existeEspeciales and re.search("^[A-Z]$",txt, re.I) \
            and self.posEspeciales[0] <= Decimal(posCaracteres[0]) \
            and self.posEspeciales[1] >= Decimal(posCaracteres[2]):
            self.listaEspeciales.append((txt,Decimal(posCaracteres[1]),
                                        Decimal(posCaracteres[3])))

        elif re.search(self.patronBloque1, txt, re.I):
            self.listaBloque.append((txt,Decimal(posCaracteres[1]),
                                     Decimal(posCaracteres[3])))

        elif self.cabeceraLista and re.search(self.patronHoras, txt):
            # Usar las posiciones previas de los dias en la cabecera para asignar
            # los horarios. Se compara contra las posiciones de los horarios reconocidos.
            # En caso de éxito, se anexa como una tupla: (Dia,Horas). Los dias tienen
            # las primeras dos letras; esto es para organizar los horarios
            # en formato CSV posteriormente.
            for (dia,limInf,limSup) in self.cabeceraDias:
                if limInf <= Decimal(posCaracteres[0]) \
                    and Decimal(posCaracteres[2]) <= limSup:
                    self.listaHorarios.append((txt,dia.upper(),
                        Decimal(posCaracteres[1]),Decimal(posCaracteres[3])))
                    break
        return

    # Función: procesarDACE
    # Argumentos:
    #   codigoCarr: String, código de la carrera a reconocer.
    #   nombreArchivoEntrada: camino hacia el archivo de DACE.
    #   fdSalida: [[String]], lista vacia. Funciona como parametro de entrada-salida
    # Salida:
    #   fdSalida: [[String]], lista de reglones de materias reconocidas en estilo CSV.
    #
    # Descripción: Función principal para procesar la lista general de DACE.
    # En cada página donde exista el código de la carrera, procesar las asignaturas.
def procesarDACE(codigoCarr,nombreArchivoEntrada,fdSalida):
    doc = fitz.open(nombreArchivoEntrada)
    # Crear un lector XML
    parser = xml.sax.make_parser()
    # Desactivar namespaces
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)
    # Variables para auxiliares para asignación de horarios
    distRecon = Decimal(0.3)
    distRecon2 = 3

    # Procesar las páginas del PDF. Se examina por
    # codigo de carrera cada página. Al encontrar ,se extrae el texto del
    # documento en archivo XML; luego se corre el parser XML.
    for num in range(doc.pageCount):
        page = doc.loadPage(num)
        if page.searchFor(codigoCarr):
            print("pag.", num + 1)
            try:
                # Archivo temporal.
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
                tuplas.append(([mat,bloq],btechoAlto,btechoBajo))

            # Acoplar los horarios junto a las materias y los bloques.
            for (fila,ftechoAlto,ftechoBajo) in tuplas:
                listaHoras = []
                listaHorasBorrar = []
                for (horas,dia,htechoAlto, htechoBajo) in contenedor.listaHorarios:
                    if  (htechoBajo + distRecon) >= ftechoBajo \
                        and ftechoAlto >= (htechoAlto - distRecon):
                        listaHoras.append((horas,dia))
                        listaHorasBorrar.append((horas,dia,htechoAlto, htechoBajo))

                # Eliminar horarios agregados
                for i in listaHorasBorrar:
                    contenedor.listaHorarios.remove(i)

                # Si existe el campo 'Especial', se asigna mediante el mismo
                # mecanismo de los horarios.
                esp = ''
                for (espe,alto,bajo) in contenedor.listaEspeciales:
                    if (bajo + distRecon2) >= ftechoBajo \
                        and ftechoAlto >= (alto - distRecon2):
                        esp = espe
                        break

                # Procesar los horarios en formato CSV
                # Si una asignatura tiene horarios.
                if listaHoras:
                    fila += componerHorarioCSV(listaHoras)[1:].split(',') + [esp]

                else:
                    fila += ['','','','','', esp]

                fdSalida.append(fila)

    f.close()
    remove('textPDFXML.xml')


if ( __name__ == "__main__"):
    # Asignar los argumentos de la linea de comando.
    (nomArchivoSalida, nomArchivoMaterias, args) = obtArgs(sys.argv[1:])

    fdSalida = []
    procesarDACE("0800",args[0],fdSalida)

    if isfile(nomArchivoSalida):
        remove(nomArchivoSalida)

    # Si se usa '-f'
    if nomArchivoSalida:
        try:
            f = open(nomArchivoSalida, 'a')
            f.write("COD_ASIGNATURA,BLOQUE,L,M,MI,J,V,ESPECIALES\n")
        except IsADirectoryError:
            print(nomArchivoSalida ,"es un directorio. Eliga un nombre distinto")
            nomArchivoSalida = raw_input("Introduzca el nombre del archivo de salida: ")
        except OSError as ose:
            print("Error de E/S: ", ose)
    else:
        print("COD_ASIGNATURA,BLOQUE,L,M,MI,J,V,ESPECIALES")

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
