import unittest
#from ..procesadorOfertas.procesadorDOC2CSV import procesarDOC



class ProcesarDOCS (unittest.TestCase):
    def setUp (self):
        print("Setting up ArithTest cases")
        self.caminoArchivoEntrada = "doc1.xml"
        self.listaMaterias = "materiasRequeridasPrueba.txt"
        self.fdSalida = []
        # Respuesta correcta
        self.Correcta_doc1 = \
            [   ["PB5611","A"], \
                ["PB5671",'A',"7-8","","7-8","2-3",""]
            ]

    def runTest (self):
        """ Test addition and succeed. """
        #procesarDOC(caminoArchivoEntrada,listaMaterias,fdSalida):
        self.fdSalida = procesarDOC(self.caminoArchivoEntrada,self.listaMaterias, self.fdSalida)
        self.assertEqual(self.fdSalida[1:], self.Correcta_doc1, "Falla de procesamiento DOC. Archivo doc1.xml")

def suite():
    suite = unittest.TestSuite()
    suite.addTest (ProcesarDOCS())
    return suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    test_suite = suite()
    runner.run (test_suite)