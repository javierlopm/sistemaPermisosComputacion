#!/usr/bin/python3
# Nombre: Daniel Leones
# Carné: 09-10977
# Fecha: 7/12/2016
# Descripción: procesa los archivos xls y xlsx usando la libreria xlrd. Se analiza
# la cabecera de los archivos en búsqueda del patrón:
# COD_ASIGNATURA,BLOQUE,LUNES,MARTES,MIERCOLES,JUEVES,VIERNES, ESPECIAL.
# En caso de existir el campo Especial y/o Carrera, se notificará en la salida
# estandar.
# Si existe el campo carrera, se superpone al reconocimiento por lista de materias.
# Si se detecta alguna palabra Cerrar, se omite la fila en la lista final.
# 

from xlrd import open_workbook,cellname
from os.path import isfile
from os import remove
from math import floor
from funcionesAuxiliares import obtArgs, cargarMaterias, \
                                normalizarMateria, usoAyuda, dividirStr
import sys
import re

# Patrones usados por las expresiones regulares
patronMateria = "(\w\w\s*-?\s*\d\d\d\d|\w\w\w\s*-?\s*\d\d\d)"
patronDias = "^(L[Uu][Nn](\.?|es)?|M[Aa][Rr](\.?|tes)?|" + \
    "M[Ii][Ee](\.?|rcoles)?|[Jj][Uu][Ee](\.?|ves)?|V[Ii][Ee](\.?|rnes)?)$"
patronBloque = "[Bb][Ll][Oo][Qq](\.|[Uu][Ee])?"
patronHoras = "^(\d{1,2}((-|..)\d{1,2})?)$"
existeEspecial = False
   
# Función: analizarCabecera
# Argumentos: 
#   cabecera: [String], fila de una hoja de cálculo.
# Salida:
#   (Booleano,[Int], Booleano, Int, Booleano, Int, Booleano, Int),
#       Posiciones y modos de operación detectados.
# 
# Descripción: Leer la cabecera usando expresiones regulares para reconocer el estilo 
# formato de la información y activar los modos de operación necesarios. 
def analizarCabecera(cabecera):
    nroCampo = 0
    posCamposValidos = []
    existeCarrera = False
    campoCarrera = -1
    campoAccion = -1
    existeAccion = False
    campoEspecial = -1
    global existeEspecial
    testposCamposValidos = []

    for celda in cabecera:
        if celda:
            celda = celda.strip()
            searchCodMateria = re.search("^C[oó]d(_Asignatura|igo" +
                                         "(\sAsignatura)?|.)$", celda, re.I)
            searchHorario = re.search(patronDias, celda, re.I)
            searchBloque = re.search(patronBloque,celda, re.I)
            searchCarrera = re.search("^Carreras?$",celda, re.I)
            searchAccion = re.search("Acci[oó]n(es)?",celda, re.I)
            searchEspecial = re.search("^(Oferta(_|\s))?Especial$", celda, re.I)
            if searchCodMateria or searchHorario or searchBloque:
                #print(searchCodMateria)
                #testposCamposValidos.append((nroCampo,celda)) #para debugging
                testposCamposValidos.append(celda) #para debugging
                posCamposValidos.append(nroCampo)

            if searchCarrera:
                existeCarrera = True
                campoCarrera = nroCampo
                testposCamposValidos.append(celda)

            if searchAccion:
                campoAccion = nroCampo
                existeAccion = True
                testposCamposValidos.append(celda)
            if searchEspecial:
                existeEspecial = True
                campoEspecial = nroCampo
                testposCamposValidos.append(celda)
        nroCampo += 1

    if len(posCamposValidos) == 7:
        print("Reconocimiento")
        print("\tCabecera: ", testposCamposValidos)
        print("\tCampo de carrera:", existeCarrera)
        print("\tCampo de acción: ", existeAccion)
        print("\tCampo de especial: ", existeEspecial)
        return (True,posCamposValidos, existeCarrera, campoCarrera,
                existeAccion, campoAccion,existeEspecial, campoEspecial)
    else:
        return (False,posCamposValidos, existeCarrera, campoCarrera,
                existeAccion, campoAccion, existeEspecial, campoEspecial)

# Función: filtrarBloque
# Argumentos: 
#   txt: [String]
# Salida:
#   Booleano
# 
# Descripción: Reconocer bloque. Se regresa True, en caso de encontrar un bloque
def filtrarBloque(txt):
    return len(txt) == 1 and txt[0].isalpha()

# Función: verificarCerrar
# Argumentos: 
#   txt: [String]
# Salida:
#   Booleano
# 
# Descripción: Reconocer la palabra clave cerrar. Esto activa la omisión de la fila
# que se esté procesando.
def verificarCerrar(txt):
    return re.search("cerrar", txt, re.I)

