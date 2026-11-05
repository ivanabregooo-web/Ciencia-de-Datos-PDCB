1. Los tres conteos

	a) ¿cuantos pacientes entraron?: 42
	b) ¿cuanto seguimiento tienen despues del indice: mediana = 30, q25 = 30, q75 = 179.5
	c) ¿cuantas veces ocurre el desenlace que te interesa en ese seguimiento?: quedandome con una variable fisiologica, frecuencia cardiaca, encuentro 53 mediciones en total.

¿Este estudio es factible con estos datos?:
	No. De entrada me interesaba comparar variables fisiologicas en una cohorte con monoterapia vs una cohorte con politerapia de Medicamentos Anti Epilepticos (MAE). De entrada la condicion epileptica no fue la eleccion ideal porque incluso antes de los criterios de inclusion/exclusion de la cohorte, me quede con pocos pacientes (aprox 200 de los ~11k pacientes totales de la base de datos). Ahora, viendo la cantidad de mediciones para los analitos mas comunmente medidos, veo que no conservamos suficiente informacion como para resolver la pregunta.
	Tomando esto en cuenta, considero apropiado cambiar la pregunta. Dado que la base de datos original es suficientemente grande, veo que la decision que mas pacientes costo fue la condicion epileptica. Elegir otra condicion permitiria conservar una N mucho mas decente en la cohorte.
	Por otro lado, dado que la epilepsia es una condicion relativamente rara, tambien vale la pena considerar la fuente de datos. Por ejemplo, la pregunta de las variables fisiologicas seria mucho mas interesante si pudieramos obtener mediciones que ocurrieran durante visitas a hospitales debidas a una crisis convulsiva. Pero hasta donde veo, synthea no tiene la capacidad de generar ese tipo de datos.


2. La tabla, paso a paso (tomando el evento inicial como 100%)

|attrition_step|retained_patients|lost_patients|retained %|
|--------------|-----------------|-------------|----------|
|0. numero total de pacientes en base de datos|11122|0|5617 %|
|1. evento inicial: diagnostico de epilepsia|198|10924|100 %|
|2. exclusiones: 1 año de periodo de obs + sin exposicion previa a medicamento|66|132|33.33 %|
|3. inclusion: recibe tratamiento de MAE|42|24|21 %|
|4. inclusion: el tratamiento de MAE es monoterapia|42|0|21 %|
|5. cohorte final|42|0|21 %|

Una vez definido el evento inicial, el criterio que mas cuesta son las exclusiones, en las cuales perdemos aprox. 2/3 partes de la cohorte. No obstante, como señale antes, la perdida de pacientes desde la base de datos completa (paso 0) hacia la condicion epileptica es brutal (se conserva unicamente alrededor del 1.8 % de los pacientes).


3. El orden importa

Tabla modificada:

|attrition_step|retained_patients|lost_patients|retained %|
|--------------|-----------------|-------------|----------|
|0. numero total de pacientes en base de datos|11122|0|5617 %|
|1. evento inicial: diagnostico de epilepsia|198|10924|100 %|
|2. inclusion: recibe tratamiento de MAE|80|40.4 %|
|3. exclusiones: 1 año de periodo de obs + sin exposicion previa a medicamento|42|38|21 %|
|4. inclusion: el tratamiento de MAE es monoterapia|42|0|21 %|

A pesar de que la N restante en pasos intermedios cambia, podemos ver que la N final de pacientes dentro de la cohorte se mantiene igual. Esto indica que los criterios son independientes entre ellos.



6. ¿que codigos metieron a la gente?

|entry_concept_id|monotherapy_drug_name|patient_count|percent_of_cohort|
|----------------|---------------------|-------------|-----------------|
|19028343|clonazepam 0.25 MG Oral Tablet|21|50.0|
|19074679|carbamazepine 20 MG/ML Oral Suspension [Tegretol]|21|50.0|

Mi cohorte se divide exactamente a la mitad entre la exposicion a dos farmacos distintos. Esto parece ser un efecto de la base de datos sintetica.



7. Conceptos huerfanos

Candidato: diazepam. Para resolverlo, extraje la cantidad de pacientes en la base de datos completa que fueron expuestos a clonazepam, carbamazepina (ambos parte de mi concept_set) o al candidato diazepam:

|medication_group|total_exposed_patients|
|----------------|----------------------|
|Diazepam|120|
|Clonazepam|116|
|Carbamazepine|110|

Sin embargo, no entro como parte de los codigos que metieron pacientes a mi cohorte del ejercicio anterior. Dado los criterios de inclusion y exclusion, considero que NO deberia entrar, ya que el hecho de que no lo hayamos encontrado en el ejercicio anterior nos indica que pacientes expuestos a este medicamento no lo recibieron desde el dia 1, sugiriendo que pudieron haberlo recibido antes (no respetando el criterio de lavado) o pudieron haberlo recibido despues (ya que estaban recibiendo alguno de los dos medicamentos del concept_set que metio pacientes, rompiendo entonces el criterio de monoterapia).



8. Lee el SQL que no escribiste

