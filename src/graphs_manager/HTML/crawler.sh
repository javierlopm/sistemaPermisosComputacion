#!/bin/bash
for carnet in $1; do curl --data "uid=${carnet}" http://directorio.dst.usb.ve > ./HTML/$1.html;done


