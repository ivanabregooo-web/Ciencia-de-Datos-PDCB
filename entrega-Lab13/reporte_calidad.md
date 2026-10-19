Para montar la base de datos:

Debido al bind mount usado cuando se hizo la conversion a OMOP-CDM (ver reporte_calidad.md de entrega-Lab12), unicamente es necesario volver a conectarse utilizando docker. En mi caso:

En terminal, en la misma ruta donde se encuentre el archivo .env con las credenciales:
	>docker run --rm --name my_postgres --env-file .env -p 5432:5432 -v "%cd%:/workspace" -v "C:\Users\IVAN\Documents\postgres_data:/var/lib/postgresql/data" -d postgres:15.4



1. ¿Que tipo de exposicion tienes?

| exposure_type | drug_type_concept_id | total_records |
|-----------------|----------------------|---------------|
| EHR prescription | 32838 | 551434 |
| EHR encounter record | 32827 | 146392 |

Mis datos son principalmente prescripciones y, en menor medida, administraciones (EHR encounter record). Implica que no puedo usar la mayor parte de mis datos (las prescripciones) ya que no puedo estar seguro de que el paciente efectivamente haya recogido y tomado el medicamente. Para llegar a conclusiones sobre exposicion validas, solo puedo usar los datos de encounter record, ya que estos implican que el medicamento fue dado al paciente durante el encuentro clinico.



2. Caracterizar DRUG_EXPOSURE:

De los 20 medicamentos mas administrados, varios corresponden al concept_class_id "CVX" (vacunas). Incluso de los que no corresponden a CVX, sino a "clinical drug", varios tienen un days_supply promedio de 0, indicando que son medicamentos de una sola exhibición. Esto tambien explicaria por que mas de la mitad de todos los medicamentos en la base de datos no tienen end_date o tienen end_date = start_date. Por otro lado, el porcentaje de filas con drug_concept_id = 0 es 0, indicando que la base de datos fue perfectamente mapeada. Sin embargo, estas consultas muestran que Synthea, o al menos de la manera que lo use para generar esta base de datos, tiene la capacidad para generar prescripciones en mayor medida, y encounter records en menor medida, que ademas corresponden en su mayoria a medicamentos de una sola exhibicion. Esto me lleva a la conclusion de que NO es una base apta para estudiar exposicion a medicamentos.



3. Buscar por ingrediente, no por producto:

Ingrediente usado: cisplatina

| search_method | unique_patients | total_records |
|---------------|-----------------|---------------|
| Exact match (ingredient only) | 0 | 0 |
| Hierarchy match (descendants) | 92 | 18328 |

Al usar unicamente el id del ingrediente, encontramos 0 pacientes expuestos. A diferencia de los 92 que encontramos al usar todos sus descendientes. Esto se debe a que el concept id del ingrediente unicamente se traduce como tal. Es decir, un medico no recetaria unicamente "cisplatina", sino que haria especificaciones sobre dosis, mL o algo parecido. Estas especificaciones resultan en concept_id distintos al de unicamente el ingrediente, los cuales tambien estamos capturando al incluir los descendientes del concept id original.



4. Construir DRUG_ERA a mano:

Ingrediente usado: cisplatina

A primera vista (viendo las primeras 20 filas de la tabla), las eras resultaron iguales (tanto en numero como en fechas). La unica diferencia esta en el era_id, el cual seguramente se va asignando conforme la conversion a OMOP va registrando los datos de todos los medicamentos, en vez de asignar un id personalizado cuyo conteo se inicializa en 1 como se hace en la solucion manual, pero no es relevante.


5. Adherencia: proporcion de dias cubiertos

PDC calculado para una ventana de un año y para el medicamento cisplatina 
|person_id|true_exposure_days|pdc_percentage|
|---------|------------------|--------------|
|5050|85|23.3|
|6021|81|22.2|
|636|76|20.8|
|1786|76|20.8|
|7065|75|20.5|

No calcule el porcentaje de pacientes con PDC mayor a 0.8 porque es 0. En la tabla muestro los 5 pacientes con el porcentaje mas alto de PDC y apenas alcanza 23%. Esto tiene sentido porque la cisplatina es un medicamento utilizado en quimioterapias. Viendo algunas fechas de exposicion, puedo darme cuenta que se trata de periodos de un dia, muy probablemente en un solo encuentro (que corresponderia a la quimioterapia). A un paciente, se le hace esta exposicion durante 3 o 4 dias consecutivos de un mes, y se suspende la exposicion. Aproximadamente un mes (pero a veces menos), se repite este patron, con exposicion de 3-4 dias consecutivos seguido de suspension. Asi se repite para cada mes. Este patron temporal tiene mucho sentido para una quimioterapia y explica los porcentajes de PDC tan bajos.
Por otro lado, el MPR (Medication Possession Ratio) se calcularia utilizando days_supply en vez de drug_exposure: (Sum of days supply for all fills in period / Number of days in period) x 100% (1). No lo use, pero es importante saber que el MPR puede inflar artificalmente la adherencia verdadera, ya que pacientes con tratamientos continuos podrian rellenar o volver a solicitar sus medicamentos antes de que se termine su periodo de suministro, provocando que haya days_supply sobrelapados que inflan el resultado. 

	- (1): https://www.pharmacytimes.com/view/do-you-know-the-difference-between-these-adherence-measures



