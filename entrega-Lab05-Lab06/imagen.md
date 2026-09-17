1. Congelar las dependencias
Sobre el lockfile, algunas dependencias transitivas y su dependencia "base":
	- colorama 0.4.6, vía pytest
	- fonttools 4.65.0, vía matplotlib
	- pathspec 1.1.1, vía mypy
	- python-dateutil 2.9.0.post0, vía matplotlib, pandas
	- pluggy 1.6.0, vía pytest

2. y 3. El primer Dockerfile y su arreglo:
| Escenario | Orden malo | Orden bueno |
|-----------|------------|-------------|
| Build desde cero | 35.9s | 103.8s |
| Rebuild tras cambiar código | 35.4s | 5.3s |
| Rebuild tras cambiar dependencias | 43.4s | 5.0s |

4. y 5. Adelgazar la imagen y .dockerignore
| Escenario | Tamaño en MB (disk usage, content size) |
|-----------|--------|
| Original (base slim) | 858, 247 |
| agregar --no-cache-dir | 661, 155 |
| multi-stage build, creando primero un ambiente nuevo | 679, 159 |
| agregar .dockerignore | 678, 159 |
| remover cache de bytecode del ambiente virtual | 564, 131 |
| Base alpine | 490, 113 |

__Nota__: con la base alpine, sí alcancé a bajar de los 500 MB, pero al tener numpy y matplotlib, tuve que usar build-base y agregar "manualmente" algunas librerías como freetype y openblas que en la base slim no son necesarias. Esto supongo que en parte anula el propósito de usar la base slim, además de que fue el build más tardado de todos (355.7s)-

Sobre el tamaño del contexto:
Antes del dockerignore: 1.18kB
Despues del dockerignore: 677B

Archivos innecesarios que estaba arrastrando:
./src/clinlab.egg-info
./src/clinlab.egg-info/SOURCES.txt
./src/clinlab.egg-info/requires.txt
./src/clinlab.egg-info/PKG-INFO
./src/clinlab.egg-info/dependency_links.txt
./src/clinlab.egg-info/top_level.txt
./notebooks/2_analisis_lab05.ipynb

8. Escanear
Número de vulnerabilidades:
- Críticas: 5
- Altas: 10

Viendo el reporte de docker scout, puedo ver que las primeras 3 vulnerabilidades críticas (de hecho 4 críticas, 4 altas, 2 medias, 2 bajas y 2 inespecificadas) vienen de un mismo paquete: perl 5.40.1-6. También puedo ver que casi todas estas vulnerabilidades (excepto por una de las bajas) ya fueron corregidas en una versión más reciente de perl:

Affected range : <5.40.1-6+deb13u1
Fixed version  : 5.40.1-6+deb13u1.

Por lo tanto, para corregirlas, podría usar docker pull para extraer la versión mas reciente de mi base (en este caso python:3.12-slim) y ver si en ella se incluye una versión superior de perl que ya incluya los patches para esas vulnerabilidades. Si esto no llegara a funcionar, podría forzar la actualización con apt-get update y upgrade. Esto corregiría gran parte de las vulnerabilidades de la imagen.

9. Correr las pruebas dentro del contenedor
No me encontré con ninguna dependencia oculta de mi entorno local, mis 18 pruebas pasaron (ver Figuras06/). El único 'problema' que fue no se imprimio el color verde en la terminal, pero las pruebas en si no fallaron.