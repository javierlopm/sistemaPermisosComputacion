#!/bin/bash

function usoAyuda(){
    echo "Uso 1: procesadorOfertas -f nombre_archivo_salida -d nombre_archivo_dace"
    echo "-m archivo_materias_requeridas [-e nomDir ]"
    echo "Uso 2: procesadorOfertas -f nombre_archivo_salida -d nombre_archivo_dace"
    echo "-m archivo_materias_requeridas archivo1.pdf archivo2.xls ... archivoN"
    echo "Ayuda: procesadorOfertas -h"
    return
}

function pasajeParametros() {
    while getopts ":f:d:m:e:h" opt; do
      case $opt in
        f)
            nombreArchSalida=$OPTARG
        ;;
        e)
            caminoDirArchs=$OPTARG
        ;;
        d)
            nombreArchDace=$OPTARG
        ;;
        m)
            nomArchMaterias=$OPTARG
        ;;
        h)
            usoAyuda
            exit 0
        ;;
        \?)
            echo "Opcion Invalida: -$OPTARG" >&2
            exit 1
        ;;
        :)
            echo "Opcion -$OPTARG requiere un argumento." >&2
            exit 1
        ;;
        esac
    done

    # Verificar que los flags sean usados
    if [[ -z "$nombreArchDace" || -z "$nomArchMaterias" || -z "$nombreArchSalida" ]]; then
        echo "-d -m -f son parametros obligatorios" >&2
        exit 1
    fi

    # Comprobar que los nombres proporcionados en los flags esten en el directorio

    # Acceder a los operandos
    shift $((OPTIND-1))
    return
}

#Procesar la entrada estandar
pasajeParametros $@

# Preprocesar los DOCS para Flat XML de libreoffice
existe=$(exec ps -U $(whoami) | awk '/soffice/ {print $4}' | wc -l)
python_bin=$(whereis python3 | grep -oE '/usr\/bin\/python3[[:space:]]')
# Linea para obtener python 3.x
#$(whereis python3 | grep -oE '/usr\/bin\/python3(\.[[:digit:]])?[[:space:]]' | awk '{ print $1}')
if [[ $existe -eq 1 ]]; then
  echo "Libreoffice esta ejecutandose. Cierre el programa y vuelva a ejecutar" >&2
  exit 1
else
    listaInsumos=$(ls $caminoDirArchs | grep .doc)
    office=$(whereis soffice | awk '{print $2}')
    for arch in $listaInsumos; do
        $office --convert-to fodt "$caminoDirArchs$arch" --outdir "$caminoDirArchs" --headless 1> /dev/null
    done
    if [[ $? -eq 0 ]]; then
        echo "Ejecutando procesadorOfertas"
        if [[ -z $caminoDirArchs ]]; then
            echo "Archivos por argumentos"
            $python_bin procesadorOfertas.py -m $nomArchMaterias \
                -f $nombreArchSalida -d $nombreArchDace $@ && exit 0
            # Linea para debugging
            # $python_bin pruebas/pruebaShell.py -m $nomArchMaterias \
            #     -f $nombreArchSalida -d $nombreArchDace $@ && exit 0
            exit 1
        else
            echo "Directorio como argumento"
            $python_bin procesadorOfertas.py -m $nomArchMaterias \
                -f $nombreArchSalida -d $nombreArchDace \
                    --input-dir=$caminoDirArchs \
                    && exit 0
            # Linea para debugging
            # $python_bin pruebas/pruebaShell.py -m $nomArchMaterias \
            #     -f $nombreArchSalida -d $nombreArchDace \
            #         --input-dir=$caminoDirArchs \
            #         && exit 0
            exit 1
        fi
    else
        echo "No se pudo preprocesar los DOCS"
        exit 1
    fi
fi

#whereis python3 | grep -oE '/usr\/bin\/python3(\.[[:digit:]])?[[:space:]]'