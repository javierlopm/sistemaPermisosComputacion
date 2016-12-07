#!/usr/bin/python3

# Nombre: Daniel Leones
# Carné: 09-10977
# Fecha: 7/12/2016
# Descripción: funciones comunes a todos los módulos del programa

import sys
import getopt

#
# Clase para manejo de excepcion en caso que alguna lista de ofertas de las dos
# etapas se encuentre vacio. Cuando esto, se detendrá el programa.
#
class Vacio_Error(Exception):
  """Excepcion para el caso que alguna lista este vacio"""
  def __init__(self,ubicacion):
    self.ubicacion = ubicacion
    def __str__(self):
        return repr(self.ubicacion)

# Diccionario utilizado para ordenar los horaios para estilos de presentación
# de computo.
corresDiaDistancia = { 'LU' : 1, 'MA' : 2, 'MI' : 3, 'JU' : 4, 'VI' : 5}

# Función: ordenarDias
# Argumentos:
#   txt: String, las dos primeras letras.
# Salida: 
#   posición: Int
# 
# Descripción: Función pasada como argumento para ordenamiento
def ordenarDias(txt):
   # Accede a una variable no local
   return corresDiaDistancia[txt[1]]

# Función: imprimirResultados
# Argumentos:
#   mensaje: String, las dos primeras letras.
#   listaOfertas: [[String]]
# Salida: 
#   ninguna
# 
# Descripción: función auxiliar para verificar resultados por pantalla
def imprimirResultados(mensaje,listaOfertas):
    print(mensaje + ": ")
    for fila in listaOfertas:
        print(fila)
    print('\n')

# Función: dividirStr
# Argumentos:
#   txt: String
#   delims: String, caracteres delimitadores.
# Salida: 
#   cadena: [String]
# 
# Descripción: dividir cadenas de caracteres por un conjunto delimitador. 
# Versión mejorada al split() de Python
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

# Función: dividirStr
# Argumentos:
#   txt: String
# Salida: 
#   cadena: String
# 
# Descripción: eliminar espacios, guión (-), saltos de linea. 
def normalizarMateria(txt):
    mat = ""
    for char in txt:
        if char != ' ' and char != '-' and char != '\n':
            mat += char
    return mat

# Función: componerHorarioCSV
# Argumentos:
#   listaHorarios: [(String,String)], Dia y hora, respectivamente
# Salida: 
#   cadena: String, en formato CSV
# 
# Descripción: convertir y organizar los horarios en formato CSV 
def componerHorarioCSV(listaHorarios):
   #corresDiaDistancia = { 'LU' : 1, 'MA' : 2, 'MI' : 3, 'JU' : 4, 'VI' : 5} # CORREGIR EL ALCANCE
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

# Función: usoAyuda
# Argumentos:
#   Ninguno
# Salida: 
#   Ninguno
# 
# Descripción: imprimir ayuda de uso
def usoAyuda():
    print("""Uso: procesador [-f nombre_archivo_salida]
                    -m archivo_materias_requeridas archivo_a_procesar
    prog [-h, --ayuda] """)

# Función: usoAyuda
# Argumentos:
#   entrada: String, argumentos de la linea de comando
# Salida: (String, String, String)
# 
# Descripción: pasaje de argumentos para los procesadores
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

#
# Funciones para cargar archivos
#


# Función: cargarMaterias
# Argumentos:
#   nomArchivoMaterias: String, camino hacia el archivo de materias
# Salida: [String], lista de códigos de materias
# 
# Descripción: cargas los códigos de materias

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

# Función: cargarOfertasCSV
# Argumentos:
#   caminoArchCSV:  String, camino hacia el archivo CSV
#   alcance:        Int, Nro de campo comenzando desde cero.
# Salida: [[String]], lista de ofertas
# 
# Descripción: cargar las ofertas de acuerdo al siguiente formato:
# COD_ASIGNATURA,BLOQUE,LUNES,MARTES,MIERCOLES,JUEVES,VIERNES,ESPECIAL,CARRERA,OPERACIÓN
# Alcance delimita hasta que campos se leerá. Se lee de izquierda a derecha.
def cargarOfertasCSV(caminoArchCSV,alcance):
    listaOfertas = []
    try:
        fdOfertas = open(caminoArchCSV, 'r')
    except FileNotFoundError:
        print("El archivo no encontrado", args[0])
        sys.exit(2)
    except IsADirectoryError:
        print(nomArchivoMaterias ,"es un directorio. Se requiere un archivo")
        sys.exit(2)
    except UnicodeDecodeError:
        print("Archivo no codificado para UTF-8. Recodifique.")
        sys.exit(2)
    else:
        sinCabecera = False
        for fila in fdOfertas:
            if sinCabecera:
                temp = fila.split(',')
                #print(temp)
                listaOfertas.append(temp[0:alcance] + [temp[alcance].split('\n')[0]])
                #print(temp[0:9] + [temp[9].split('\n')[0]])
            else:
                sinCabecera = True
    return listaOfertas
