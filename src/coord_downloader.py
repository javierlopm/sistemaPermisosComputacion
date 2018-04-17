# -*- coding: utf-8 -*-
#!/usr/bin/python
import getpass
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import os
import pdb
import codecs


usuario = raw_input("Usuario:")
clave = getpass.getpass("Clave  :")
carnets = raw_input("Archivo de carnets:")
dirname = raw_input("Introduzca el nombre de la carpeta: ")


try:
    os.stat("./"+dirname)
except:
    os.mkdir("./"+dirname)


try:
    carnets = open(carnets, "r").read().split()
except:
    print("No se encontro el archivo especificado.")
    exit(1)

driver = webdriver.Firefox()
driver.get("http://expediente.dii.usb.ve")
driver.find_element_by_name("username").send_keys(usuario)
driver.find_element_by_name("password").send_keys(clave)
driver.find_element_by_name("submit").click()

for i, c in enumerate(carnets):
    if (i > 0):
        driver.find_element_by_link_text("Nueva Consulta").click()
    driver.find_element_by_name("texto").send_keys(c)
    driver.find_element_by_tag_name("form").submit()
    driver.find_element_by_link_text("Informe Académico").click()

    # pdb.set_trace()

    file = codecs.open("./" + dirname + "/" + c + ".html",
                       "w", encoding="iso-8859-1")
    file.write(driver.page_source)
    file.close()
