import sys
import getopt


class Vacio_Error(Exception):
  """Excepcion para el caso que alguna lista este vacio"""
  def __init__(self,ubicacion):
    self.ubicacion = ubicacion
    def __str__(self):
        return repr(self.ubicacion)

corresDiaDistancia = { 'LU' : 1, 'MA' : 2, 'MI' : 3, 'JU' : 4, 'VI' : 5}
# Función auxiliar para el ordenamiento de los horarios
def ordenarDias(txt):
   # Accede a una variable no local
   return corresDiaDistancia[txt[1]]

# Función auxiliar para verificar resultados por pantalla
def imprimirResultados(mensaje,listaOfertas):
    print(mensaje + ": ")
    for fila in listaOfertas:
        print(fila)
    print('\n')

# Funcion auxiliar para dividir cadenas de caracteres por un delimitador
def dividirStr(txt, delims = " "):
   cadena = []
   palabra = ""
   for c in txt:
      if c in delims and (palabra != ""):
         cadena.append(palabra)
         palabra = ""
      else:
         if c not in delims:
            palabra += c

   if palabra != "":
      cadena.append(palabra)

   return cadena

def normalizarMateria(txt):
    mat = ""
    for char in txt:
        if char != ' ' and char != '-' and char != '\n':
            mat += char
    return mat

def componerHorarioCSV(listaHorarios):
   corresDiaDistancia = { 'LU' : 1, 'MA' : 2, 'MI' : 3, 'JU' : 4, 'VI' : 5} # CORREGIR EL ALCANCE
   ultimoDia = ''
   horarios = ""
   for (hora,dia) in listaHorarios:
      if ultimoDia == '':
         ultimoDia = dia
         horarios += (corresDiaDistancia[dia] * ',') + hora
      else:
         horarios += ((corresDiaDistancia[dia] -  \
                    corresDiaDistancia[ultimoDia]) * ',') + hora
         ultimoDia = dia

   if ultimoDia != '' and corresDiaDistancia[ultimoDia] < 5:
         horarios += ((5 - corresDiaDistancia[ultimoDia]) * ',')

   return horarios

#
# Funciones de linea de comando para los procesadores individuales
#

# Impresión de ayuda
def usoAyuda():
    print("""Uso: procesador [-f nombre_archivo_salida]
                    -m archivo_materias_requeridas archivo_a_procesar
    prog [-h, --ayuda] """)

# Pasaje de argumentos para los procesadores
def obtArgs(entrada):
    nomArchivoSalida = ""
    nomArchivoMaterias = ""
    try:
        opts, args = getopt.getopt(entrada, "f:m:h", ["ayuda"])
    except getopt.GetoptError as err:
        # print ayuda information and exit:
        print(err) # will print something like "option -a not recognized"
        usoAyuda()
        sys.exit(2)

    for o, a in opts:
        if o == "-f":
            nomArchivoSalida = a
        elif o == "-m":
            nomArchivoMaterias = a
        elif o in ("-h", "--ayuda"):
            usoAyuda()
            sys.exit(0)
        else:
            assert False, "unhandled option"

    if not nomArchivoMaterias:
      print("Se requiere el parametro -m")
      sys.exit(2)

    return (nomArchivoSalida, nomArchivoMaterias, args)

def cargarMaterias(nomArchivoMaterias):
    listaMaterias = []

    try:
        f = open(nomArchivoMaterias, 'r')
    except FileNotFoundError:
        print("El archivo no encontrado", nomArchivoMaterias)
        sys.exit(2)
    except IsADirectoryError:
        print(nomArchivoMaterias ,"es un directorio. Se requiere un archivo")
        sys.exit(2)
    else:
        for materia in f:
            if (not materia.isspace()) and materia[0] != '#':
                listaMaterias.append(materia.rstrip(' \t\n\r'))

    return listaMaterias
