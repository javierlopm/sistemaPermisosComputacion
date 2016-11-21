# Introducción
(Dejar para el final)

# Resumen
(Dejar para el final)

# Planteamiento del problema

Trimestralmente, la coordinación de ingenieria de la computación prepara las ofertas de materias de acuerdo al pensum vigente para los posteriores trimestres.

A fin de entregar un documento público con dichas materias, la coordinadora debe examinar las ofertas de los distintos departamentos cuyas materias se encuentran en el pensum. Las ofertas departamentales se presentan bajo diferentes formatos y archivos como PDF, DOC, XLS (Excel), XLSX.

Estas ofertas consisten de renglones de código de asignatura, bloque y horario. Cada renglón debe ser examinado contra un borrador de ofertas que la coordinación dispone: agregar, eliminar o modificar cada caso. Luego de etse examen, se produce una oferta que envia a DACE. No obstante, esta la oferta producida no se da por terminada ya que esta sujeta a varias revisiones conforme DACE la revise. Esto significa que el proceso anteriormente descrito se repita hasta que no hayan nuevas versiones.

Este proceso es realizado a manualmente por la coordinación. Por otra parte, es propenso a errores debido a la cantidad de información que se maneja.


# Objetivos del miniproyecto
* Implementación una aplicación que permita la integración de los horarios de las asignaturas enviados por los distintos departamentos.

* Analizar, modificar e integrar ofertas provenientes de los diferentes departamentos que ofertan materias a la coordinación de ingeniería de la computación.

* Facilitar y automatizar la gestión de los horarios en los trámites académicos de la coordinación.


# Análisis

El flujo de trabajo del procesador de horarios es similar al proceso expuesto en el planteamiento del problema. Es modelado por lo siguientes etapas en el orden descrito a continuación:

    * Ofertas departamentales y oferta 0800
    * Análisis y comparación
    * Emisión preliminar de materias a DACE
    * Análisis y comparación con nueva oferta de DACE
    * Generación de oferta trimestral.





(imagen del flujo de trabajo en la expo)

Ofertas departamentales:  en cada trimestre, los departamentos entregan las ofertas de asignaturas en archivos con formatos diversos. Los formatos más comunes son: XLS (Excel), XLSX, PDF y DOC. Estas ofertas son generales, es decir, cada coordinación de carrera extrae y analiza la información relevante a su dominio. Todos las archivos departamentales se utilzan como insumo para generar una primera oferta.

El formato de presentación de las asignaturas varia en cada departamento. Existen 2 formatos comunes, aunque no necesariamente en el orden descrito. He aqui los siguientes:

* Código, Nombre Asignatura, Bloque, Lunes, Martes, Miercoles, Jueves, Viernes, Carrera
* Códigos, Asignaturas, horarios.

Oferta 0800: Archivo contra el cual se comparan las ofertas de los departamentos. Suele estar en formato XLS (Excel). Este archivo es el primer insumo requerido para generar una primera oferta.

El formato del archivo es el siguiente y sigue el orden descrito:
* Código, Bloque, Lunes, Martes, Miercoles, Jueves, Viernes, Oferta Especial, Carrera, Operación.

En ambas etapas se extraen las materias que sean pertinentes a la coordinación de ingenieria de la computación por medio de un archivo de texto donde se enuncian los códigos de las asignaturas.

Análisis y comparación: Las ofertas departamentales y la 0800 son analizadas y comparadas bajo ciertas reglas y se genera una oferta preliminar. Basta decir, que la comparación consiste eliminar y agregar asignaturas, y modificar el horario en el caso que haya discrepancias.

Emisión preliminar de materias a DACE: el resultado es un archivo en formato CSV (siglas en inglés, comma-separated value) bajo el siguiente orden:

* Código, Bloque, Lunes, Martes, Miercoles, Jueves, Viernes, Especial

Análisis y comparación con nueva oferta de DACE:  Una vez que se haya producido una primera oferta, se debe reanalizar y comparar contra la oferta general de DACE. Tal documento se reproduce en formato PDF donde se encuentra, para cada carrera de la universidad, sus asignaturas para el trimestre posterior. La comparación, nuevamente, consiste eliminar y agregar asignaturas, y modificar el horario en el caso que haya discrepancias.

Generación de oferta trimestral: para esta etapa se genera un borrador de materias para entregar a DACE. No obstante, esta sujeto a cambios mientras haya revisiones de la oferta general de DACE. Esto significa que, el producto de esta etapa debe volver a pasar por la etapa anterior; generar una nueva oferta hasta que no hayan nuevas revisiones.

El formato de esta etapa será en CSV con la siguiente presentación:

* Código, Bloque, Lunes, Martes, Miercoles, Jueves, Viernes, Oferta Especial, Carrera, Operación.

Estas etapas se representa en 2 procesos  separados similares al planteamiento del problema: emisión preeliminar de materias de DACE y generación de oferta trimestral. La emisión preliminar de materias a DACE requiere de las ofertas departamentales y una oferta 0800. La generación de oferta trimestral, que es la etapa fina, su insumo es el resultado de la emisión preeliminar de materias. En la figura se puede observar el proceso.

