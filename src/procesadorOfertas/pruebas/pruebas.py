import unittest
import os
import sys
sys.path.insert(0, os.path.abspath('..'))

from procesadorOfertas import procesarDOC, procesarDACE, procesarPDF, procesarXLS, \
                                generarOferta, cargarOfertas, imprimirResultados, \
                                cargarOfertasCSV
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
            [   ["PB5611","A",'','','','','','Y'], \
                ["PB5671",'A',"7-8","","7-8","2-3","",'']
            ]
        self.Correcta_doc2 = \
            [
                ["PB5611","A","","","","5-7","",''],
                ["PB5611","B","","3-4","","3-4","",''],
                ["PB5611","C","","","","","5-6",''],
                ["PB5671","A","7-8","","7-8","2-3","",''],
                ["CO5212","A","3-4","","3-4","","",''],
                ["CO5212","D","","4","","","",''],
            ]
        self.Correcta_doc3 = \
            [
                ["CO3211","C","","3-4","3-4","3-4","",''],
                ["CO3211","F","3-4","5-6","3-4","","",''],
                ["CO3121","A","","1-2","5-6","","1-2",''],
                ["CO3121","B","3-4","","3-4","","5-6",''],
                ["CO3321","G","3-4","","3-4","","5-6",''],
                ["CO3321","H","5-6","","5-6","","7-8",''],
                ["CO3411","A","7-8","","7-8","5-7","",''],
                ["CO5212","A","","5-6","","5-6","",''],
                ["CO5213","A","5-6","","5-6","","",''],
                ["CO5412","A","3-4","","3-4","","",''],
                ["CO6531","A","","3-4","","3-4","",''],
                ["CO6612","A","","5-6","","5-6","",''],
            ]
        self.Correcta_doc4 = \
            [
                ["CO3211","C","","3-4","3-4","3-4","",''],
                ["CO3211","F","3-4","5-6","3-4","","",''],
                ["CO3121","A","","1-2","","1-2","5-6",''],
                ["CO3121","B","","","3-4","5-6","3-4",''],
                ["CO3321","G","3-4","","3-4","","5-6",''],
                ["CO3321","H","5-6","","7-8","","5-6",''],
                ["CO3411","A","5-7","7-8","7-8","","",''],
                ["CO5212","A","","5-6","","5-6","",''],
                ["CO5213","A","5-6","","5-6","","",''],
                ["CO5412","A","3-4","","3-4","","",''],
                ["CO6531","A","","3-4","","3-4","",''],
                ["CO6612","A","","5-6","","5-6","",''],
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
        self.fdSalida = []
        procesarPDF(self.carpetaBase + "doc11.pdf",self.listaMaterias, self.fdSalida)
        self.assertEqual(self.fdSalida, self.Correcta_doc1, "Falla de procesamiento PDF. Archivo doc11.pdf")

class ProcesarDOC2_PDF (Contexto):
    def runTest (self):
        """ Prueba de procesamiento sobre doc2.pdf """
        procesarPDF(self.carpetaBase +  "doc2.pdf",self.listaMaterias, self.fdSalida)
        self.assertEqual(self.fdSalida, self.Correcta_doc2, "Falla de procesamiento PDF. Archivo doc2.pdf")
        self.fdSalida = []
        procesarPDF(self.carpetaBase + "doc21.pdf",self.listaMaterias, self.fdSalida)
        self.assertEqual(self.fdSalida, self.Correcta_doc2, "Falla de procesamiento PDF. Archivo doc21.pdf")

class ProcesarDOC3_PDF (Contexto):
    def runTest (self):
        """ Prueba de procesamiento sobre doc3.pdf """
        procesarPDF(self.carpetaBase + "doc3.pdf",self.listaMaterias, self.fdSalida)
        self.assertEqual(self.fdSalida, self.Correcta_doc3, "Falla de procesamiento PDF. Archivo doc3.pdf")
        self.fdSalida = []
        procesarPDF(self.carpetaBase + "doc31.pdf",self.listaMaterias, self.fdSalida)
        self.assertEqual(self.fdSalida, self.Correcta_doc3, "Falla de procesamiento PDF. Archivo doc31.pdf")

class ProcesarDOC4_PDF (Contexto):
    def runTest (self):
        """ Prueba de procesamiento sobre doc4.pdf """
        procesarPDF(self.carpetaBase + "doc4.pdf",self.listaMaterias, self.fdSalida)
        self.assertEqual(self.fdSalida, self.Correcta_doc4, "Falla de procesamiento PDF. Archivo doc4.pdf")
        self.fdSalida = []
        procesarPDF(self.carpetaBase + "doc41.pdf",self.listaMaterias, self.fdSalida)
        self.assertEqual(self.fdSalida, self.Correcta_doc4, "Falla de procesamiento PDF. Archivo doc41.pdf")

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



class ContextoDatosReales(unittest.TestCase):
    """docstring for CargaDace"""
    def setUp(self):
        self.carpetaBase = "pruebas_integrales/"
        self.carpetaRespuestas = "res_pruebas_procesamiento/"
        self.CarpetaDACE = "pruebas_procesamiento/datos_reales/"
        #self.listaMaterias = cargarMaterias("../materiasRequeridas.txt")
        self.listaMaterias = []
        for materia in open("../materiasRequeridas.txt", 'r'):
            if (not materia.isspace()) and materia[0] != '#':
                self.listaMaterias.append(materia.rstrip(' \t\n\r'))


class XLS_datosReales_CE(ContextoDatosReales):
    """docstring for Prueba"""
    def runTest(self):
        fdSalida = []
        respuesta = cargarOfertasCSV(self.carpetaRespuestas + "oferta1_resCE.csv", 7)
        procesarXLS(self.carpetaBase + "ofertas1/OfertaCE.xls", True, self.listaMaterias, fdSalida)
        self.assertEqual(fdSalida, respuesta, "Falla de procesamiento XLS. Archivo ofertas1/OfertaCE.xls")

class XLS_datosReales_ID(ContextoDatosReales):
    """docstring for Prueba"""
    def runTest(self):
        fdSalida = []
        respuesta = cargarOfertasCSV(self.carpetaRespuestas + "oferta1_resID.csv", 7)
        procesarXLS(self.carpetaBase + "ofertas1/OfertaID.xlsx", True, self.listaMaterias, fdSalida)
        self.assertEqual(fdSalida, respuesta, "Falla de procesamiento XLS. Archivo ofertas1/OfertaID.xlsx")

class XLS_datosReales_MAT(ContextoDatosReales):
    """docstring for Prueba"""
    def runTest(self):
        fdSalida = []
        respuesta = cargarOfertasCSV(self.carpetaRespuestas + "oferta1_resMAT.csv", 7)
        procesarXLS(self.carpetaBase + "ofertas1/OfertaMatematicas.xls", True, self.listaMaterias, fdSalida)
        self.assertEqual(fdSalida, respuesta, "Falla de procesamiento XLS. Archivo ofertas1/OfertaMatematicas.xls")

class XLS_datosReales_0800(ContextoDatosReales):
    """docstring for Prueba"""
    def runTest(self):
        fdSalida = []
        respuesta = cargarOfertasCSV(self.carpetaRespuestas + "oferta1_res0800.csv", 7)
        procesarXLS(self.carpetaBase + "ofertas1/0800.xls", False, self.listaMaterias, fdSalida)
        self.assertEqual(fdSalida, respuesta, "Falla de procesamiento XLS. Archivo ofertas1/0800.xls")

class PDF_datosReales_SIG(ContextoDatosReales):
    """docstring for Prueba"""
    def runTest(self):
        fdSalida = []
        respuesta = cargarOfertasCSV(self.carpetaRespuestas + "oferta1_resSIG.csv", 7)
        procesarPDF(self.carpetaBase + "ofertas1/OfertaSIG.pdf", self.listaMaterias, fdSalida)
        self.assertEqual(fdSalida, respuesta, "Falla de procesamiento PDF. Archivo ofertas1/OfertaSIG.pdf")

class FODT_datosReales_Computo(ContextoDatosReales):
    """docstring for Prueba"""
    def runTest(self):
        fdSalida = []
        respuesta = cargarOfertasCSV(self.carpetaRespuestas + "oferta1_resComputo.csv", 7)
        procesarDOC(self.carpetaBase + "ofertas1/OfertaComputo.fodt", self.listaMaterias, fdSalida)
        self.assertEqual(fdSalida, respuesta, "Falla de procesamiento DOC. Archivo ofertas1/OfertaComputo.fodt")

class FODT_datosReales_PB(ContextoDatosReales):
    """docstring for Prueba"""
    def runTest(self):
        fdSalida = []
        respuesta = cargarOfertasCSV(self.carpetaRespuestas + "oferta1_resPB.csv", 7)
        procesarDOC(self.carpetaBase + "ofertas1/OfertaPB.fodt", self.listaMaterias, fdSalida)
        self.assertEqual(fdSalida, respuesta, "Falla de procesamiento DOC. Archivo ofertas1/OfertaPB.fodt")


class procesamiento_DACE_EM2017_v1(ContextoDatosReales):
    """docstring for procesamiento_DACE_EM2017_v1"""
    def runTest(self):
        fdSalida = []
        respuesta = cargarOfertasCSV(self.carpetaRespuestas + "resDACE_EM2017_v1.csv", 7)
        procesarDACE("0800", "../Oferta_DACE_EN2017_v1.pdf", fdSalida)
        self.assertEqual(fdSalida, respuesta, "Falla de procesamiento PDF DACE. Archivo Oferta_DACE_EN2017_v1.pdf")

class procesamiento_DACE_EM2017_v2(ContextoDatosReales):
    """docstring for procesamiento_DACE_EM2017_v2"""
    def runTest(self):
        fdSalida = []
        respuesta = cargarOfertasCSV(self.carpetaRespuestas + "resDACE_EM2017_v2.csv", 7)
        procesarDACE("0800","../Oferta_DACE_EN2017_v2.pdf", fdSalida)
        self.assertEqual(fdSalida, respuesta, "Falla de procesamiento PDF DACE. Archivo Oferta_DACE_EN2017_v2.pdf")

class procesamiento_DACE_EM2017_v3(ContextoDatosReales):
    """docstring for procesamiento_DACE_EM2017_v3"""
    def runTest(self):
        fdSalida = []
        respuesta = cargarOfertasCSV(self.carpetaRespuestas + "resDACE_EM2017_v3.csv", 7)
        procesarDACE("0800","../Oferta_DACE_EN2017_v3.pdf", fdSalida)
        self.assertEqual(fdSalida, respuesta, "Falla de procesamiento PDF DACE. Archivo Oferta_DACE_EN2017_v3.pdf")

class procesamiento_DACE_SD2016(ContextoDatosReales):
    """docstring for procesamiento_DACE_SD2016"""
    def runTest(self):
        fdSalida = []
        respuesta = cargarOfertasCSV(self.carpetaRespuestas + "resDACE_SD2016.csv", 7)
        procesarDACE("0800",self.CarpetaDACE + "Oferta_DACE_SD2016.pdf", fdSalida)
        self.assertEqual(fdSalida, respuesta, "Falla de procesamiento PDF DACE. Archivo Oferta_DACE_SD2016.pdf")
        



#
# Pruebas integrales
#

class ContextoIntegral(unittest.TestCase):
    def setUp(self):
        self.listaMaterias = []
        for materia in open("../materiasRequeridas.txt", 'r'):
            if (not materia.isspace()) and materia[0] != '#':
                self.listaMaterias.append(materia.rstrip(' \t\n\r'))

        self.carpetaRespuestas = "res_pruebas_procesamiento/"
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
        self.listaArchivos = ["doc1.pdf","doc1.xls","doc1.xml","0800_prueba1.xls"]

        (self.listaOfertas, self.listaDACE) = cargarOfertas( \
                        self.listaArchivos,"pruebas_integrales",
                        self.listaMaterias,True,"0800_prueba1.xls")
        #imprimirResultados("Resultado", self.fdSalida)
        self.assertEqual(self.fdSalida, self.Correcta1, "Falla integral. Archivo 0800_prueba1.xls")

class Oferta_V1(ContextoIntegral):
    """docstring for Oferta_V1"""
    def runTest(self):
        respuesta = cargarOfertasCSV(self.carpetaRespuestas + "ofertas1_integral_v1.csv", 9)
        listaArchivos = ['0800.xls','OfertaCE.xls','OfertaComputo.fodt',
        'OfertaID.xlsx', 'OfertaMatematicas.xls','OfertaPB.fodt', 'OfertaSIG.pdf'
            ]

        listaOfertas = []
        listaDACE = []
        try:
            (listaOfertas, listaDACE) = cargarOfertas(
                            listaArchivos,"pruebas_integrales/ofertas1",
                            self.listaMaterias,True,"0800.xls")
            fdSalida = generarOferta(listaOfertas, listaDACE)
        except Vacio_Error as ve:
            print("Falta información en: ", ve)
            print("Revise el formato y datos de los archivos fuentes")
            print("Abortar")
            sys.exit(2)
        except FileNotFoundError:
            print("El archivo no encontrado", nomArchivoMaterias)
            sys.exit(2)
        except IsADirectoryError:
            print(nomArchivoMaterias ,"es un directorio. Se requiere un archivo")
            sys.exit(2)
        except UnicodeDecodeError:
            print("Archivo no codificado para UTF-8. Recodifique.")
            sys.exit(2)
        else:
            self.assertEqual(fdSalida, respuesta, "Falla integral ofertas1.")




def suiteXLS():
    suite = unittest.TestSuite()
    suite.addTest (ProcesarDOC1_XLS())
    suite.addTest (ProcesarDOC2_XLS())
    suite.addTest (ProcesarDOC3_XLS())
    suite.addTest (ProcesarDOC4_XLS())
    return suite

def suiteXLS_datosReales():
    suite = unittest.TestSuite()
    suite.addTest (XLS_datosReales_CE())
    suite.addTest (XLS_datosReales_ID())
    suite.addTest (XLS_datosReales_MAT())
    suite.addTest (XLS_datosReales_0800())
    return suite

def suiteDOC():
    suite = unittest.TestSuite()
    suite.addTest (ProcesarDOC1_XML())
    suite.addTest (ProcesarDOC2_XML())
    suite.addTest (ProcesarDOC3_XML())
    suite.addTest (ProcesarDOC4_XML())
    return suite

def suiteDOC_datosReales():
    suite = unittest.TestSuite()
    suite.addTest (FODT_datosReales_Computo())
    suite.addTest (FODT_datosReales_PB())
    return suite

def suitePDF_datosReales():
    suite = unittest.TestSuite()
    suite.addTest (PDF_datosReales_SIG())
    return suite

def suiteDACE():
    suite = unittest.TestSuite()
    suite.addTest (procesamiento_DACE_SD2016())
    suite.addTest (procesamiento_DACE_EM2017_v1())
    suite.addTest (procesamiento_DACE_EM2017_v2())
    suite.addTest (procesamiento_DACE_EM2017_v3())
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
    #suite.addTest (ProcesarOfertasPequena())
    suite.addTest (Oferta_V1())
    return suite

if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    # runner.run (suiteDOC())
    # runner.run (suiteXLS())
    #runner.run (suitePDF())
    runner.run (suiteDACE())
    # runner.run (suiteXLS_datosReales())
    # runner.run (suiteDOC_datosReales())
    # runner.run (suitePDF_datosReales())
    #runner.run (suiteIntegral())
