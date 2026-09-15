Laboratorio 05 - Buenas prácticas pytest

El análisis del notebook 2_analisis_lab05.ipynb requiere de los archivos:
- patients.csv
- encounters.csv
- observations.csv
del dataset de Synthea: Specialized Data Set COVID-19 10k (link de descarga: https://synthea.mitre.org/downloads)

Notas:
- se usó pre-commit install, para configurar ruff, ruff-format y mypy en cada commit.
- se usaron dos ignores de mypy, dentro de visualising.py, líneas 119 y 127, para el método .agg() de pandas.
