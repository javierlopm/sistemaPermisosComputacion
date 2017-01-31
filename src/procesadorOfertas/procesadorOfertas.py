#!/usr/bin/python3.x

# Nombre: Daniel Leones
# Carné: 09-10977
# Fecha: 7/12/2016
# Descripción: Programa principal. Este program realiza las siguientes funciones:
#   - Generar ofertas a partir de documentos de los departamentos y una
#     lista de DACE.
#   - Reanalizar ofertas realizadas con nuevas listas de DACE. Esto se realiza
#     mediante la opción -r.
# En ambos casos, la salida es un archivo en formato CSV.
#
# En caso de requerir expandir el procesador a formatos adicionales sólo se debe
# agregar las lineas pertienentes en la funcion cargarOfertas.

from procesadorXLS import procesarXLS
from procesadorDOC import procesarDOC
from procesadorPDF import procesarPDF
from procesadorDACE import procesarDACE
from funcionesAuxiliares import imprimirResultados, Vacio_Error, cargarOfertasCSV
from os.path import splitext, isfile, join
from os import remove, listdir
import sys
import getopt
import re

# Función: cargarOfertas
# Argumentos:
#   listaArchivos:  [String], lista de nombre de los archivos.
#   nomDirectorio:  String, camino hacia el directorio
#   nomArchivoDace: String, nombre del archivo de DACE.
#   opcionDir:      Booleano, modo directorio
#   listaMaterias: [String], lista de materias
# Salida: ([[String]],[[String]]) , lista de ofertas en estilo CSV.
#
# Descripción: despacho de archivos de ofertas para cada procesador que sea acoplado
# a esta función. En caso que alguna variable de salida esté vacia, se levanta una
# excepción y se detendrá el programa.
def cargarOfertas(listaArchivos, nomDirectorio, listaMaterias,
                  opcionDir, nomArchivoDace):

    listaOfertas = []
    listaDACE = []
    for archivo in listaArchivos:
        # Selección de archivos para procesar. Se extrae su extensión para
        # elegir el procesador adecuado
        ext = splitext(archivo)[1]

        # Constuir el camino para procesar los archivos.
        if opcionDir:
            if ext != ".doc" and ext != ".txt":
                camino = join(nomDirectorio,archivo)
                print(camino)

        # En caso de abarcar más formatos, se agrega en este espacio para las ofertas
        # 0800.
        if  nomArchivoDace == archivo:
            if  ext == ".fodt" or ext == ".xml":
                procesarDOC(camino,listaMaterias ,listaDACE)
            elif ext == ".pdf":
                procesarPDF(camino, listaMaterias, listaDACE)
            elif ext == ".xls" or ext == ".xlsx":
                procesarXLS(camino, False, listaMaterias, listaDACE)
            continue

        # En caso de abarcar más formatos, se agrega en este espacio para las ofertas
        # departamentales
        if  ext == ".fodt" or ext == ".xml":
            procesarDOC(camino,listaMaterias ,listaOfertas)
        elif ext == ".pdf":
            procesarPDF(camino,listaMaterias, listaOfertas)
        elif ext == ".xls" or ext == ".xlsx":
            procesarXLS(camino, True, listaMaterias, listaOfertas)


    if not (listaOfertas):
        raise Vacio_Error("Lista de Ofertas")
    if not listaDACE:
        raise Vacio_Error("Lista de DACE. " + nomArchivoDace)

    return (listaOfertas, listaDACE)

# Función: generarOferta
# Argumentos:
#   listaOfertas:   [[String]], lista de ofertas en estilo CSV.
#   listaDACE:      [[String]], lista de ofertas en estilo CSV.
# Salida: [[String]], lista de ofertas en estilo CSV.
#
# Descripción: etapa de analisis y comparación, cada oferta se análiza de acuerdo
# ciertas reglas (ver informe) y se agrega a una lista final. En caso que la
# variable de salida esté vacia, se levanta una excepción y se detendrá el programa.
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
                procesado.append(filaDace + ['0800','E'])
            else:
                procesado.append(filaDace + ['0800',''])

        filaEncontrada = False

    # Descartar las materias de la lista de DACE
    # que no se encuentren en la oferta de dptos
    for filaPorBorrar in materiasDacePorBorrar:
        listaDACE.remove(filaPorBorrar)

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
                procesado.append(filaOfertas + ['0800',''])
            else:
                procesado.append(filaOfertas + ['0800','M'])
        else:
        # Caso 3:
            procesado.append(filaOfertas + ['0800','I'])

        filaEncontrada = None

    if not procesado:
        raise Vacio_Error(nomArchivoSalida)

    return procesado


# Función: generarOferta
# Argumentos:
#   listaOfertas:   [[String]], lista de ofertas en estilo CSV.
#   listaDACE:      [[String]], lista de ofertas en estilo CSV.
# Salida: [[String]], lista de ofertas en estilo CSV.
#
# Descripción: etapa de analisis y comparación con una lista general de DACE,
# cada oferta se análiza de acuerdo a ciertas reglas (ver informe) contra la listaDACE
# y se agrega a una lista final. En caso que la variable de salida esté vacia, se
# levanta una excepción y se detendrá el programa.
def reanalizarOferta(listaOfertas,listaDACE):
    procesado = []

    # Realizar comparaciones para I y M. Desde el pto de vista de las ofertas.
    filaEncontrada = None
    for filaOfertas in listaOfertas:
        for filaDace in listaDACE:
            if filaOfertas[0] == filaDace[0] \
                and filaOfertas[1] == filaDace[1]:
                filaEncontrada = filaDace
                break

        # Caso 1:
        if filaEncontrada:
            for (itemOferta,itemDace) in zip(filaOfertas,filaEncontrada):
                match = itemOferta == itemDace
                if not match:
                    break

            if match:
                procesado.append(filaOfertas[:9] + [''])
            elif filaOfertas[9] == 'E':
                procesado.append(filaEncontrada[:9] + ['M'])
            else:
                procesado.append(filaOfertas[:9] + ['M'])
        else:
            procesado.append(filaOfertas[:9] + ['I'])

        filaEncontrada = None

    return procesado

# Función: usoAyuda
# Argumentos:
#   Ninguno
# Salida:
#   Ninguno
#
# Descripción: imprimir ayuda de uso. Para uso de procesadorOfertas
def usoAyuda():
    print("""Uso: prog -f nombre_archivo_salida -d nombre_archivo_dace
                    -m archivo_materias_requeridas [--dir-input=nomDir ]
                    archivo1.pdf archivo2.xls ... archivoN
    prog [-h, --help] """)

# Función: obtArgs
# Argumentos:
#   entrada: String, argumentos de la linea de comando
# Salida: (String, String, String, String, Booleano, String, String)
#
# Descripción: pasaje de argumentos para al procesador de ofertas.
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

    # Código para ejecutar etapa 1
    if not reanalisis:
        # Obtener las materias requeridas
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

        try:
            (listaOfertas,listaDACE) = cargarOfertas(args,
                                             nomDirectorio,listaMaterias,
                                             opcionDir,nomArchivoDace)
            print("\nOfertas cargadas con éxito")
            procesado = generarOferta(listaOfertas,listaDACE)
        except Vacio_Error as ve:
            print("Falta información en: ", ve)
            print("Revise el formato y datos de los archivos fuentes")
            print("Abortar")
            sys.exit(2)
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
        # Código para ejecutar etapa 2
        print("\nReanalizando Ofertas ")
        listaOfertas = cargarOfertasCSV(args[0],9)
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
