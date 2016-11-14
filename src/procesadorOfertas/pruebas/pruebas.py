import unittest
import os
import sys
sys.path.insert(0, os.path.abspath('..'))

from procesadorOfertas import procesarDOC, procesarPDF, procesarXLS, \
                                generarOferta, cargarOfertas, imprimirResultados


#
# Pruebas de procesamiento. Se prueba cada procesador
#
class Contexto(unittest.TestCase):
    def setUp (self):
        self.listaMaterias = []
        for materia in open("../materiasRequeridas.txt", 'r'):
            if (not materia.isspace()) and materia[0] != '#':
                self.listaMaterias.append(materia.rstrip(' \t\n\r'))

        self.fdSalida = []
        self.carpetaBase = "pruebas_procesamiento/"
        # Respuestas correctas
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
        procesarDOC(self.carpetaBase + "doc1.xml",self.listaMaterias, self.fdSalida)
        self.assertEqual(self.fdSalida, self.Correcta_doc1, "Falla de procesamiento DOC. Archivo doc1.xml")

class ProcesarDOC2_XML (Contexto):
    def runTest (self):
        """ Prueba de procesamiento sobre Doc2.xml """
        #procesarDOC(caminoArchivoEntrada,listaMaterias,fdSalida):
        procesarDOC(self.carpetaBase + "doc2.xml",self.listaMaterias, self.fdSalida)
        self.assertEqual(self.fdSalida, self.Correcta_doc2, "Falla de procesamiento DOC. Archivo doc2.xml")

class ProcesarDOC3_XML (Contexto):
    def runTest (self):
        """ Prueba de procesamiento sobre Doc3.xml """
        #procesarDOC(caminoArchivoEntrada,listaMaterias,fdSalida):
        procesarDOC(self.carpetaBase + "doc3.xml",self.listaMaterias, self.fdSalida)
        self.assertEqual(self.fdSalida, self.Correcta_doc3, "Falla de procesamiento DOC. Archivo doc3.xml")

class ProcesarDOC4_XML (Contexto):
    def runTest (self):
        """ Prueba de procesamiento sobre Doc4.xml """
        #procesarDOC(caminoArchivoEntrada,listaMaterias,fdSalida):
        procesarDOC(self.carpetaBase + "doc4.xml",self.listaMaterias, self.fdSalida)
        self.assertEqual(self.fdSalida, self.Correcta_doc4, "Falla de procesamiento DOC. Archivo doc4.xml")

class ProcesarDOC1_PDF (Contexto):
    def runTest (self):
        """ Prueba de procesamiento sobre doc1.pdf """
        procesarPDF(self.carpetaBase + "doc1.pdf",self.listaMaterias, self.fdSalida)
        self.assertEqual(self.fdSalida, self.Correcta_doc1, "Falla de procesamiento PDF. Archivo doc1.pdf")

class ProcesarDOC2_PDF (Contexto):
    def runTest (self):
        """ Prueba de procesamiento sobre doc2.pdf """
        procesarPDF(self.carpetaBase +  "doc2.pdf",self.listaMaterias, self.fdSalida)
        self.assertEqual(self.fdSalida, self.Correcta_doc2, "Falla de procesamiento PDF. Archivo doc2.pdf")

class ProcesarDOC3_PDF (Contexto):
    def runTest (self):
        """ Prueba de procesamiento sobre doc3.pdf """
        procesarPDF(self.carpetaBase + "doc3.pdf",self.listaMaterias, self.fdSalida)
        self.assertEqual(self.fdSalida, self.Correcta_doc3, "Falla de procesamiento PDF. Archivo doc3.pdf")

class ProcesarDOC4_PDF (Contexto):
    def runTest (self):
        """ Prueba de procesamiento sobre doc4.pdf """
        procesarPDF(self.carpetaBase + "doc4.pdf",self.listaMaterias, self.fdSalida)
        self.assertEqual(self.fdSalida, self.Correcta_doc4, "Falla de procesamiento PDF. Archivo doc4.pdf")


class ProcesarDOC1_XLS (Contexto):
    def runTest(self):
        """ Prueba de procesamiento sobre doc1.xls """
        procesarXLS(self.carpetaBase + "doc1.xls", True, self.listaMaterias, self.fdSalida)
        self.assertEqual(self.fdSalida, self.Correcta_doc1, "Falla de procesamiento XLS. Archivo doc1.xls")

class ProcesarDOC2_XLS (Contexto):
    def runTest (self):
        """ Prueba de procesamiento sobre doc2.xls """
        procesarXLS(self.carpetaBase +  "doc2.xls", True, self.listaMaterias, self.fdSalida)
        self.assertEqual(self.fdSalida, self.Correcta_doc2, "Falla de procesamiento XLS. Archivo doc2.xls")

