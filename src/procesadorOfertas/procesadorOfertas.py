from procesadorExcel import procesarXLS
from procesadorDOC2CSV import procesarDOC
from procesadorPDF2CSV import procesarPDF
import sys
from os.path import splitext, isfile
from os import remove

if __name__ == '__main__':
    if isfile('ofertas.csv'):
        remove('ofertas.csv')
    fdTempOfertas = open('ofertas.csv', 'a')
    fdTempOfertas.write("COD_ASIGNATURA,BLOQUE,LUNES,MARTES" + \
                        ",MIERCOLES,JUEVES,VIERNES\n")
    for archivo in sys.argv[1:]:
        ext = splitext(archivo)[1]
        if  ext == ".xml":
            #print("Aqui va un .DOC")
            procesarDOC(archivo, fdTempOfertas)
        elif ext == ".pdf":
            #print("Aqui va un .PDF")
            procesarPDF(archivo, fdTempOfertas)
        elif ext == ".xls":
            #print("Aqui va un .XLS")
            procesarXLS(archivo, fdTempOfertas)

    fdTempOfertas.close()
    print("\nOfertas procesadas exitosamente")



# arch1.xls arch2.pdf arch3.doc
# OfertaMatematicas.xls OfertaComputo.xml OfertaComp.pdf