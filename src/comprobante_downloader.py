'''
*
*
*
'''

#---------------------------------------------------------#
#                      IMPORTES                           #
#---------------------------------------------------------#

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import codecs
import getpass
import os
import comprobante_crawler

#---------------------------------------------------------#
#                  DEFINICIÓN DE FUNCIONES                #
#---------------------------------------------------------#

#---------------------------------------------------------#
#                 INICIO DEL CÓDIGO PRINCIPAL             #
#---------------------------------------------------------#

user = str(input("Usuario: "))
password = getpass.getpass("Clave: ")

driver = webdriver.Chrome("./chromedriver")
driver.get("http://comprobante.dii.usb.ve")
driver.find_element_by_name("username").send_keys(user)
driver.find_element_by_name("password").send_keys(password)
driver.find_element_by_name("submit").click()
#driver.find_element_by_link_text("Horario de Clases").click()

comprobante_crawler.get_student_data(driver.page_source)
