from mmap import mmap,ACCESS_READ
from xlrd import open_workbook,cellname
from os.path import isfile
from os import remove
import sys
import re
from funcionesAuxiliares import obtArgs, cargarMaterias, \
                                normalizarMateria, usoAyuda


patronMateria = "(\w\w\s*-?\s*\d\d\d\d|\w\w\w\s*-?\s*\d\d\d)"
patronDias = "(L[Uu][Nn](\.?|es)?|M[Aa][Rr](\.?|tes)?|" + \
    "M[Ii][Ee](\.?|rcoles)?|[Jj][Uu][Ee](\.?|ves)?|V[Ii][Ee](\.?|es)?)"
patronBloque = "[Bb][Ll][Oo][Qq](\.|[Uu][Ee])?"
patronHorario = "^(\d{1,2}(-\d{1,2})?)$"

def analizarCabecera(cabecera):
    nroCampo = 0
    posCamposValidos = []
    existeCarrera = False
    campoCarrera = -1

    for celda in cabecera:
        searchCodMateria = re.search("C[oó]d(_Asignatura|igo)", celda, re.I)
        searchHorario = re.search(patronDias, celda, re.I)
        searchBloque = re.search(patronBloque,celda, re.I)
        searchCarrera = re.search("Carreras?",celda, re.I)
        if searchCodMateria or searchHorario or searchBloque:
            #posCamposValidos.append((nroCampo,celda)) #para debugging
            posCamposValidos.append(nroCampo)
        elif searchCarrera:
                existeCarrera = True
                campoCarrera = nroCampo
        nroCampo += 1

    #print("posCamposValidos: ",posCamposValidos, existeCarrera, campoCarrera)
    #print("posCamposInvalidos: ",posCamposInvalidos)
    if len(posCamposValidos) == 7:
        return (True,posCamposValidos, existeCarrera, campoCarrera)
    else:
        return (False,posCamposValidos, existeCarrera, campoCarrera)

def filtrarBloque(txt):
    return len(txt) == 1 and txt[0].isalpha()

def verificarCerrar(txt):
    return re.search("cerrar", txt, re.I)

def procesarXLS(nomArchivoEntrante, activarFitrado, listaMaterias, fdSalida):
    # Abrir el la hoja de cálculo en cuestión
    book = open_workbook(nomArchivoEntrante)
    # Acceder a la primera hoja.
    sheet0 = book.sheet_by_index(0)
    # Concatenar en un solo string e imprimir filas y
    # escribir filas en un archivo estilo csv.
    cabeceraProcesada = False
    for nroFila in range(sheet0.nrows):
        if not cabeceraProcesada:
            (cabeceraProcesada, \
             posCamposValidos, \
             existeCarrera, \
             campoCarrera) = analizarCabecera(sheet0.row_values(nroFila))
        else:
            entrada = sheet0.row_values(nroFila)
            #print(entrada)
            # Comprueba si pertenece al pensum de computación
            if activarFitrado:
                if (existeCarrera and \
                    (not re.search("0800",str(entrada[campoCarrera])))):
                    #print("Eliminar por Carrera", entrada)
                    continue

                if (not normalizarMateria(entrada[posCamposValidos[0]]) in listaMaterias):
                    #print("Ignorar codCarrera", re.search("0800",str(entrada[campoCarrera])))
                    # print("Eliminar por lista materias ",
                    #       normalizarMateria(entrada[posCamposValidos[0]]), entrada, "\n")
                    continue

            nuevaEntrada = ""
            for pos in posCamposValidos:
                if isinstance(entrada[pos],float):
                    txt = str(round(entrada[pos]))
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
                elif filtrarBloque(txt) \
                    or txt == '' or re.search(patronHorario, txt):
                    #print("pasa el filtro", txt)
                    nuevaEntrada += ',' + txt

            nuevaEntrada = nuevaEntrada[1:]
            if nuevaEntrada and nuevaEntrada[0] != ',' :
                #fdSalida.write(nuevaEntrada + "\n") # Salida para archivo
                #print(nuevaEntrada)
                fdSalida.append(nuevaEntrada.split(','))

if ( __name__ == "__main__"):
    (nomArchivoSalida, nomArchivoMaterias, args) = obtArgs(sys.argv[1:])

    listaMaterias = cargarMaterias(nomArchivoMaterias)

    fdSalida = []
    sheet0 = open_workbook(args[0]).sheet_by_index(0)
    # Concatenar en un solo string e imprimir filas y
    # escribir filas en un archivo estilo csv.
    if isfile(nomArchivoSalida):
        remove(nomArchivoSalida)

    if nomArchivoSalida:
        try:
            f = open(nomArchivoSalida, 'a')
            f.write("COD_ASIGNATURA,BLOQUE,L,M,MI,J,V\n")
        except OSError as ose:
            print("Error de E/S: ", ose)
            sys.exit(2)
    else:
        print("COD_ASIGNATURA,BLOQUE,L,M,MI,J,V")

    procesarXLS(args[0],True,listaMaterias,fdSalida)

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