Para este laboratorio elegí trabajar con el dataset de 10k pacientes de COVID-19. 
Link de descarga: https://synthea.mitre.org/downloads

Cita: Walonoski J, Klaus S, Granger E, Hall D, Gregorowicz A, Neyarapally G, Watson A, Eastman J. Synthea™ Novel coronavirus (COVID-19) model and synthetic data set. Intelligence-Based Medicine. 2020 Nov;1:100007. https://doi.org/10.1016/j.ibmed.2020.100007

El análisis se corre en un notebook interactivo de python (.ipynb) y para reproducirlo es necesario contar con lo siguientes archivos del dataset:
- observations.csv
- patients.csv
- encounters.csv

Y contar con las siguientes librerías instaladas:
- polars
- pyspark
- memory_profiler
