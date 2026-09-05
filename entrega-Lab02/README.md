Abrego Islas Iván
Laboratorio 02 - Python, estructuras, pandas

Para este laboratorio elegí trabajar con un dataset prearmado de Synthea: COVID-19 10k.
Link de descarga: https://synthea.mitre.org/downloads
Cita: Jason Walonoski, Mark Kramer, Joseph Nichols, Andre Quina, Chris Moesel, Dylan Hall, Carlton Duffett, Kudakwashe Dube, Thomas Gallagher, Scott McLachlan, Synthea: An approach, method, and software mechanism for generating synthetic patients and the synthetic electronic health care record, Journal of the American Medical Informatics Association, Volume 25, Issue 3, March 2018, Pages 230–238, https://doi.org/10.1093/jamia/ocx079

La primera parte del análisis corre en un notebook interactivo de python (analisis_pacientes.ipynb) y para reproducirlo es necesario contar con los siguientes archivos del dataset:
- encounters.csv
- patients.csv
- observations.csv

La segunda parte del análisis también corre en un notebook interactivo (analisis_pacientes_PySpark.ipynb) y para reproducirlo es necesario contar con el siguiente archivo, incluido en el repositorio:
- full.pkl

Tabla actividad 8:

| Herramienta | Lineas de codigo | Tiempo (s) | Memoria pico; incremento (MB) | Que costo mas |
|:-----------:|:----------------:|:----------:|:-----------------------------:|:-------------:|
| Pandas | 65 | 1.31 ± 121 ms | 867.41; 149.06 (%%memit) | La pregunta 4 (distribucion y pacientes con al menos 3 mediciones) consumio mas memoria |
| Polars | 63 | 0.456 ± 52.7 ms | 1516.76; 17.81 (%%memit) | La pregunta 3 (10 codigos mas frecuentes) consumio mas memoria, pero fue bastante menos que al hacerlo con pandas(15MB vs 82MB) |
| PySpark | 78 | 73 (individual, sumando lo que colab dice que tarda). 27.8 ± 637 ms (al correr las 4 en la misma celda, usando %%timeit)  | 2191.57; 0.05 (%%memit). 4.7(tracemalloc)  | La pregunta 2 (media y mediana de encuentros por paciente) consumio mas memoria |
