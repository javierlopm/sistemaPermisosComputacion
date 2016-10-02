from procesadorXLS import procesarXLS
from procesadorDOC2CSV import procesarDOC
from procesadorPDF2CSV import procesarPDF
import sys
import getopt
from os.path import splitext, isfile, join
from os import remove, listdir

# Función auxiliar para verificar resultados por pantalla
def imprimirResultados(mensaje,listaOfertas):
    print(mensaje + ": ")
    for fila in listaOfertas:
        print(fila)
    print('\n')

def usoAyuda():
    print("""Uso: prog -f nombre_archivo_salida -d nombre_archivo_dace
                    -m archivo_materias_requeridas [--dir-input=nomDir ]
                    archivo1.pdf archivo2.xls ... archivoN
    prog [-h, --help] """)

def obtArgs():
    nomArchivoDace = ""
    nomArchivoSalida = ""
    nomArchivoMaterias = ""
    nomDirectorio = ""
    opcionDir = False
    try:
        opts, args = getopt.getopt(sys.argv[1:], "d:f:m:h", ["help","dir-input="])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err) # will print something like "option -a not recognized"
        usoAyuda()
        sys.exit(2)

    if  len(opts) == 2 or (len(opts) == 1 and (not opts[0][0] in ["-h", "--help"])):
        assert False, "Número incorrecto de parámetros"
        usoAyuda()


    for o, a in opts:
        if o == "-f":
            nomArchivoSalida = a
        elif o == "-d":
            nomArchivoDace = a
        elif o == "-m":
            nomArchivoMaterias = a
        elif o == "--dir-input":
            nomDirectorio = a
            opcionDir = True
        elif o in ("-h", "--help"):
            usoAyuda()
            sys.exit()
        else:
            assert False, "unhandled option"

# python procesadorOfertas.py -f OfertasProcesadas.csv -d 0800.xls -m materiasRequeridas.txt OfertaPB.xml OfertaSIG.pdf OfertaID.xlsx OfertaCE.xls OfertaMatematicas.xls ofertaComputo.xml
# python procesadorOfertas.py -f OfertasProcesadas.csv -d 0800.xls -m materiasRequeridas.txt --dir-input=archivos_de_prueba/
    if opcionDir:
        return (nomArchivoSalida, nomArchivoMaterias, \
                nomArchivoDace, opcionDir, listdir(nomDirectorio), nomDirectorio)
    else:
        args.append(nomArchivoDace)
        return (nomArchivoSalida, nomArchivoMaterias, \
                nomArchivoDace, opcionDir, args , "")


if __name__ == '__main__':
    (nomArchivoSalida, nomArchivoMaterias, \
     nomArchivoDace, opcionDir, args, nomDirectorio) = obtArgs()

    # Obtener las materias requeridas
    listaMaterias = []
    for materia in open(nomArchivoMaterias, 'r'):
        if (not materia.isspace()) and materia[0] != '#':
            listaMaterias.append(materia.rstrip(' \t\n\r'))

    # Borrar el contenido del archivo de salida si existe
    if isfile(nomArchivoSalida):
        remove(nomArchivoSalida)

    listaOfertas = []
    listaDACE = []
    # Lista necesaria para evitar eliminar materias especiales que no se
    # incluyen en la ofertas
    iniMatEspeciales = ["CI","CC", "EP", "CS"]
<<<<<<< HEAD
    # Deshabilita el filtrado en el procesador XLS.
    # Sólo es neceario para el archivo DACE
    activarListado = True

    for archivo in args:
        # Selección de archivos para procesar. Se extrae su extensión para
        # elegir el procesador adecuado
        ext = splitext(archivo)[1]

        # Constuir el camino para procesar los archivos.
        if opcionDir:
            camino = join(nomDirectorio,archivo)

        if  nomArchivoDace == archivo:
            #Excepcion para cuando no se encuentre 0800
            if  ext == ".xml":
                procesarDOC(camino,listaMaterias ,listaDACE)
            elif ext == ".pdf":
                procesarPDF(camino,listaDACE)
            elif ext == ".xls" or ext == ".xlsx":
                procesarXLS(camino, activarListado, listaMaterias, listaDACE)
            continue

        if  ext == ".xml":
            procesarDOC(camino,listaMaterias ,listaOfertas)
        elif ext == ".pdf":
            procesarPDF(camino,listaOfertas)
        elif ext == ".xls" or ext == ".xlsx":
            procesarXLS(camino, activarListado, listaMaterias, listaOfertas)

    print("\nOfertas cargadas con éxito")

<<<<<<< HEAD
    imprimirResultados("ListaDace",listaDACE)
    imprimirResultados("ListaOfertas",listaOfertas)

    materiasDacePorBorrar = []
    procesado = []
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