6. Caracterizar MEASUREMENT

Unidades de analitos relacionados con leucocitos en sangre:

|analyte_name|unit_concept_id|unit_name|total_records|null_value_pct|censored_value_pct|
|------------|---------------|---------|-------------|
|Leukocytes [#/volume] in Blood by Automated count|8848|thousand per microliter|36311|0|0|
|Eosinophils/Leukocytes in Blood by Automated count|8554|percent|2452|0|0|
|Basophils/Leukocytes in Blood by Automated count|8554|percent|2452|0|0|
|Lymphocytes/Leukocytes in Blood by Automated count|8554|percent|2452|0|0|
|Monocytes/Leukocytes in Blood by Automated count|8554|percent|2452|0|0|
|Neutrophils/Leukocytes in Blood by Automated count|8554|percent|2452|0|0|
|Leukocytes (#/volume) in Blood|8848|thousand per microliter|31|0|0|

Aunque no fue el caso, encontrar una medida con un operador asociado implicaria que se esta trabajando con un umbral de algun tipo. E.g., una carga viral menor a 0.05. En ese ejemplo, dejar la medida como tal y sin considerar el operador implica que el valor numerico se manejaria como 0.05 lo cual seria incorrecto y podria alterar los resultados. Dependiendo de la pregunta que se este respondiendo, estos valores con operador deberian ser tratados de manera distinta. Yo les asignaria una etiqueta categorica indicando que son censurados, de manera que pueda omitirlos facilmente de las operaciones matematicas que considere necesarias.



7. Normalizar unidades

Como en mi base de datos no encontre un analito con mas de una unidad, simule unidades mixtas. Elegi al azar la mitad de las observaciones de conteo de leucocitos en sangre y modifique sencillamente sus unidades: pase de las originales que eran 1000 leucocitos/microlitro y las modifique a 1000 leucocitos/mililitro. Esto destruyo por completo el patron original de la distribucion (fig. 7, arriba) y se genero un nuevo patron con una distribucion bimodal debido a las unidades mixtas (fig. 7, en medio). Despues, normalice ambas observaciones (originales y corruptas) a unidades arbitrarias e intermedias entre ellas: 1000 leucocitos/500 microlitros, que es lo mismo que 1000 leucocitos/(0.5 mililitro). Esto permitio recuperar la forma original de la dsitribucion (fig. 7, abajo). El ejercicio demuestra como una base de datos con unidades mixtas no puede ser analizada directamente y se debe de buscar una normalizacion para que los valores sean comparables.

Factores de conversion:
Mili = Micro / 1000


8. Valores implausibles.

Rangos fisiologicos:

- a) Leucocitos en sangre: 4000-11000 / uL de sangre 
(https://psrihospital.com/leukocyte-count-a-comprehensive-guide-to-normal-levels-testing-methods-and-procedures/)

- b) Hemoglobina en sangre: 12-17 g / dL de sangre 
(https://www.cadabamsdiagnostics.com/blogs/how-much-hemoglobin-should-be-present-in-human-body)

- c) Plaquetas en sangre: 150k-450k / uL de sangre 
(https://my.clevelandclinic.org/health/diagnostics/21782-platelet-count)

| Analito | Valores totales | Valores plausibles | Valores implausibles | ¿Hay sentinelas? |
|---------|-----------------|--------------------|----------------------|------------------|
| Leucocitos en sangre | 36,311 | 29,412 | 6,899 | no |
| Hemoglobina en sangre | 36,429 | 30,348 | 6,081 | no |
| Plaquetas en sangre | 36,311 | 33,519 | 2,792 | no |



9. MEASUREMENT contra OBSERVATION

Tanto peso como frecuencia respiratoria quedaron en la tabla MEASUREMENT. Tabaquismo por otro lado, quedo en OBERSVATION. Esto va de acuerdo con las convenciones de dominio en THEMIS.



10. El ultimo valor antes del indice

|Pacientes diagnosticados con anemia|Pacientes anemicos y con valor basal de hemoglobina|
|-----------------------------------|---------------------------------------------------|
|                4044               |                        1234                       |

Esto reduce bastante la n de la cohorte.
