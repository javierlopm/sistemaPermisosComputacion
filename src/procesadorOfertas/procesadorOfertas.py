#!/usr/bin/python3.x

# Nombre: Daniel Leones
# Carné: 09-10977
# Fecha: 26/10/2016
# Descripción: Programa principal. Este program realiza las siguientes funciones:
#   - Generar ofertas a partir de documentos de los departamentos y una
#     lista de DACE.
#   - Reanalizar ofertas realizadas con nuevas listas de DACE. Esto se realiza
#     mediante la opción -r.
# En ambos casos, la salida es un archivo en formato CSV

from procesadorXLS import procesarXLS
from procesadorDOC import procesarDOC
from procesadorPDF import procesarPDF
from procesadorDACE import procesarDACE
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

def cargarOfertas(listaArchivos, nomDirectorio, listaMaterias, \
                  opcionDir, nomArchivoDace):
    listaOfertas = []
    listaDACE = []

    for archivo in listaArchivos:
        # Selección de archivos para procesar. Se extrae su extensión para
        # elegir el procesador adecuado
        ext = splitext(archivo)[1]

        # Constuir el camino para procesar los archivos.
        if opcionDir:
            camino = join(nomDirectorio,archivo)
            print("\t", camino)

        if  nomArchivoDace == archivo:
            if  ext == ".fodt" or ext == "xml":
                procesarDOC(camino,listaMaterias ,listaDACE)
            elif ext == ".pdf":
                procesarPDF(camino, listaMaterias, listaDACE)
            elif ext == ".xls" or ext == ".xlsx":
                procesarXLS(camino, False, listaMaterias, listaDACE)
            continue

        if  ext == ".fodt" or ext == "xml":
            procesarDOC(camino,listaMaterias ,listaOfertas)
        elif ext == ".pdf":
            procesarPDF(camino,listaMaterias, listaOfertas)
        elif ext == ".xls" or ext == ".xlsx":
            procesarXLS(camino, True, listaMaterias, listaOfertas)

    return (listaOfertas, listaDACE)

def generarOferta(listaOfertas,listaDACE):
    # Lista necesaria para evitar eliminar materias especiales que no se
    # incluyen en la ofertas
    iniMatEspeciales = ["CI","CC", "EP", "CS"]
    materiasDacePorBorrar = []
    procesado = []
    filaEncontrada = False

    # Realizar comparación entre listas del dpto y las listas de DACE.
    # Se aborda desde el pto de vista de lista de DACE. Se realizan operaciones
    # de E e inclusión de materias que existen sólo en DACE.
    for filaDace in listaDACE:
        for filaOfertas in listaOfertas:
            # Comprobar materia y bloque, salvo las materias especiales
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

    # Realizar comparaciones para I y M. Desde el pto de vista de las ofertas
    filaEncontrada = None
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

        filaEncontrada = None

    return procesado


def reanalizarOferta(listaOfertas,listaDACE):
    materiasDacePorBorrar = []
    procesado = []
    filaEncontrada = False

    # Realizar comparación entre listas del dpto y las listas de DACE.
    # Se aborda desde el pto de vista de lista de DACE. Se realizan operaciones
    # de E e inclusión de materias que existen sólo en DACE.
    for filaDace in listaDACE:
        for filaOfertas in listaOfertas:
            if filaOfertas[0] == filaDace[0] \
                and filaOfertas[1] == filaDace[1]:
                filaEncontrada = True
                break
        # Caso 2:
        if not (filaEncontrada):
            materiasDacePorBorrar.append(filaDace)
            procesado.append(filaDace + ['','0800','E'])

        filaEncontrada = False

    # Descartar las materias de la lista de DACE
    # que no se encuentren en la oferta de dptos
    for filaPorBorrar in materiasDacePorBorrar:
        listaDACE.remove(filaPorBorrar)

    # Realizar comparaciones para I y M. Desde el pto de vista de las ofertas.
    # Se agregan las filas con operación E. Se analizan otras.
    filaEncontrada = None
    for filaOfertas in listaOfertas:
        if filaOfertas[9] != 'E':
            for filaDace in listaDACE:
                if filaOfertas[0] == filaDace[0] \
                    and filaOfertas[1] == filaDace[1]:
                    filaEncontrada = filaDace
                    break
            # Caso 1:
            if filaEncontrada:
                #print("Comparar", filaEncontrada, filaOfertas)
                for (itemOferta,itemDace) in zip(filaOfertas,filaEncontrada):
                    match = itemOferta == itemDace
                    if match:
                        continue
                    else:
                        break
                if match:
                    procesado.append(filaEncontrada + ['','0800',''])
                else:
                    # for (itemOferta,itemDace) in zip(filaOfertas,filaEncontrada):
                    # print((itemOferta,itemDace))
                    procesado.append(filaOfertas)
            else:
            # Caso 3:
                procesado.append(filaOfertas[0:7] + ['','0800','I'])
        else:
            procesado.append(filaOfertas)

        filaEncontrada = None

    return procesado

def usoAyuda():
    print("""Uso: prog -f nombre_archivo_salida -d nombre_archivo_dace
                    -m archivo_materias_requeridas [--dir-input=nomDir ]
                    archivo1.pdf archivo2.xls ... archivoN
    prog [-h, --help] """)

