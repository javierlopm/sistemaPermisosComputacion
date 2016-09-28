from procesadorXLS import procesarXLS
from procesadorDOC2CSV import procesarDOC
from procesadorPDF2CSV import procesarPDF
import sys
from os.path import splitext, isfile
from os import remove

# Función auxiliar para verificar resultados por pantalla
def imprimirResultados(mensaje,listaOfertas):
    print(mensaje + ": ")
    for fila in listaOfertas:
        print(fila)
    print('\n')

def obtArgs():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "ho:v", ["help", "output="])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    output = None
    verbose = False
    for o, a in opts:
        if o == "-v":
            verbose = True
        elif o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-o", "--output"):
            output = a
        else:
            assert False, "unhandled option"



if __name__ == '__main__':
    nomArchivoDace = sys.argv[-2]
    nomArchivoSalida = sys.argv[-1]
    nomArchivoMaterias = sys.argv[1]

    # Obtener las materias requeridas
    listaMaterias = []
    for materia in open(nomArchivoMaterias, 'r'):
        if (not materia.isspace()) and materia[0] != '#':
            listaMaterias.append(materia.rstrip(' \t\n\r'))

    # Borrar el contenido del archivo de salida si existe
    if isfile(nomArchivoSalida):
        remove(nomArchivoSalida)

    listaOfertas = []
    procesado = []
    listaDACE = []
    # Lista necesaria para evitar eliminar materias especiales que no se
    # incluyen en la ofertas
    iniMatEspeciales = ["CI","CC", "EP", "CS"]
    # Deshabilita el filtrado en el procesador XLS.
    # Sólo es neceario para el archivo DACE
    activarListado = True

    for archivo in sys.argv[1:]:
        # Selección de archivos para procesar
        ext = splitext(archivo)[1]
        if nomArchivoDace == archivo:
            temp = listaOfertas
            listaOfertas = listaDACE
            activarListado = False

        if  ext == ".xml":
            procesarDOC(archivo,listaMaterias ,listaOfertas)
        elif ext == ".pdf":
            procesarPDF(archivo,listaOfertas)
        elif ext == ".xls" or ext == ".xlsx":
            procesarXLS(archivo, activarListado, listaMaterias, listaOfertas)

    listaOfertas = temp
    print("\nOfertas cargadas con éxito")

    # imprimirResultados("ListaDace",listaDACE)
    # imprimirResultados("ListaOfertas",listaOfertas)

    materiasDacePorBorrar = []
    filaEncontrada = False
    # Realizar comparación entre listas del dpto y las listas de DACE
    for filaDace in listaDACE:
        for filaOfertas in listaOfertas:
            # Comprobar materia y bloque, salvo las materias CI
            if filaOfertas[0] == filaDace[0] \
                and filaOfertas[1] == filaDace[1] \
                and (not filaDace[0][0:2] in iniMatEspeciales):
                filaEncontrada = True
                break
        # Caso 2:
        if not (filaEncontrada):
            if (not (filaDace[0][0:2] in iniMatEspeciales)):
                materiasDacePorBorrar.append(filaDace)
                procesado.append(filaDace + ['','0800','E'])
            else:
                procesado.append(filaDace + ['','0800',''])

        filaEncontrada = False

    # Descartar las materias de la lista de DACE
    # que no se encuentren en la oferta de dptos
    for filaPorBorrar in materiasDacePorBorrar:
        listaDACE.remove(filaPorBorrar)

    # imprimirResultados("ListaDace E",listaDACE)
    # imprimirResultados("ListaOfertas E",listaOfertas)

    filaEncontrada = None
    materiasCompIncorporadas = False
    for filaOfertas in listaOfertas:
        for filaDace in listaDACE:
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
                procesado.append(filaOfertas + ['','0800',''])
            else:
                procesado.append(filaOfertas + ['','0800','M'])
        else:
        # Caso 3:
            procesado.append(filaOfertas + ['','0800','I'])

        materiasCompIncorporadas = True
        filaEncontrada = None

    # Imprimir resultados al archivo de salida
    fdSalida = open(nomArchivoSalida, 'a')
    fdSalida.write("COD_ASIGNATURA,BLOQUE,LUNES,MARTES" + \
                    ",MIERCOLES,JUEVES,VIERNES,OFERTA,COD_CARRERA,OPERACIÓN\n")
    for fila in procesado:
        fdSalida.write(','.join(fila) + '\n')

    fdSalida.close()

    print("Ofertas procesadas exitosamente")
