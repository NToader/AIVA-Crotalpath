# Crotalpath Backend
Crotalpath Backend es un sistema de reconocimiento automático de texto presente en
crotales por medio de técnicas de visión artificial.

## Instalación
El sistema ha sido programado en Python, por ello, serán necesarias las 
siguientes dependencias:
- Python 3.6 o superior
- Numpy 1.15.4 o superior

## Ejecución
Para utilizar el sistema basta con invocarlo desde un terminal proporcionando 
una serie de imágenes o una carpeta de imágenes. 
Para procesar una carpeta con imágenes se debe utilizar la opción ```-f``` 
mientras que para una o varias imágenes, la opción ```-i```.

Algunos ejemplos:
```
python predictor.py -i 0002.TIF
```
```
python predictor.py -i 0001.TIF 0002.TIF 0003.TIF
```
```
python predictor.py -f ../../CrotalesTest/TestSamples
```

## Test
Para la ejecución de las pruebas unitarias del sistema es necesario disponer de 
una estructura de directorios tal y como se propone a continuación:
```
│
├── AIVA-Crotalpath/
│   └── ...
├── CrotalesTest/
│   ├── TestSamples/
│   │   ├── 0001.TIF
│   │   ├── 0002.TIF
│   │   └── 0003.TIF
│   └── GroundTruth.ods
```
Donde ```CrotalesTest``` es un directorio situado al mismo nivel jerárquico 
con ```AIVA-Crotalpath``` (el presente repositorio). El directorio ```CrotalesTest```
deberá contener como mínimo el directorio ```TestSamples```. 
A su vez ```TestSamples```deberá contener como mínimo los ficheros 
```0001.TIF```, ```0002.TIF``` y ```0003.TIF```.

Para la ejecución de los test hay que ejecutar la siguiente línea desde la raíz
de la carpeta de este repositorio:
``` 
python -m unittest discover -v ./crotalpath_backend/tests/
```
