# Crotalpath
Crotalpath es un sistema destinado a complementar la trazabilidad del ganado,
aportada por los crotales, mediante visión artificial. Este sistema está dividido
en dos módulos: Crotalpath Core, el algoritmo de visión, y Crotalpath WebApp, la aplicación web, para 
realizar consultas.


## Instalación

### Dependencias de cada sistema operativo
Para la correcta ejecución del sistema son necesarias las siguientes dependencias específicas para cada sistema 
operativo:
- Python 3.7 (su instalación depende del sistema operativo, consultar https://www.python.org/downloads/)
- Tesseract 4.0 (su instalación depende del sistema operativo, consultar 
https://github.com/tesseract-ocr/tesseract/wiki#installation, en la versión actual existe un bug por el cual el paquete 
de idioma no será correctamente instalado en Windows y Mac)
- Git (consultar https://gist.github.com/derhuerst/1b15ff4652a867391f03)

### Descarga del sistema e instalación de dependencias de Python (comunes a todos los sistema operativos)
Una vez resueltas las dependencias anteriores, para descargar el sistema se debe ejecutar:

```
git clone https://github.com/NToader/AIVA-Crotalpath.git
```

Entramos en el directorio generado
```
cd AIVA-Crotalpath
```

Los paquetes de Python necesarios se deben instalar de la siguiente manera:

```
pip install -r requirements.txt
```

Con esto habría finalizado la instalación y ya se podría usar el sistema.

## Ejecución
Para utilizar el sistema basta con invocarlo desde un terminal proporcionando 
una serie de imágenes o una carpeta de imágenes. 
Para procesar una carpeta con imágenes se debe utilizar la opción ```-f``` 
mientras que para una o varias imágenes, la opción ```-i```. Para mostrar el resultado de cada reconocimiento
en una ventana de OpenCV se debe indicar el parámetro ``-d`` y para establecer la ruta donde almacenar el resultado
se debe usar el parámetro ``-o``. Finalmente, para determinar el tipo de reconocedor a usar se debe utilizar el flag
``-t`` seguido por un número. Actualmente el único reconocedor disponible es el Bovino, identificado como ``1``.

### Algunos ejemplos (ejecutar desde la raíz del repositorio):
Reconocimiento de una imagen de un crotal bovino y muestra del resultado
```
python -m crotalpath_core -t 1 -i crotalpath_core/tests/dataset/TestSamples/0001.TIF -o ./res.json  -d 
```

Reconocimiento de una imagen de un crotal bovino sin mostrar el resultado
```
python -m crotalpath_core -t 1 -i crotalpath_core/tests/dataset/TestSamples/0001.TIF -o ./res.json
```


Reconocimiento de varios crotales
```
python -m crotalpath_core -t 1 -i crotalpath_core/tests/dataset/TestSamples/0001.TIF crotalpath_core/tests/dataset/TestSamples/0002.TIF crotalpath_core/tests/dataset/TestSamples/0003.TIF -o ./res.json 
```

Reconocimiento de todos los crotales presentes en un directorio (5 crotales)
```
python -m crotalpath_core -t 1 -f=crotalpath_core/tests/dataset/TestSamples5/ -o ./res.json
```

## Test
Para la ejecución de los test hay que ejecutar la siguiente línea desde la raíz
de la carpeta de este repositorio:
``` 
python -m unittest discover -v crotalpath_core
```

# Despliegue con Docker

Para realizar el despliegue mediante Docker se debe instalar este programa,
para ello consultar el siguiente enlace: https://www.docker.com/get-started

## Linux
### Instalación 
Para instalar el sistema mediante Docker se deberá utilizar el siguiente comando desde la raíz del repositorio:
```
bash build.sh
```
### Ejecución
Para ejecutar el contenedor Docker y, con ello, el sistema Crotalpath se debe ejecutar el 
sigueinte comando:
```
bash start.sh
```
Una vez iniciado el contenedor Docker hay que navegar a la siguiente dirección para usar el sistema: 
http://127.0.0.1:5000/index.html



Para detener el servicio hay que ejecutar:
```
bash stop.sh
```


## Windows
### Instalación 
Para instalar el sistema mediante Docker se deberá utilizar el siguiente comando desde la raíz del repositorio:
```
build.bat
```
### Ejecución
Para ejecutar el contenedor Docker y, con ello, el sistema Crotalpath se debe ejecutar el 
siguiente comando:
```
start.bat
```
Una vez iniciado el contenedor Docker hay que navegar a la siguiente dirección para usar el sistema: 
http://127.0.0.1:5000/index.html


Para detener el servicio hay que ejecutar:
```
stop.bat
```