#!/usr/bin/python3.5
import xml.sax
import re

class Ofertas( xml.sax.ContentHandler ):
   def __init__(self, corresDiaDistancia):
      self.filas = []
      self.celda = ""
      self.tuplas = []
      self.corresDiaDistancia = corresDiaDistancia
      self.ultimoDia = ''
      self.patronDia = "(L[Uu][Nn]|M[Aa][Rr]|M[Ii][Ee][Rr]?|[Jj][Uu][Ee]|V[Ii][Ee][Rr]?)"
      self.patronHoras = "\d{1,2}-\d{1,2}"
      self.patronHorario = self.patronDia + "((\s)*-(\s)*" + self.patronDia + ")?" \
         + "\s+" + self.patronHoras
      self.patronBloque = "[Bb][Ll][Oo][Qq][Uu]?[Ee]?(\s)+\D"
   # Call when an element starts
   def startElement(self, tag, attributes):
      pass


   # Call when an elements ends
   def endElement(self, tag):
      if tag == "row":
         self.tuplas.append(self.filas)
         self.filas = []
         self.ultimoDia = ''

      if tag == "txt":
         #print("TXT", self.celda)
         if self.filtrarMateria(self.celda):
            self.filas.append(self.celda)

         #print("Mi exp Reg",searchBloque, self.celda )
         searchBloque = re.search(self.patronBloque, self.celda)
         if searchBloque:
            self.filas.append(self.filtrarBloque(self.celda))

         searchObj = re.search(self.patronHorario, self.celda)
         # Para notificar error del formato posiblemnete haya que colocar
         # una excepcion por aqui
         #print("Mi exp Reg",searchObj, self.celda )
         if searchObj:
            #print("Patron reconocido:", searchObj.group())
            txt = dividirStr(self.celda)
            dias = dividirStr(txt[0],"-")
            # Garantizar que solo los digitos de las horas
            txt =  txt[1][0:4]
            #print(dias, txt)
            if len(dias) > 1:
               self.filas.append((txt,dias[0][0:2].upper()))
               self.filas.append((txt,dias[1][0:2].upper()))
            else:
               self.filas.append((txt,dias[0][0:2].upper()))

         self.celda = ""

   # Call when a character is read
   def characters(self, content):
      if not (content.isspace()):
         #print (content.strip(' \t\n\r'))
         self.celda = content.strip(' \t\n\r.-*()')

   def filtrarBloque(self,txt):
      return dividirStr(txt)[1]

   def filtrarMateria(self,txt):
      #print("TXT", txt)
      if len(txt) == 6 and txt[0].isalpha() and txt[1].isalpha() \
         and txt[2].isdigit():
         return True
      return False

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

# Función auxiliar para el ordenamiento de los horarios
def ordenarDias(txt):
   # Accede a una variable no local
   corresDiaDistancia = { 'LU' : 1, 'MA' : 2, 'MI' : 3, 'JU' : 4, 'VI' : 5} # CORREGIR EL ALCANCE
   return corresDiaDistancia[txt[1]]

# Funcion auxiliar para dividir cadenas de caracteres por un delimitador
def dividirStr(txt, delim = " "):
   cadena = []
   palabra = ""
   for c in txt:
      if delim == c and (palabra != ""):
         cadena.append(palabra)
         palabra = ""
      else:
         if c != delim:
            palabra += c

   if palabra != "":
      cadena.append(palabra)

   return cadena

def procesarDOC(nombreArchivoEntrada,fdArchivoSalida):
   corresDiaDistancia = { 'LU' : 1, 'MA' : 2, 'MI' : 3, 'JU' : 4, 'VI' : 5}
   # create an XMLReader
   parser = xml.sax.make_parser()
   # turn off namepsaces
   parser.setFeature(xml.sax.handler.feature_namespaces, 0)

   # override the default ContextHandler
   Handler = Ofertas(corresDiaDistancia)
   parser.setContentHandler( Handler )
   parser.parse(nombreArchivoEntrada)

   # Ordenar de acuerdo al formato (COD_ASIGNATURA,BLOQUE,HORARIO)
   # Concatenar en un solo string e imprimir filas y
   # escribir filas en un archivo estilo csv.
   acum = ""
   for fil in Handler.tuplas[1:]:
      #Eliminar Len si todos las filas deben tener horario
      if len(fil) > 1:
         if isinstance(fil[1],tuple):
            acum = fil[0] + ',A'
            horariosOrdenados = sorted(fil[1:], key=ordenarDias)
         else:
            acum = ",".join(fil[:2])
            horariosOrdenados = sorted(fil[2:], key=ordenarDias)
         acum += componerHorarioCSV(horariosOrdenados)
      else:
         acum = fil[0] + ',A'
      fdArchivoSalida.write(acum + '\n')
      acum = ""

if ( __name__ == "__main__"):
   corresDiaDistancia = { 'LU' : 1, 'MA' : 2, 'MI' : 3, 'JU' : 4, 'VI' : 5}
   # create an XMLReader
   parser = xml.sax.make_parser()
   # turn off namepsaces
   parser.setFeature(xml.sax.handler.feature_namespaces, 0)

   # override the default ContextHandler
   Handler = Ofertas(corresDiaDistancia)
   parser.setContentHandler( Handler )
   parser.parse("oferta-sept-dic-2016-version-final_Computo.xml")

   # Ordenar de acuerdo al formato (COD_ASIGNATURA,BLOQUE,HORARIO)

   f = open('OfertaDocCSV.csv', 'a')
   # Concatenar en un solo string e imprimir filas y
   # escribir filas en un archivo estilo csv.
   f.write("COD_ASIGNATURA,BLOQUE,L,M,MI,J,V\n")
   acum = ""
   for fil in Handler.tuplas[1:]:
      #Eliminar Len si todos las filas deben tener horario
      if len(fil) > 1:
         #print("Fila", fil, fil[1:])
         if isinstance(fil[1],tuple):
            acum = fil[0] + ',A'
            #print("Seleccion1", fil[1:])
            horariosOrdenados = sorted(fil[1:], key=ordenarDias)
         else:
            #print("Seleccion2", fil[2:])
            acum = ",".join(fil[:2])
            horariosOrdenados = sorted(fil[2:], key=ordenarDias)
         acum += componerHorarioCSV(horariosOrdenados)
      else:
         acum = fil[0] + ',A'
      #print("Al escribir", acum)
      f.write(acum + '\n')
      acum = ""
   f.close()

# Pruebas sobre dividirStr
   # print(dividirStr("Mar -Jue  5-6   "))
   # print(dividirStr("    Mar -Jue  5-6   "))
   # print(dividirStr("    5-6   "))
   # print(dividirStr("       "))
   # print(dividirStr(""))
   # prueba = [('9-10', 'MI'), ('9-10', 'JU'), ('9-10', 'LU')]
   # prueba1 = [('9-10', 'MI'), ('9-10', 'JU'), ('9-10', 'LU')]
   # # print(sorted(prueba,key=ordenarDias))
   # horarios = sorted(prueba,key=ordenarDias)
   # print(componerHorarioCSV(horarios))