(Imagen de procesos separados)


## Especificación de reglas

En los archivos de salida de cada etapa, una fila x consiste en

x = (cod1,bloque1,horarios,especial,carrera,operacion)

donde
    horarios: son las posiciones de los dias en el siguientes orden:
        Lunes, Martes, Miercoles, jueves, viernes. En tales espacios son los
        horas.

    operación: los valores son M(modificado), E(eliminar) , I(insertar) o
        vacio (en el archivo puede verse que no hay datos en tal campo).

Las reglas de comparación se aplican a todos los campos de la fila x salvo en carrera y operación.
En el, se anotan el resultado de aplicar alguna regla.

Para la primera etapa, existen 3 reglas de comparación:

Sea A un archivo de ofertas de DACE y B cada una de las ofertas departamentales.
    * Si fila de A y B son iguales en sus campos, el resultado es vacio. En caso contrario, se escribe la fila de A como resultado, el resultado es M.
    * Si una fila de A no existe en B, su operación es E. Se escribe en el archivo final.
    * Si una fila de B no existe en A, su operación es I. Se escribe en el archivo final.

Para la segunda etapa, existen 3 reglas de comparación y se apoyan en los resultados de la primera etapa:

Sea A un archivo CSV de la primera etapa y B un archivo de ofertas general de DACE.
    * Si una fila de A con operación M, es no igual en sus campos a una de B, se escribe la fila de A.
    * Si una fila de A con operación E, no existe en B, se escribe la fila de B.
    * Si una fila de A con operación es I, no existe en B, se escribe la fila de A.

# Diseño

La implantación del procesador de horarios fue implementada usando el lenguaje de programación Python versión 3.4. Sin embargo, no existe compatibilidad en versiones posteriores.

Las dependencias externas a la biblioteca estandar de Python son las siguientes:
    * Libreoffice
    * PyMupdf
    * xlrd


## Arquitectura

El procesador de horarios consta 6 modulos. Tres módulos se encargan de la lectura de las ofertas departamentales a saber: procesadorDOC, procesadorXLS, procesadorPDF. El procesadorDACE espera un archivo PDF que contenga el formato que se observa en la imagen de abajo. El módulo de funcionesAuxiliares contiene funciones de apoyo a los procesadores anteriores. procesadorOfertas es el programa principal y donde reside la lógica del sistema. El script procesadorOfertas.sh se utiliza para abstraer detalles de ejecución, detectar errores y automatizar la conversión de archivos DOC a XML.

(Imagen del formato de DACE)

(Imagen de la arquitectura)

Dado que se debe discriminar que materias son de interés para la coordinación de ingeniería de la Computación. se dispone de un archivo de texto plano para cargar los códigos de materias. Puede tener comentarios para ayudar a clasificar las materia del pensum.

## Ejecución

El procesador de horarios se ejecuta utilizando linea de comando, a través del interprete de Python o haciendo uso del script para sistemas tipo Unix. Se recomienda usar el script por las razones expuestas.

## Pseudocódigos

El procesadorPDF procesa un archivo PDF de la siguiente manera:
    1) Convertir el archivo PDF en XML usando Pymupdf
    2) Procesar XML


El procesadorDOC procesa un archivo FODT, producto de una función de libreoffice.
    1) Leer el archivo FODT.
    2) Reconocer códigos de materias, bloques y horarios.
    3) Componer una lista de un codigo de materia, bloque y sus horarios respectivos.
    4) Si en una lista donde su codigo de materia no encuentra en una lista de materias requeridas, eliminar.
        En caso contrario, almanecar en una lista.
    5) Transformar la lista de ofertas en una lista en formato CSV.

El procesadorXLS procesa un archivo XLS mediante la dependencia xlrd.
    1) Leer el archivo XLS.
    2)





Para generar una primera oferta trimestral, esto es, la primera etapa:
    1) Leer y cargar el archivo de materias requeridas.
    2) Procesar los insumos de acuerdo a procesadores respectivos.
    3) Comparar entre la lista de ofertas de departamentos y una lista de DACE
        de acuerdo al primer conjunto de reglas.
    4) Escribir los resultados en formato CSV.

Para generar ofertas trimestrales contra un listado de DACE, esto es, la segunda etapa:
    1) Leer y cargar primera oferta trimestral.
    2) Leer y cargar listado de dace desde un archivo pdf
    3) Comparar entre la lista de ofertas de departamentos y una lista de DACE
        de acuerdo al segundo conjunto de reglas.
    4) Escribir los resultados en formato CSV.

Agregar pseudo algoritmos
```
ejemplo1.pseudo()
si furula:
    vamo_a_programá()
```

~~~~~~~~~~~~~~~~~~~~~~ {#mycode .py .numberLines startFrom="61"}
print("Ejemplo de código con sintaxis de python")
~~~~~~~~~~~~~~~~~~~~~~

## Arquitectura
(Plataforma ????)

## Plan de pruebas y resultados
(Describir el an y resultados de ejecución)

# Conclusión
(Dejar para el final)

# Bibliografía
(Dejar para el final)