a) la diferencia mas grande es que en ATLAS no encontre como agregar como criterio de censura el momento en que un paciente pase de monoterapia a politerapia. Es importante tenerlo en cuenta, ya que de haber utilizado ATLAS como herramienta inicial para generar la cohorte, este criterio de censura deberia agregarlo posteriormente.

b) de acuerdo con las instrucciones de la actividad en el laboratorio anterior, mi script de SQL utiliza CTEs para ir encadenando las operaciones necesarias, como criterios de inclusion, censura, etc. En cambio, por lo que veo, ATLAS utiliza tablas temporales, utilizando el comando CREATE TEMP TABLE las cuales al final va descratando (mediante DROP TABLE). Si el resultado es el mismo, no deberia importar que se utilicen estrategias distintas. Pero es interasante contemplar ambas posibilidades, sobretodo en cuanto a los tiempos de ejecucion para bases de datos grandes.

c) como mencione antes, para esta base de datos encontre algunos casos en los que drug_exposure_end_date sea igual que la start_date. Para esos casos yo asumi que la exposicion deberia ser de un mes, siendo este un tiempo de dosis relativamente estandar para ese tipo de medicamentos. Es decir, estoy asumiendo que a los pacientes se les hace una sola prescripcion de un mes y la toman. En cambio, ATLAS, asume esta exposicion como de un dia en vez de 30. Esta diferencia si es importante, ya que puede cambiar las fechas de salida de la cohorte y por lo tanto los resultados.



9. Tres variantes

|Medida|Lavado 180|Lavado 365|Lavado 730|
|------|----------|----------|----------|
|Total patients|50|42|37|
|Age (median (IQR))|10 (4 - 15)|13 (6 - 17)|13 (8 - 23)|
|Sex|MALE (56.0%), FEMALE (44.0%)|MALE (59.5%), FEMALE (40.5%)|MALE (59.5%), FEMALE (40.5%)|
|Follow-up days (median (IQR))|78 (30 - 182)|30 (30 - 180)|30 (30 - 182)|
|Top 3 comorbidities|Seizure disorder (50), Viral sinusitis (19), Gingivitis (16)|Seizure disorder (42), Viral sinusitis (19), Gingivitis (16)|Seizure disorder (37), Viral sinusitis (17), Gingivitis (16)|



10. Cuantificar el traslape

Efectivamente se trata de subconjuntos:

--------------------
porcentaje de la cohorte 730 presente en la cohorte 365: 100.0%
porcentaje de la cohorte 365 presente en la cohorte 180: 100.0%

--------------------
en cohorte 365 queda un: 84.0% de la cohorte 180
en cohorte 730 queda un: 88.1% de la cohorte 365

Tambien lo muestro en las figuras 10_1 y 10_2. En la primera aproximacion, la 10_1, construi un histrograma bineando el conteo de los subjects_ids que entraron a cada cohorte. Se muestra como cada bin de subjects_ids va perdiendo altura conforme el lavado se hace mas estricto, confirmando el sobrelape entre cohortes. Sin embargo, no tiene sentido ni interpretacion binear los ids ya que en realidad es una variable categorica. De ahi que llegara a la segunda aproximacion, el diagrama de venn de la figura 10_2, donde es mucho mas evidente el sobrelape entre cohortes conforme el criterio de lavado se hace mas estricto. Claramente la cohorte base (180 dias, menos estricta, azul) contiene a todos los pacientes, mientras que la naranja (365 dias, intermedia) contiene solo un subset de ellos, y a su vez la verde (730 dias, mas estricta) sigue el mismo patrón. De los 37 que entraron a la cohorte 730, se añadieron 5 mas para conformar la cohorte 365, a los cuales a su vez se les agregaron 8 mas para formar la cohorte 730, dando como resultado los 50 pacientes que entraron a esta ultima.



11. La discusion

- ¿qué decisión de diseño afecta más al resultado?
	De entrada, la condicion elegida es la que mas drasticamente reduce la N de mi cohorte. No se trata de una condicion especialmente rara, como por ejemplo un trastorno genetico muy especifico. Sin embargo, epidemiologicamente, la epilepsia tiende a aparecer en aprox. un 1% de la poblacion, y synthea parece respetar dicha cifra. Eso le quita mucha fuerza a la pregunta. Por otro lado, el criterio de exclusion de un año de observacion previa tambien disminuyo mi N de manera importante.
	
- ¿cuál declaras como tu definición principal, y por qué ésa?
	el diagnostico de epilepsia, seguido de la monoterapia de medicamentos antiepilepticos es una definicion solida que serviria para comenzar a estudiar diferencias entre la monoterapia y la politerapia, como se tenia planeado inicialmente. Despues del laboratorio anterior y este, considero que mi base de datos no contiene la suficiente informacion como para responder esta pregunta efectivamente. Sin embargo, la solidez en los criterios de inclusion y exclusion de mi definicion me convencen.
	
- ¿qué limitación de esta cohorte mencionarías tú mismo antes de que te la señalen?

	de entrada y como mencione antes, mi suposicion sobre el periodo de exposicion a farmacos de 30 dias en los casos en los que synthea no genero days_supply es bastante fuerte y puede afectar de gran manera los resultados.