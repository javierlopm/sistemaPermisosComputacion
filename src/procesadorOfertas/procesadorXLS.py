from mmap import mmap,ACCESS_READ
from xlrd import open_workbook,cellname
from os.path import isfile
from os import remove
from math import floor
from funcionesAuxiliares import obtArgs, cargarMaterias, \
                                normalizarMateria, usoAyuda, dividirStr
import sys
import re


patronMateria = "(\w\w\s*-?\s*\d\d\d\d|\w\w\w\s*-?\s*\d\d\d)"
patronDias = "^(L[Uu][Nn](\.?|es)?|M[Aa][Rr](\.?|tes)?|" + \
    "M[Ii][Ee](\.?|rcoles)?|[Jj][Uu][Ee](\.?|ves)?|V[Ii][Ee](\.?|rnes)?)$"
patronBloque = "[Bb][Ll][Oo][Qq](\.|[Uu][Ee])?"
patronHoras = "^(\d{1,2}((-|..)\d{1,2})?)$"
existeEspecial = False

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

def filtrarBloque(txt):
    return len(txt) == 1 and txt[0].isalpha()

def verificarCerrar(txt):
    return re.search("cerrar", txt, re.I)

def normalizarHoras(txt):
    #print("entrada", txt)
    nuevo = dividirStr(txt,'.')
    if len(nuevo) > 1:
        temp = nuevo[1]
        nuevo[1] = '-'
        nuevo.append(temp)
    nuevo = "".join(nuevo)
    #print("salida", nuevo)
    return nuevo

def procesarXLS(nomArchivoEntrante, activarFiltrado, listaMaterias, fdSalida):
    global existeEspecial
    # Abrir el la hoja de cálculo en cuestión
    book = open_workbook(nomArchivoEntrante)
    # Acceder a la primera hoja.
    sheet0 = book.sheet_by_index(0)
    # Concatenar en un solo string e imprimir filas y
    # escribir filas en un archivo estilo csv.
    cabeceraProcesada = False
    for nroFila in range(sheet0.nrows):
        if not cabeceraProcesada:
            #print(sheet0.row_values(nroFila))
            (cabeceraProcesada, posCamposValidos,
             existeCarrera,campoCarrera,
             existeAccion, campoAccion,
             existeEspecial,
             campoEspecial) = analizarCabecera(sheet0.row_values(nroFila))
        else:
            entrada = sheet0.row_values(nroFila)
            #print(entrada)
            # Comprueba si pertenece al pensum de computación
            if activarFiltrado:
                if (existeCarrera and \
                    (not re.search("0?800",str(entrada[campoCarrera])))):
                    #print("Eliminar por Carrera",str(entrada[campoCarrera]))
                    continue

                if (not normalizarMateria(entrada[posCamposValidos[0]]) in listaMaterias):
                    #print("Ignorar codCarrera", re.search("0800",str(entrada[campoCarrera])))
                     #print("Eliminar por lista materias ",
                    #       normalizarMateria(entrada[posCamposValidos[0]]), entrada, "\n")
                    continue
                if existeAccion and verificarCerrar(entrada[campoAccion]):
                    # print("Eliminada por cerrar", entrada[posCamposValidos[0]],
                    #       entrada[posCamposValidos[1]])
                    continue

            nuevaEntrada = ""
            for pos in posCamposValidos:
                if isinstance(entrada[pos],float):
                    #Compvertir numeros unitarios flotantes en enteros.
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
                    #print("Tienen cerrar", ','.join(entrada))
                    break

                searchMat = re.search(patronMateria,txt, re.I)
                if searchMat:
                    nuevaEntrada += ',' + normalizarMateria(searchMat.group())
                elif re.search(patronHoras, txt):
                    nuevaEntrada += ',' + normalizarHoras(txt)
                elif filtrarBloque(txt) \
                    or txt == '':
                    #print("pasa el filtro", txt)
                    nuevaEntrada += ',' + txt

            if existeEspecial and re.search("^[A-Z]$",
                          entrada[campoEspecial].strip(), re.I):
                nuevaEntrada += ',' + entrada[campoEspecial].strip()

            nuevaEntrada = nuevaEntrada[1:]
            if nuevaEntrada and nuevaEntrada[0] != ',' :
                #fdSalida.write(nuevaEntrada + "\n") # Salida para archivo
                #print(nuevaEntrada)
                fdSalida.append(nuevaEntrada.split(','))

if ( __name__ == "__main__"):
    global modoDACE
    (nomArchivoSalida, nomArchivoMaterias, args) = obtArgs(sys.argv[1:])

    listaMaterias = cargarMaterias(nomArchivoMaterias)

    fdSalida = []
    sheet0 = open_workbook(args[0]).sheet_by_index(0)
    # Concatenar en un solo string e imprimir filas y
    # escribir filas en un archivo estilo csv.
    if isfile(nomArchivoSalida):
        remove(nomArchivoSalida)

    procesarXLS(args[0],True,listaMaterias,fdSalida)

    if nomArchivoSalida:
        try:
            f = open(nomArchivoSalida, 'a')
            f.write("COD_ASIGNATURA,BLOQUE,L,M,MI,J,V\n")
        except OSError as ose:
            print("Error de E/S: ", ose)
            sys.exit(2)
    elif existeEspecial:
        print("\nCOD_ASIGNATURA,BLOQUE,L,M,MI,J,V,ESPECIAL")
    else:
        print("\nCOD_ASIGNATURA,BLOQUE,L,M,MI,J,V")


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