def obtArgs(entrada):
    nomArchivoDace = ""
    nomArchivoSalida = ""
    nomArchivoMaterias = ""
    nomDirectorio = ""
    opcionDir = False
    reanalisis = False
    try:
        opts, args = getopt.getopt(entrada, "d:f:m:hr", ["help","input-dir="])
    except getopt.GetoptError as err:
        print(err)
        usoAyuda()
        sys.exit(2)

    for o, a in opts:
        if o == "-f":
            nomArchivoSalida = a
        elif o == "-r":
            reanalisis = True
        elif o == "-d":
            nomArchivoDace = a
        elif o == "-m":
            nomArchivoMaterias = a
        elif o == "--input-dir":
            nomDirectorio = a
            opcionDir = True
        elif o in ("-h", "--help"):
            usoAyuda()
            sys.exit()
        else:
            assert False, "unhandled option"

    # Argumentos para la función de reanalisis
    if reanalisis:
        return (nomArchivoSalida, "", reanalisis, nomArchivoDace , opcionDir, args, "")
    elif opcionDir:
        # Argumentos generar ofertas. Los archivos están en un directorio
        try:
            direcContenido = listdir(nomDirectorio)
        except NotADirectoryError:
            print(nomDirectorio, "no es un directorio")
            sys.exit(2)

        return (nomArchivoSalida, nomArchivoMaterias, reanalisis,
                nomArchivoDace, opcionDir, direcContenido, nomDirectorio)
    else:
        args.append(nomArchivoDace)
        return (nomArchivoSalida, nomArchivoMaterias, reanalisis,
                nomArchivoDace, opcionDir, args , "")

if __name__ == '__main__':
    (nomArchivoSalida, nomArchivoMaterias, reanalisis,
     nomArchivoDace, opcionDir, args, nomDirectorio) = obtArgs(sys.argv[1:])

    # Borrar el contenido del archivo de salida si existe
    if isfile(nomArchivoSalida):
        remove(nomArchivoSalida)

    # Obtener las materias requeridas
    if not reanalisis:
        listaMaterias = []
        try:
            matArch = open(nomArchivoMaterias, 'r')
        except FileNotFoundError:
            print("El archivo no encontrado", nomArchivoMaterias)
            sys.exit(2)
        except IsADirectoryError:
            print(nomArchivoMaterias ,"es un directorio. Se requiere un archivo")
            sys.exit(2)
        except UnicodeDecodeError:
            print("Archivo no codificado para UTF-8. Recodifique.")
            sys.exit(2)
        else:
            for materia in matArch:
                if (not materia.isspace()) and materia[0] != '#':
                    listaMaterias.append(materia.rstrip(' \t\n\r'))

        (listaOfertas,listaDACE) = cargarOfertas(args,nomDirectorio,listaMaterias,\
                                                 opcionDir,nomArchivoDace)

        print("\nOfertas cargadas con éxito")
        # imprimirResultados("ListaDace",listaDACE)
        # imprimirResultados("ListaOfertas",listaOfertas)
        procesado = generarOferta(listaOfertas,listaDACE)
    else:
        print("\nReanalizando Ofertas ")
        listaOfertas = []
        sinCabecera = False
        try:
            fdOfertas = open(args[0], 'r')
        except FileNotFoundError:
            print("El archivo no encontrado", args[0])
            sys.exit(2)
        except IsADirectoryError:
            print(nomArchivoMaterias ,"es un directorio. Se requiere un archivo")
            sys.exit(2)
        except UnicodeDecodeError:
            print("Archivo no codificado para UTF-8. Recodifique.")
            sys.exit(2)

        for fila in fdOfertas:
            if sinCabecera:
                temp = fila.split(',')
                listaOfertas.append(temp[0:9] + [temp[9].split('\n')[0]])
                #print(temp[0:9] + [temp[9].split('\n')[0]])
            else:
                sinCabecera = True

        listaDACE = []
        procesarDACE("0800",nomArchivoDace,listaDACE)
        procesado = reanalizarOferta(listaOfertas,listaDACE)

    # Imprimir resultados al archivo de salida
    try:
        fdSalida = open(nomArchivoSalida, 'a')
        fdSalida.write("COD_ASIGNATURA,BLOQUE,LUNES,MARTES" + \
                        ",MIERCOLES,JUEVES,VIERNES,OFERTA,COD_CARRERA,OPERACIÓN\n")
        for fila in procesado:
            fdSalida.write(','.join(fila) + '\n')
    except IsADirectoryError:
        print(nomArchivoSalida ,"es un directorio. Eliga un nombre distinto")
        sys.exit(2)
    except OSError as ose:
        print("Error de E/S: ", ose)
        sys.exit(2)
    finally:
        fdSalida.close()
    print("Ofertas procesadas exitosamente")


    # python procesadorOfertas.py -f OfertasProcesadas.csv
#-d 0800.xls -m materiasRequeridas.txt OfertaPB.xml
# OfertaSIG.pdf OfertaID.xlsx OfertaCE.xls OfertaMatematicas.xls ofertaComputo.xml

# python procesadorOfertas.py -f OfertasProcesadas.csv -d 0800.xls
# -m materiasRequeridas.txt --dir-input=archivos_de_prueba/
