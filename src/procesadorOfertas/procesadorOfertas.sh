#!/bin/bash

function usoAyuda(){
    echo "Uso: procesadorOfertas -f nombre_archivo_salida -d nombre_archivo_dace"
    echo "-m archivo_materias_requeridas [--dir-input=nomDir ]"
    echo "tarchivo1.pdf archivo2.xls ... archivoN"
    echo "procesadorOfertas -h"
    return
}

while getopts ":f:d:m:e:h" opt; do
  case $opt in
    f)
        nombreArchSalida=$OPTARG
        echo "-f was triggered, Parameter: $nombreArchSalida" >&2
    ;;  
    e)
        caminoDirArchs=$OPTARG
        echo "-e was triggered, Parameter: $caminoDirArchs" >&2
    ;;
    d)
        nombreArchDace=$OPTARG
        echo "-d was triggered, Parameter: $nombreArchDace" >&2
    ;;
    m)
        nomArchMaterias=$OPTARG
        echo "-m was triggered, Parameter: $nomArchMaterias" >&2
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

if [[ -z `$nombreArchDace` && -z "$nomArchMaterias" && -z "$nombreArchSalida" ]]; then
    echo "-d -m -f son parametros obligatorios"
    exit 1
fi

# Preprocesar los DOCS para XML de libreoffice
existe=$(exec ps -U daniel | awk '/soffice/ {print $4}' | wc -l)
python_bin=$(whereis python3)
if [[ $existe -eq 1 ]]; then
  echo "Libreoffice esta ejecutandose. Cierre el programa y vuelva a ejecutar"
  exit 1
else
    listaInsumos=$(ls $caminoDirArchs | grep .doc)
    office=$(whereis soffice | awk '{print $2}')
    for arch in $listaInsumos; do
        arch="$caminoDirArchs$arch"
        $office --convert-to xml "$arch" --outdir "$caminoDirArchs" --headless 1> /dev/null 
    done
    if [[ $? -eq 0 ]]; then
        echo "Ejecutando procesadorOfertas"
        # exec /usr/bin/python3.4 procesadorOfertas 
        #     -m $nomArchMaterias -f $nombreArchSalida -d $nombreArchDace --dir-input=$caminoDirArchs
    else
        echo "No se pudo preprocesar los DOCS"
    fi
fi