class ProcesarDOC3_XLS (Contexto):
    def runTest(self):
        """ Prueba de procesamiento sobre doc3.xls """
        procesarXLS(self.carpetaBase + "doc3.xls", True, self.listaMaterias, self.fdSalida)
        self.assertEqual(self.fdSalida, self.Correcta_doc3, "Falla de procesamiento XLS. Archivo doc3.xls")

class ProcesarDOC4_XLS (Contexto):
    def runTest (self):
        """ Prueba de procesamiento sobre doc4.xls """
        procesarXLS(self.carpetaBase +  "doc4.xls", True, self.listaMaterias, self.fdSalida)
        self.assertEqual(self.fdSalida, self.Correcta_doc4, "Falla de procesamiento XLS. Archivo doc4.xls")


#
# Pruebas integrales
#

class ContextoIntegral(unittest.TestCase):
    def setUp(self):
        self.listaMaterias = []
        self.fdSalida = []
        for materia in open("../materiasRequeridas.txt", 'r'):
            if (not materia.isspace()) and materia[0] != '#':
                self.listaMaterias.append(materia.rstrip(' \t\n\r'))

        self.listaArchivos = ["doc1.pdf","doc1.xls","doc1.xml","0800_prueba1.xls"]

        (self.listaOfertas, self.listaDACE) = cargarOfertas( \
                        self.listaArchivos,"pruebas_integrales",
                        self.listaMaterias,True,"0800_prueba1.xls")

        # imprimirResultados("ListaDace",self.listaDACE)
        # imprimirResultados("ListaOfertas",self.listaOfertas)
        # Respuesta correcta
        self.Correcta1 = \
            [
                ["CCW114","A","","3-5","","","","","0800",""],
                ["TS1113","A","","","","","","","0800","E"],
                ["TS2712","A","","","","","","","0800","E"],
                ["CI2511","A","3-4","3-4","3-4","","","","0800",""],
                ["CI2525","A","7-8","7-8","7-8","","","","0800",""],
                ["CI2526","A","5-6","5-6","3-4","","","","0800",""],
                ["EP1308","A","","","","","","","0800",""],
                ["EP2308","A","","","","","","","0800",""],
                ["EP3308","A","","","","","","","0800",""],
                ["CO5412","A","3-4","","3-4","","","","0800","E"],
                ["CO6612","A","5-6","","5-6","","","","0800","I"],
                ["CO6531","B","","3-4","","3-4","","","0800","M"],
                ["CE3114","A","3-5","","","","","","0800","M"],
                ["CE3114","B","5-6","","","5-6","","","0800","M"],
                ["CE3114","C","","","8-10","","","","0800","M"],
                ["CE3419","A","1-3","","","","","","0800","I"],
                ["CE3419","B","","","1-3","","","","0800","I"],
                ["PB5611","A","","","","","","","0800","M"],
                ["PB5671","A","","","","","","","0800","M"],
            ]

class ProcesarOfertasPequena(ContextoIntegral):
    """docstring for ProcesarOfertasPequena"""
    def runTest(self):
        self.fdSalida = generarOferta(self.listaOfertas,self.listaDACE)
        #imprimirResultados("Resultado", self.fdSalida)
        self.assertEqual(self.fdSalida, self.Correcta1, "Falla integral. Archivo 0800_prueba1.xls")


def suiteXLS():
    suite = unittest.TestSuite()
    suite.addTest (ProcesarDOC1_XLS())
    suite.addTest (ProcesarDOC2_XLS())
    suite.addTest (ProcesarDOC3_XLS())
    suite.addTest (ProcesarDOC4_XLS())
    return suite

def suiteDOC():
    suite = unittest.TestSuite()
    suite.addTest (ProcesarDOC1_XML())
    suite.addTest (ProcesarDOC2_XML())
    suite.addTest (ProcesarDOC3_XML())
    suite.addTest (ProcesarDOC4_XML())
    return suite

def suitePDF():
    suite = unittest.TestSuite()
    suite.addTest (ProcesarDOC1_PDF())
    suite.addTest (ProcesarDOC2_PDF())
    suite.addTest (ProcesarDOC3_PDF())
    suite.addTest (ProcesarDOC4_PDF())
    return suite

def suiteIntegral():
    suite = unittest.TestSuite()
    suite.addTest (ProcesarOfertasPequena())
    return suite

if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run (suiteDOC())
    runner.run (suiteXLS())
    runner.run (suitePDF())
