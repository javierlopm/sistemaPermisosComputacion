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

import bs4
import codecs
import getpass
import os
import re
import requests

## PENDIENTE: Modularizar esto para que no haya codigo repetido de esta funcion
## en comprobante_crawler y coord_crawler
def format_id(student_id):
    if   re.match(pattern[0],student_id):
        return student_id
    elif (re.match(pattern[1],student_id) or re.match(pattern[2],student_id)):
        return student_id[0:2] + student_id[3:8]
    else:
        print ("Error: formato de carnet invalido para " + student_id +
               " probar con 0000000 , 00-00000 o 00-00000@usb.ve" )
        # raise Exception("studen_id format error" )
        return None

class StudentCurrentDownloader():

    def __init__(self,user,password,save_dir="graphs_manager/COMPR_HTML"):

        """ Authenticates the given user with the university's CAS.
            NOTE: Since the university uses a self signed SSL certificate, I had to disable ceritificate
            verification, which triggers a warning at runtime.
            Parameters:
                user: the user's username
                password: the user's password
            Returns:
                A dict holding the cookie received after authentication (empty if it failed)
                A requests.Session object with the same cookie which can be used to make requests
        """

        # Logs in with Coordination credentials
        session = requests.Session()
        first_response = session.get(DST_URL, verify=False)
        soup = bs4.BeautifulSoup(first_response.content, 'html.parser')
        lt = soup.find("input", {"name": "lt"}).attrs["value"]
        jsessionid = first_response.cookies.get('JSESSIONID')
        params = {
            'username': user,
            'password': password,
            'lt': lt,
            '_eventId': 'submit',
            'submit': 'INICIAR SESIÓN'
        }
        second_response = session.post(DST_URL + ';jsessionid=' + jsessionid, data=params)
        resp = session.get(DST_URL + "?service=https%3A%2F%2Fcomprobante.dii.usb.ve%2FCAS%2Flogin.do", verify=False)

        self.save_dir = save_dir
        self.session = session

    def search_student(self, student_id):

        student_id = self.format_id(student_id)

        if student_id:

            params = {
                "cedula" : student_id,
                "tipo" : "1"
            }

            resp_buscador = self.session.post("https://comprobante.dii.usb.ve/CAS/consultaCarnet.do",data=params, verify=False)

            file = codecs.open("./" + self.save_dir + "/" + student_id[0:2] + "-" + student_id[2:] + ".html", "w",encoding="iso-8859-1")
            file.write(resp_buscador.text)
            file.close()




def get_current_classes(comprobante_html, filtro=None):

    all_classes = []
    file = codecs.open(comprobante_html,"r",encoding="iso-8859-1").read()
    parser = bs4.BeautifulSoup(file,'html.parser')
    schedule_table = parser.body.find_all("td",colspan="10")

    for course in schedule_table:
        trimmed_course = course.text.strip()
        all_classes.append(trimmed_course)

    return all_classes

#---------------------------------------------------------#
#                 INICIO DEL CÓDIGO PRINCIPAL             #
#---------------------------------------------------------#

#with open("/home/prmm95/Bureau/comprobantePablo.html","r",encoding="iso-8859-1") as comprobante:
#    data_comprobante = comprobante.read()
#    get_student_data(data_comprobante)
