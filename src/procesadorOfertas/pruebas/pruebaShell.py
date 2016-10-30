import sys
import getopt
from os import listdir

def usoAyuda():
    print("""Uso: pruebaShell.py -f nombre_archivo_salida -d nombre_archivo_dace
                    -m archivo_materias_requeridas [--dir-input=nomDir ]
                    archivo1.pdf archivo2.xls ... archivoN
    prog [-h, --help] """)

def obtArgs(entrada):
    nomArchivoDace = ""
    nomArchivoSalida = ""
    nomArchivoMaterias = ""
    nomDirectorio = ""
    opcionDir = False
    try:
        opts, args = getopt.getopt(entrada, "d:f:m:h", ["help","input-dir="])
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
        elif o == "--input-dir":
            nomDirectorio = a
            opcionDir = True
        elif o in ("-h", "--help"):
            usoAyuda()
            sys.exit()
        else:
            assert False, "unhandled option"

    if opcionDir:
        return (nomArchivoSalida, nomArchivoMaterias, \
                nomArchivoDace, opcionDir, listdir(nomDirectorio), nomDirectorio)
    else:
        args.append(nomArchivoDace)
        return (nomArchivoSalida, nomArchivoMaterias, \
                nomArchivoDace, opcionDir, args , "")

if __name__ == '__main__':
    print("El shell BASH me ejecutó. Esta es mi salida:")
    (nomArchivoSalida, nomArchivoMaterias,
     nomArchivoDace, opcionDir, args, nomDirectorio) = obtArgs(sys.argv[1:])

    print("archivo_salida: ", nomArchivoSalida)
    print("Archivo_materias: ", nomArchivoMaterias)
    print("Archivo_DACE: ", nomArchivoDace)
    print("Directorio?: ", opcionDir)
    print("Directorio a buscar: ", nomDirectorio)
    print("Argumentos: ", args)
    exit()