# -*- coding: utf-8 -*-
#!/usr/bin/python
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from electivas import *
import pdb
import codecs
import re
import os

# Valid students id formats
pattern    = []
pattern.insert(0 , re.compile("\d{7}"))
pattern.insert(1 , re.compile("\d{2}\-\d{5}"))
pattern.insert(2 , re.compile("\d{2}\-\d{5}\@usb\.ve"))

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

def show_carnet(int_carnet):
    std_str = str(int_carnet).rjust(7,'0')
    return std_str[0:2] + "-" + std_str[2:8]

class StudentDownloader():
    """Class for web crawler that search for students id and downloads
        their academic info
    """
    def __init__(self,user,password,save_dir):
        chromedriver = "./chromedriver"
        os.environ["webdriver.chrome.driver"] = chromedriver
        driver = webdriver.Chrome(chromedriver)
        self.browser      = driver #webdriver.Firefox()
        self.first_search = True
        self.save_dir     = save_dir

        self.browser.get("http://expediente.dii.usb.ve")
        self.browser.find_element_by_name("username").send_keys(user)
        self.browser.find_element_by_name("password").send_keys(password)
        self.browser.find_element_by_name("submit").click()
        

    def __str__(self):
        return ("(StudentDownloader  first_seach:" + str(self.first_search) + 
                "   save_dir:" + save_dir)

    def format_id(self,student_id):
        if   re.match(pattern[0],student_id):
            return student_id
        elif (re.match(pattern[1],student_id) or re.match(pattern[2],student_id)):
            return student_id[0:2] + student_id[3:8]
        else:
            print ("Error: formato de carnet invalido para " + student_id + 
                   " probar con 0000000 , 00-00000 o 00-00000@usb.ve" )
            # raise Exception("studen_id format error" ) 
            return None

    def search_student(self,student_id):
        student_id = self.format_id(student_id)

        if student_id:
            if self.first_search:
                self.first_search = False
            else:
                self.browser.find_element_by_link_text("Nueva Consulta").click()
        
            self.browser.find_element_by_name("texto").send_keys(student_id)
            self.browser.find_element_by_tag_name("form").submit()
            self.browser.find_element_by_link_text("Informe Académico").click()

            expediente = self.browser.page_source

            file = codecs.open( "./" + self.save_dir + "/" + student_id[0:2] + "-" + student_id[2:] + ".html", "w",encoding="iso-8859-1")
            file.write(expediente)
            file.close()

            return self.get_student_data(expediente)

    def get_student_data(self,str_exp):
        from bs4 import BeautifulSoup

        parser = BeautifulSoup(str_exp, 'html.parser')

        nombres = parser.body.strong.text.split("\n")
        last_table = parser.body.table.table.find_all("table")[-3]
        
        aprobadas  = int(last_table.find_all("td")[5].text)
        indice     = float(parser.body.table.table.find_all("table")[-6].
                                td.text.split("\n")[1].split(" ")[-1])
        nombres    = nombres[2].split("\t")[-1] + nombres[3].split("\t")[-1]

        return (nombres,indice,aprobadas)


    def close(self):
        self.browser.close()


CODIGO = 0
NOMBRE = 1
NOTA   = 3

def get_all_classes(inf_acad,filtro=None):
    from bs4 import BeautifulSoup
    all_classes = []
    file = codecs.open( inf_acad, "r",encoding="iso-8859-1").read()
    parser = BeautifulSoup(file, 'html.parser')

    table = parser.table.table
    codigo = table.findAll("td",{"width":"50","align":"left"})
    nombre = table.findAll("td",{"width":"380","align":"left"})
    nota   = table.findAll("td",{"width":"45","align":"center"})
    for i in range(len(codigo)):
        if filtro(codigo[i].text):
            trim = codigo[i].findParents()[5].td.text[4:]
            all_classes.append("{}|{}|{}|{}".format(codigo[i].text,nombre[i].text,nota[i].text,trim))

    return all_classes

def get_gen(inf_acad):
    from re import compile,match
    patt = re.compile("[A-Z]{3}\d{3}")
    filtro = lambda x: patt.match(x) and not (x in ciclo_basico)

    return get_all_classes(inf_acad,filtro)
    

def get_elect(inf_acad):
    filtro = lambda x: (x in area) or (x in libres)
    return get_all_classes(inf_acad,filtro)