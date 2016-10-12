import unittest
import os
import sys
sys.path.insert(0, os.path.abspath('..'))

from procesadorOfertas import procesarDOC
from procesadorOfertas import procesarPDF
from procesadorOfertas import procesarXLS


class Contexto(unittest.TestCase):
    def setUp (self):
        self.listaMaterias = []
        for materia in open("../materiasRequeridas.txt", 'r'):
            if (not materia.isspace()) and materia[0] != '#':
                self.listaMaterias.append(materia.rstrip(' \t\n\r'))

        self.fdSalida = []
        # Respuesta correcta
        self.Correcta_doc1 = \
            [   ["PB5611","A",'','','','',''], \
                ["PB5671",'A',"7-8","","7-8","2-3",""]
            ]
        self.Correcta_doc2 = \
            [
                ["PB5611","A","","","","5-7",""],
                ["PB5611","B","","3-4","","3-4",""],
                ["PB5611","C","","","","","5-6"],
                ["PB5671","A","7-8","","7-8","2-3",""],
                ["CO5212","A","3-4","","3-4","",""],
                ["CO5212","D","","4","","",""],
            ]
        self.Correcta_doc3 = \
            [
                ["CO3211","C","","3-4","3-4","3-4",""],
                ["CO3211","F","3-4","5-6","3-4","",""],
                ["CO3121","A","","1-2","5-6","","1-2"],
                ["CO3121","B","3-4","","3-4","","5-6"],
                ["CO3321","G","3-4","","3-4","","5-6"],
                ["CO3321","H","5-6","","5-6","","7-8"],
                ["CO3411","A","7-8","","7-8","5-7",""],
                ["CO5212","A","","5-6","","5-6",""],
                ["CO5213","A","5-6","","5-6","",""],
                ["CO5412","A","3-4","","3-4","",""],
                ["CO6531","A","","3-4","","3-4",""],
                ["CO6612","A","","5-6","","5-6",""],
            ]
        self.Correcta_doc4 = \
            [
                ["CO3211","C","","3-4","3-4","3-4",""],
                ["CO3211","F","3-4","5-6","3-4","",""],
                ["CO3121","A","","1-2","","1-2","5-6"],
                ["CO3121","B","","","3-4","5-6","3-4"],
                ["CO3321","G","3-4","","3-4","","5-6"],
                ["CO3321","H","5-6","","7-8","","5-6"],
                ["CO3411","A","5-7","7-8","7-8","",""],
                ["CO5212","A","","5-6","","5-6",""],
                ["CO5213","A","5-6","","5-6","",""],
                ["CO5412","A","3-4","","3-4","",""],
                ["CO6531","A","","3-4","","3-4",""],
                ["CO6612","A","","5-6","","5-6",""],
            ]
        

class ProcesarDOC1_XML (Contexto):
    def runTest (self):
        """ Prueba de procesamiento sobre Doc1.xml"""
        procesarDOC("doc1.xml",self.listaMaterias, self.fdSalida)
        self.assertEqual(self.fdSalida, self.Correcta_doc1, "Falla de procesamiento DOC. Archivo doc1.xml")

class ProcesarDOC2_XML (Contexto):
    def runTest (self):
        """ Prueba de procesamiento sobre Doc2.xml """
        #procesarDOC(caminoArchivoEntrada,listaMaterias,fdSalida):
        procesarDOC("doc2.xml",self.listaMaterias, self.fdSalida)
        self.assertEqual(self.fdSalida, self.Correcta_doc2, "Falla de procesamiento DOC. Archivo doc2.xml")



class ProcesarDOC1_PDF (Contexto):
    def runTest (self):
        """ Prueba de procesamiento sobre doc2.pdf """
        procesarPDF("doc1.pdf",self.listaMaterias, self.fdSalida)
        self.assertEqual(self.fdSalida, self.Correcta_doc1, "Falla de procesamiento PDF. Archivo doc1.pdf")

class ProcesarDOC2_PDF (Contexto):
    def runTest (self):
        """ Prueba de procesamiento sobre doc2.pdf """
        procesarPDF("doc2.pdf",self.listaMaterias, self.fdSalida)
        self.assertEqual(self.fdSalida, self.Correcta_doc2, "Falla de procesamiento PDF. Archivo doc2.pdf")

class ProcesarDOC3_PDF (Contexto):
    def runTest (self):
        """ Prueba de procesamiento sobre doc3.pdf """
        procesarPDF("doc3.pdf",self.listaMaterias, self.fdSalida)
        self.assertEqual(self.fdSalida, self.Correcta_doc3, "Falla de procesamiento PDF. Archivo doc3.pdf")
 
class ProcesarDOC4_PDF (Contexto):
    def runTest (self):
        """ Prueba de procesamiento sobre doc3.pdf """
        procesarPDF("doc4.pdf",self.listaMaterias, self.fdSalida)
        self.assertEqual(self.fdSalida, self.Correcta_doc4, "Falla de procesamiento PDF. Archivo doc4.pdf")

def suite():
    suite = unittest.TestSuite()
    suite.addTest (ProcesarDOC1_XML())
    suite.addTest (ProcesarDOC2_XML())
    return suite

def suitePDF():
    suite = unittest.TestSuite()
    suite.addTest (ProcesarDOC1_PDF())
    suite.addTest (ProcesarDOC2_PDF())
    suite.addTest (ProcesarDOC3_PDF())
    suite.addTest (ProcesarDOC4_PDF())
    return suite

if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    test_suite = suitePDF()
    runner.run (test_suite)