# Función: normalizarHoras
# Argumentos: 
#   txt: [String]
# Salida:
#   String, 
# 
# Descripción: toma las horas previamente reconocidas y las convierte en el siguiente
# formato: Hora-Hora. 
def normalizarHoras(txt):
    nuevo = dividirStr(txt,'.')
    if len(nuevo) > 1:
        temp = nuevo[1]
        nuevo[1] = '-'
        nuevo.append(temp)
    nuevo = "".join(nuevo)
    return nuevo

# Función: procesarXLS
# Argumentos: 
#   nomArchivoEntrante: String, camino hacia el archivo a procesar.
#   activarFiltrado:    Booleano, activar supresión de materias.
#   listaMaterias:      [String], lista de materias
#   fdSalida:           [[String]], lista de ofertas posiblemente vacia.
# Salida:
#   fdSalida: [[String]]
# 
# Descripción: función principal de procesamiento. 
def procesarXLS(nomArchivoEntrante, activarFiltrado, listaMaterias, fdSalida):
    global existeEspecial
    # Abrir el la hoja de cálculo en cuestión
    book = open_workbook(nomArchivoEntrante)
    # Acceder a la primera hoja.
    sheet0 = book.sheet_by_index(0)

    cabeceraProcesada = False
    for nroFila in range(sheet0.nrows):
        if not cabeceraProcesada:
            (cabeceraProcesada, posCamposValidos,
             existeCarrera,campoCarrera,
             existeAccion, campoAccion,
             existeEspecial,
             campoEspecial) = analizarCabecera(sheet0.row_values(nroFila))
        else:
            entrada = sheet0.row_values(nroFila)
            # Comprueba si pertenece al pensum de computación
            if activarFiltrado:
                if (existeCarrera and \
                    (not re.search("0?800",str(entrada[campoCarrera])))):
                    continue

                if (not normalizarMateria(entrada[posCamposValidos[0]]) in listaMaterias):
                    continue
                if existeAccion and verificarCerrar(entrada[campoAccion]):
                    continue

            nuevaEntrada = ""
            horarioNoVacio = True
            for pos in posCamposValidos:
                # Normalizar la entrada
                if isinstance(entrada[pos],float):
                    #Convertir numeros unitarios flotantes en enteros.
                    txt = str(floor(entrada[pos]))
                elif entrada[pos] != '':
                    txt = str(entrada[pos]).strip()
                else:
                    txt = entrada[pos]

                if txt == '-':
                    entrada[pos] = ''
                    txt = ''

                # Para verificar semántica de archivo del dpto ID
                if verificarCerrar(txt):
                    nuevaEntrada = ""
                    break

                # Reconocimiento de códigos de materias
                searchMat = re.search(patronMateria,txt, re.I)
                if searchMat:
                    nuevaEntrada += ',' + normalizarMateria(searchMat.group())
                # Reconocimiento de horas
                elif re.search(patronHoras, txt):
                    nuevaEntrada += ',' + normalizarHoras(txt)
                    horarioNoVacio = False
                # Reconocimiento de bloques
                elif filtrarBloque(txt) \
                    or txt == '':
                    nuevaEntrada += ',' + txt

            # Reconocimiento de campo Especial
            if existeEspecial and re.search("^[A-Z]$",
                          entrada[campoEspecial].strip(), re.I):
                nuevaEntrada += ',' + entrada[campoEspecial].strip()
            elif horarioNoVacio:
                nuevaEntrada += ',Y'
            else:
                nuevaEntrada += ','

            nuevaEntrada = nuevaEntrada[1:]
            if nuevaEntrada and nuevaEntrada[0] != ',' :
                fdSalida.append(nuevaEntrada.split(','))

# Programa principal para ejecutar el procesador individualmente.
if ( __name__ == "__main__"):
    global modoDACE
    # Pasaje de parametros
    (nomArchivoSalida, nomArchivoMaterias, args) = obtArgs(sys.argv[1:])

    # Cargar lista de materias
    listaMaterias = cargarMaterias(nomArchivoMaterias)

    if isfile(nomArchivoSalida):
        remove(nomArchivoSalida)

    fdSalida = []
    procesarXLS(args[0],True,listaMaterias,fdSalida)

    # Si se usa '-f'
    if nomArchivoSalida:
        try:
            f = open(nomArchivoSalida, 'a')
            f.write("COD_ASIGNATURA,BLOQUE,L,M,MI,J,V,ESPECIAL\n")
        except OSError as ose:
            print("Error de E/S: ", ose)
            sys.exit(2)
    else:
        print("\nCOD_ASIGNATURA,BLOQUE,L,M,MI,J,V,ESPECIAL")

    # Escribir los resultados
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
