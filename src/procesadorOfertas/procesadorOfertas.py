from procesadorXLS import procesarXLS
from procesadorDOC2CSV import procesarDOC
from procesadorPDF2CSV import procesarPDF
import sys
from os.path import splitext, isfile
from os import remove

if __name__ == '__main__':
    if isfile('ofertas.csv'):
        remove('ofertas.csv')
    if isfile('ListaDACE.csv'):
        remove('ListaDACE.csv')

    fdSalida = open('ofertas.csv', 'a')
    fdSalida.write("COD_ASIGNATURA,BLOQUE,LUNES,MARTES" + \
                        ",MIERCOLES,JUEVES,VIERNES\n")
    fdDace = open('ListaDACE.csv', 'a')
    nomArchivoDace = sys.argv[len(sys.argv) - 1]
    for archivo in sys.argv[1:]:

        # Selección de archivos para procesar
        ext = splitext(archivo)[1]
        if nomArchivoDace == archivo:
            fdSalida = fdDace

        if  ext == ".xml":
            #print("Aqui va un .DOC")
            procesarDOC(archivo, fdSalida)
        elif ext == ".pdf":
            #print("Aqui va un .PDF")
            procesarPDF(archivo, fdSalida)
        elif ext == ".xls" or ext == ".xlsx":
            #print("Aqui va un .XLS")
            procesarXLS(archivo, fdSalida)

    fdSalida.close()
    fdDace.close()
    print("\nOfertas procesadas exitosamente")



# arch1.xls arch2.pdf arch3.doc
# OfertaMatematicas.xls OfertaComputo.xml OfertaID.xlsx OfertaCE.xls OfertaSIG.pdf 0800DACE.xls