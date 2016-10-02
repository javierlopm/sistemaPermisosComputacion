from mmap import mmap,ACCESS_READ
from xlrd import open_workbook,cellname
from os.path import isfile
from os import remove
import re

def analizarCabecera(cabecera):
    nroCampo = 0
    posCamposValidos = []
    existeCarrera = False
    campoCarrera = -1
    patronDias = "(L[Uu][Nn](\.?|es)?|M[Aa][Rr](\.?|tes)?|" + \
        "M[Ii][Ee](\.?|rcoles)?|[Jj][Uu][Ee](\.?|ves)?|V[Ii][Ee](\.?|es)?)"
    patronBloque = "[Bb][Ll][Oo][Qq](\.|[Uu][Ee])?"

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

def filtrarMateria(txt):
    #print("TXT", txt)
    return len(txt) == 6 and txt[0].isalpha() and txt[1].isalpha() \
            and txt[2].isdigit()

<<<<<<< HEAD
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
            # Comprueba si pertenece al pensum de computación
            if activarFitrado:
                if (existeCarrera and \
                        (not re.search("0800",str(entrada[campoCarrera])))):
                    #print("Ignorar codCarrera", re.search("0800",str(entrada[campoCarrera])))
                    continue
                elif (not entrada[posCamposValidos[0]] in listaMaterias):
                    #print("Ignorar Materia", entrada[posCamposValidos[0]], re.search("0800",str(entrada[campoCarrera])), existeCarrera)
                    continue

            nuevaEntrada = ""
            for pos in posCamposValidos:
                # Para verificar semántica de archivo del dpto ID
                if verificarCerrar(entrada[pos]):
                    nuevaEntrada = ""
                    #print(entrada)
                    break
                if entrada[pos] == '-':
                    entrada[pos] = ''

                if re.search("^(\w\w-?\d\d\d\d|\w\w\w-?\d\d\d)$", entrada[pos]) \
                    or filtrarBloque(entrada[pos]) \
                    or re.search("^\d{1,2}(-\d{1,2})?$",entrada[pos]) \
                    or entrada[pos] == '':
                    nuevaEntrada += ',' + entrada[pos]

            nuevaEntrada = nuevaEntrada[1:]
            if nuevaEntrada and nuevaEntrada[0] != ',' :
                #fdSalida.write(nuevaEntrada + "\n") # Salida para archivo
                #print(nuevaEntrada)
                fdSalida.append(nuevaEntrada.split(','))



if ( __name__ == "__main__"):
    bookCE = open_workbook('OfertaCE.xls')
    bookID = open_workbook('OfertaID.xlsx')
    bookMAT = open_workbook('OfertaMatematicas.xls')
    sheet0 = bookID.sheet_by_index(0)
    # Concatenar en un solo string e imprimir filas y
    # escribir filas en un archivo estilo csv.
    # if isfile('OfertaXLS.csv'):
    #     remove('OfertaXLS.csv')

    #f = open('OfertaXLS.csv', 'a')
    #f.write("COD_ASIGNATURA,BLOQUE,LUNES,MARTES,MIERCOLES,JUEVES,VIERNES\n")
    cabeceraProcesada = False
    for nroFila in range(sheet0.nrows):
        if not cabeceraProcesada:
            (cabeceraProcesada, \
             posCamposValidos, \
             existeCarrera, \
             campoCarrera) = analizarCabecera(sheet0.row_values(nroFila))
            #print(sheet0.row_values(nroFila), cabeceraProcesada, "\n\n")
        else:
            #print("Listo para procesar entradas")
            entrada = sheet0.row_values(nroFila)
            #print("Nueva linea", entrada)
            # Comprueba si pertenece al pensum de computación
            if (existeCarrera and \
                    (not re.search("0800",str(entrada[campoCarrera])))):
                #print("Ignorar codCarrera", re.search("0800",str(entrada[campoCarrera])))
                continue
            # elif (not entrada[posCamposValidos[0]] in listaMaterias):
            #     #print("Ignorar Materia", entrada[posCamposValidos[0]], re.search("0800",str(entrada[campoCarrera])), existeCarrera)
            #     continue

            nuevaEntrada = ""
            for pos in posCamposValidos:
                # Para verificar semantica de archivo de ID
                if verificarCerrar(entrada[pos]):
                    nuevaEntrada = ""
                    #print("Tienen cerrar", ','.join(entrada))
                    break

                if entrada[pos] == '-':
                    entrada[pos] = ''

                if filtrarMateria(entrada[pos]) \
                    or filtrarBloque(entrada[pos]) \
                    or re.search("^\d{1,2}(-\d{1,2})?$",entrada[pos]) \
                    or entrada[pos] == '':
                    nuevaEntrada += ',' + entrada[pos]

            nuevaEntrada = nuevaEntrada[1:]
            if nuevaEntrada and nuevaEntrada[0] != ',' :
                print("Nueva entrada", nuevaEntrada) # Para debugging
                #f.write(','.join(entrada) + "\n")
    # f.close()