from procesadorXLS import procesarXLS
from procesadorDOC2CSV import procesarDOC
from procesadorPDF2CSV import procesarPDF
import sys
from os.path import splitext, isfile
from os import remove

def imprimirResultados(mensaje,listaOfertas):
    print(mensaje + ": ")
    for fila in listaOfertas:
        print(fila)
    print('\n')


if __name__ == '__main__':
    # if isfile('ListaDACE.csv'):
    #     remove('ListaDACE.csv')
    nomArchivoDace = sys.argv[-2]
    nomArchivoSalida = sys.argv[-1]
    nomArchivoMaterias = sys.argv[1]

    # Obtener las materias requeridas
    listaMaterias = []
    for materia in open(nomArchivoMaterias, 'r'):
        listaMaterias.append(materia.rstrip(' \t\n\r'))
    print(listaMaterias)

    if isfile(nomArchivoSalida):
        remove(nomArchivoSalida)

    listaOfertas = []
    procesado = []
    listaDACE = []

    for archivo in sys.argv[1:]:
        # Selección de archivos para procesar
        ext = splitext(archivo)[1]
        if nomArchivoDace == archivo:
            temp = listaOfertas
            listaOfertas = listaDACE

        if  ext == ".xml":
            procesarDOC(archivo,listaMaterias ,listaOfertas)
        elif ext == ".pdf":
            procesarPDF(archivo, listaOfertas)
        elif ext == ".xls" or ext == ".xlsx":
            procesarXLS(archivo, listaOfertas)

    listaOfertas = temp
    print("\nOfertas cargadas con éxito")

    materiasDacePorBorrar = []
    filaEncontrada = False
    # Realizar comparación entre listas del dpto y las listas de DACE

    for filaDace in listaDACE:
        for filaOfertas in listaOfertas:
            # Comprobar materia y bloque, salvo las materias CI
            if filaOfertas[0] == filaDace[0] \
                and filaOfertas[1] == filaDace[1] \
                and (not (filaDace[0][0] == 'C' \
                        and filaDace[0][1] == 'I')):
                filaEncontrada = True
                break
        # Caso 2:
        if not filaEncontrada:
            materiasDacePorBorrar.append(filaDace)
            procesado.append(filaDace + ['-','0800','E'])
            filaEncontrada = False

    # Descartar las materias de la lista de DACE
    # que no se encuentren en la oferta de dptos
    for filaPorBorrar in materiasDacePorBorrar:
        listaDACE.remove(filaPorBorrar)

    filaEncontrada = None
    materiasCompIncorporadas = False
    for filaOfertas in listaOfertas:
        for filaDace in listaDACE:
            # Incorporar las materias de computación
            if (not materiasCompIncorporadas) and filaDace[0][0] == 'C' \
                and filaDace[0][1] == 'I':
                procesado.append(filaDace + ['-','0800','-'])

            if filaOfertas[0] == filaDace[0] \
                and filaOfertas[1] == filaDace[1]:

                filaEncontrada = filaDace
                break
        # Caso 1:
        if filaEncontrada:
            for (itemOferta,itemDace) in zip(filaOfertas,filaDace):
                match = itemOferta == itemDace
                if match:
                    continue
                else:
                    break
            if match:
                procesado.append(filaOfertas + ['-','0800','-'])
            else:
                procesado.append(filaOfertas + ['-','0800','M'])
        else:
        # Caso 3:
            procesado.append(filaOfertas + ['-','0800','I'])

        materiasCompIncorporadas = True
        filaEncontrada = None

    # Imprimir resultados al archivo de salida
    fdSalida = open(nomArchivoSalida, 'a')
    fdSalida.write("COD_ASIGNATURA,BLOQUE,LUNES,MARTES" + \
                        ",MIERCOLES,JUEVES,VIERNES\n")
    for fila in procesado:
        fdSalida.write(','.join(fila) + '\n')

    fdSalida.close()

    print("Ofertas procesadas exitosamente")

    # imprimirResultados("FilaOfertas", fdSalida)
    # imprimirResultados("FilaDace", fdDace)
    #imprimirResultados("Materias que existen", procesado)
    #fdDace.close()

# materiasRequeridas.txt OfertaMatematicas.xls OfertaComputo.xml OfertaID.xlsx OfertaCE.xls OfertaSIG.pdf 0800DACE.xls OfertaProcesadas.csv

