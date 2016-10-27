# -*- coding: utf-8 -*-
#!/usr/bin/python
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pdb
import codecs
import re

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
    std_str = str(int_carnet)
    return std_str[0:2] + "-" + std_str[2:8]

class StudentDownloader():
    """Class for web crawler that search for students id and downloads
        their academic info
    """
    def __init__(self,user,password,save_dir):
        self.browser      = webdriver.Firefox()
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

            file = codecs.open( "./" + self.save_dir + "/" + student_id[0:2] + "-" + student_id[3:] + ".html", "w",encoding="iso-8859-1")
            file.write(self.browser.page_source)
            file.close()

