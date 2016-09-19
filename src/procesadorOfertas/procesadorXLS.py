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

def procesarXLS(nomArchivoEntrante,fdSalida):
    book = open_workbook(nomArchivoEntrante)
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
            #print(sheet0.row_values(nroFila), cabeceraProcesada, "\n\n")
        else:
            #print("Listo para procesar entradas")
            entrada = sheet0.row_values(nroFila)
            #print("Nueva linea", entrada)
            if existeCarrera and \
                (not re.search("0800",str(entrada[campoCarrera]))):
                continue

            nuevaEntrada = ""
            for pos in posCamposValidos:
                if entrada[pos] == '':
                    entrada[pos] = '-'

                if re.search("^(\w\w-?\d\d\d\d|\w\w\w-?\d\d\d)$", entrada[pos]) \
                    or filtrarBloque(entrada[pos]) \
                    or re.search("^\d{1,2}(-\d{1,2})?$",entrada[pos]) \
                    or entrada[pos] == '-':
                    nuevaEntrada += ',' + entrada[pos]

            nuevaEntrada = nuevaEntrada[1:]
            if nuevaEntrada and nuevaEntrada[0] != '-' :
                #fdSalida.write(nuevaEntrada + "\n") # Salida para archivo
                fdSalida.append(nuevaEntrada.split(','))


if ( __name__ == "__main__"):
    bookCE = open_workbook('OfertaCE.xls')
    bookID = open_workbook('OfertaID.xlsx')
    bookMAT = open_workbook('OfertaMatematicas.xls')
    sheet0 = bookMAT.sheet_by_index(0)
    # Concatenar en un solo string e imprimir filas y
    # escribir filas en un archivo estilo csv.
    if isfile('OfertaXLS.csv'):
        remove('OfertaXLS.csv')

    # print("bookID")
    # analizarCabecera(bookID.sheet_by_index(0).row_values(0))
    #print("bookCE")
    #analizarCabecera(bookCE.sheet_by_index(0).row_values(3))
    # print("bookMAT")
    # analizarCabecera(bookMAT.sheet_by_index(0).row_values(4))

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
            if existeCarrera and \
                (not re.search("0800",str(entrada[campoCarrera]))):
                continue

            nuevaEntrada = ""
            for pos in posCamposValidos:
                if entrada[pos] == '':
                    entrada[pos] = '-'

                if filtrarMateria(entrada[pos]) \
                    or filtrarBloque(entrada[pos]) \
                    or re.search("^\d{1,2}(-\d{1,2})?$",entrada[pos]) \
                    or entrada[pos] == '-':
                    nuevaEntrada += ',' + entrada[pos]

            nuevaEntrada = nuevaEntrada[1:]
            if nuevaEntrada and nuevaEntrada[0] != '-' :
                print("Nueva entrada", nuevaEntrada) # Para debugging
                #f.write(','.join(entrada) + "\n")
    # f.close()