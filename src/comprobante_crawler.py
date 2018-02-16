'''
*    Archivo: comprobante_crawler.py
*
*    Descripción: En este archivo se implementará
*    el parseo del html de un comprobante usando
*    BeautifulSoup para obtener las materias
*    en curso de un estudiante
*
*    Autor: Pablo Maldonado - prmmm95@gmail.com
'''
#---------------------------------------------------------#
#                      IMPORTES                           #
#---------------------------------------------------------#

from bs4 import BeautifulSoup # usado para el parseo de los HTMLs

#---------------------------------------------------------#
#                  DEFINICIÓN DE FUNCIONES                #
#---------------------------------------------------------#

def get_student_data(comprobante_html):
    '''
        Descripción:
        Entradas:
        Salidas:
    '''
    parser = BeautifulSoup(comprobante_html,'html.parser')

    #schedule_table = parser.body.find_all("table", width="700")
    schedule_table = parser.body.find_all("tr",style="display:none")

    for course in schedule_table:
        print(course['id'])


#---------------------------------------------------------#
#                 INICIO DEL CÓDIGO PRINCIPAL             #
#---------------------------------------------------------#

#with open("/home/prmm95/Bureau/comprobantePablo.html","r",encoding="iso-8859-1") as comprobante:
#    data_comprobante = comprobante.read()
#    get_student_data(data_comprobante)
