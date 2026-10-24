1. Reconoce el terreno

| Ingrediente | RxCUI | TTY | SCDF | BN |
|-------------|-------|-----|------|----|
|Carbamazepine| 2002  |  IN |  6   |  4 |
|  Clonazepam | 2598  |  IN |  3   |  1 |
|   Diazepam  | 3322  |  IN |  15  |  4 |



2. Del producto al Ingrediente:

|drug_concept_id|drug_name|concept_class_id|ingredients|
|---------------|---------|----------------|-----------|
|19030765|1 ML epoetin alfa 4000 UNT/ML Injection [Epogen]|Quant Branded Drug|epoetin alfa|
|40213154|Influenza, split virus, trivalent, injectable, preservative free|CVX|No Standard Ingredient Mapped|
|19009384|insulin isophane, human 70 UNT/ML / insulin, regular, human 30 UNT/ML Injectable Suspension [Humulin]|Branded Drug|insulin isophane + insulin, regular, human|
|19080128|lisinopril 10 MG Oral Tablet|Clinical Drug|lisinopril|
|19078106|hydrochlorothiazide 25 MG Oral Tablet|Clinical Drug|hydrochlorothiazide|
|19073094|amlodipine 2.5 MG Oral Tablet|Clinical Drug|amlodipine|
|44818179|sodium fluoride 0.0272 MG/MG Oral Gel|Clinical Drug|sodium fluoride|
|40163924|24 HR metformin hydrochloride 500 MG Extended Release Oral Tablet|Quant Clinical Drug|metformin|
|35604087|cisplatin 50 MG Injection|Clinical Drug|cisplatin|
|1378388|paclitaxel 100 MG Injection|Clinical Drug|paclitaxel|
|40173590|alendronic acid 10 MG Oral Tablet|Clinical Drug|alendronate|
|1539463|simvastatin 10 MG Oral Tablet|Clinical Drug|simvastatin|
|40213227|tetanus and diphtheria toxoids, adsorbed, preservative free, for adult use (5 Lf of tetanus toxoid and 2 Lf of diphtheria toxoid)|CVX|No Standard Ingredient Mapped|
|40162606|acetaminophen 300 MG / hydrocodone bitartrate 5 MG Oral Tablet|Clinical Drug|acetaminophen + hydrocodone|
|19033893|ibuprofen 400 MG Oral Tablet [Ibu]|Branded Drug|ibuprofen|
|19041324|acetaminophen 325 MG Oral Tablet [Tylenol]|Branded Drug|acetaminophen|
|906115|tropicamide 5 MG/ML Ophthalmic Solution|Clinical Drug|tropicamide|
|46287738|24 HR tacrolimus 1 MG Extended Release Oral Tablet [Envarsus]|Quant Branded Drug|tacrolimus|
|40231918|acetaminophen 325 MG / oxycodone hydrochloride 10 MG Oral Tablet [Percocet]|Branded Drug|acetaminophen + oxycodone|
|1127433|acetaminophen 325 MG Oral Tablet|Clinical Drug|acetaminophen|



3. De la clase ATC a los ingredientes

|ingredient_concept_id|ingredient_name|distinct_product_count|patient_count|total_exposures|
|---------------------|---------------|----------------------|-------------|---------------|
|1539403|simvastatin|5|2439|12264|
|1503297|metformin|1|437|19394|
|1510813|rosuvastatin|8|63|63|
|40170911|liraglutide|1|3|12|



4. <<Exposicion a metformina>>, tres veces:

Ingrediente: simvastatina 

| Version | ¿Que incluye? | Numero de presentaciones |Numero de pacientes expuestos |
|---------|---------------|--------------------------|------------------------------|
|    A    |  Monoterapia  |            3             |            2965              |
|    B    |  Combinacion  |            5             |            2967              |
|    B    |   Seleccion   |            3             |            2925              |

En realidad no hay mucha diferencia entre los conteos, efecto de la base de datos sintetica que genera en su gran mayoria monoterapias para este medicamento. Sin embargo, si fuera a estudiar los efectos del medicamento en cierto órgano, me quedaría con la versión A de monoterapia, ya que buscaría incluir la menor cantidad posible de variables con el fin de ver exclusivamente el efecto de ese medicamento.


5. Leer tres codigos LOINC:

|loinc_code|long_common_name|component|property|time_aspect|system|scale_type|method|
|----------|----------------|---------|--------|-----------|------|----------|------|
|2160-0|Creatinine [Mass/volume] in Serum or Plasma|Creatinine|Mass Concentration|Point in time (spot)|Serum or Plasma|Qn|Unspecified|
|2345-7|Glucose [Mass/volume] in Serum or Plasma|Glucose|Mass Concentration|Point in time (spot)|Serum or Plasma|Qn|Unspecified|
|4548-4|Hemoglobin A1c/Hemoglobin.total in Blood|Hemoglobin A1c/Hemoglobin.total|Mass fraction|Point in time (spot)|Blood|Qn|Unspecified|

Descripciones:
- component: nombre del analito
- property: unidad de medida
- time_aspect: unidad de tiempo en la cual se realiza la observacion
- system: parte o fluido del cuerpo de la cual se obtiene la observacion
- scale_type: tipo de medida (escala, categoria, etc)
- method: tecnica de laboratorio o instrumento usado para obtener la observacion


6. El concept set de un analito no es un codigo

|concept_id|loinc_code|loinc_name|method_name|measurement_count|patient_count|
|----------|----------|----------|-----------|-----------------|-------------|
|3004410|4548-4|Hemoglobin A1c/Hemoglobin.total in Blood|Unspecified / Standard|89080|4782|
|3011397|5794-3|Hemoglobin [Presence] in Urine by Test strip|Test strip|77162|2478|
|3000963|718-7|Hemoglobin [Mass/volume] in Blood|Unspecified / Standard|36429|11122|
|3009744|786-4|MCHC [Entitic Mass/volume] in Red Blood Cells by Automated count|Automated count|36311|11122|
|3012030|785-6|MCH [Entitic mass] by Automated count|Automated count|36311|11122|
|40761014|57905-2|Hemoglobin [Presence] in Stool from gastrointestinal lower by Immunoassay --1st specimen|Immunoassay|710|691|

A pesar de ser el codigo mas frecuente (~89k mediciones), si unicamente se tomara el codigo 4548-4 perderiamos una gran cantidad de registros. Tan solo el codigo 5794-3 aporta otras ~77k mediciones. Tambien hay otros codigos que a pesar de no aportar tantas mediciones, fueron realizadas en todos los pacientes de la base de datos (~11k), lo cual me dice que son parte de encuentros rutinarios en vez de especializados.


7. Auditoria de unidades

|loinc_code|analyte|total_measurements|distinct_valid_units|pct_unmapped_or_null|
|2160-0|Creatinine [Mass/volume] in Serum or Plasma|65544|1|0.00|
|2345-7|Glucose [Mass/volume] in Serum or Plasma|65544|1|0.00|
|4548-4|Hemoglobin A1c/Hemoglobin.total in Blood|89080|1|0.00|

En este caso la base sintetica genero datos demasiados buenos, mostrando para estos 3 analitos 100% de los valores en la misma unidad. Así mismo, ninguno de los 3 muestra mediciones sin unidades registradas. Por lo tanto, para los 3 casos es perfectamente seguro promediar los datos, ya que no es necesario considerar ningún factor de conversión.


8. Mapear un catalogo local

| N° | clave_local | descripcion_local | concept_id | concept_name | confianza |¿quien y por que?|
|----|-------------|-------------------|------------|--------------|-----------|-----------------|
| 01 | 010.000.0101.00 | aspirina 500mg | 1718517 | acetylsalicylsalicylic acid | alta | de RxNorm, encontrado en Athena a partir de "Non-standard to Standard map" |
| 02 | 010.000.5940.00 | IBUPROFENO | 1177480 | ibuprofen | alta | de RxNorm, encontrado en Athena a partir de "Non-standard to Standard map" |
| 03 | 040.000.6175.00 | naloxona/oxicodona | 36029671 | nalaxone/oxycodone | dudosa | en athena, cada ingrediente si mapea a una entry standard de RxNorm, pero la combinacion especifica no es standard|
| 04 | 040.000.2608.00 | CBZ | 740275 | carbamazepine | alta | de RxNorm, encontrado en Athena a partir de "Non-standard to Standard map" |
| 05 | 040.000.2673.00 | ergotamina y cafeina, 1mg y 100mg | 36677567 | ergotamine and caffeine containing product | no mapeable | cada ingrediente individual si mapea a standarnd de RxNorm, pero la combinacion especifica solo la encuentro en athena como "containing product", sin dosis, y no es standard |
| 06 | 010.000.6349.00 | CERLIPONASA ALFA | 1594332 | cerliponase | dudosa | cerliponase alfa no es standard, pero esta en la seccion "Has form (RxNorm)" de cerliponase, la cual si es estandar |
| 07 | 010.000.2630.00 | VALPROATO SEMISÓDICO tableta liberacion prolongada 500 mg | 21272000 | valproate semisodium | no mapeable | tiene equivalente en vocabulario dm+d (Dictionary of Medicine and Devices), pero no es standard y dice en athena que ya esta obsoleto (deprecated) |
| 08 | 010.000.2617.00 |LEVETIRACETAM 500mg | 711584 | levetiracetam | alta | de RxNorm, encontrado en Athena a partir de "Non-standard to Standard map" |
| 09 | 010.000.4362.00 | toxina botulinica A | 729855 | botulinum toxin type A | alta | de RxNorm, encontrado en Athena a partir de "Non-standard to Standard map" |
| 10 | 010.000.5236.00 | RANIBIZUMAB 2.3mg | 19080982 | ranibizumab | dudosa | mapeable a ingrediente standard de RxNorm, pero no en esa presentacion |
| 11 | 010.000.5451.00 | cinarizina | 19097490 | cinnarizine 75mg | alta | de RxNorm, encontrado en Athena a partir de "Ingredient of" del ingrediente base |
| 12 | 010.000.5795.00 | CERTOLIZUMAB PEGOL 200mg solucion inyecyable | 607336 | Certolizumab pegol 200 mg/mL solution for injection | Alta | de SNOMED, encontrado en Athena a partir de "Precise active ingredient of (SNOMED)" del ingrediente base |
| 13 | 060.066.1144 | Solucion antiseptica al 0.002% de especies activas de cloro y oxigeno. Envase con 60 ml| 4337018 | Antiseptic | no mapeable | se encuentran clases similares en vocabulario NDFRT, bajo el concepto Pharmacologic class. Pero no con las especificaciones de ingredientes |
| 14 | 010.000.5487.01 | citalopram tableta 20mg | 797636 | citalopram 20 MG | Alta | de RxNorm, encontrado en Athena a partir de "Ingredient of" del ingrediente base |
| 15 | 010.000.4058.01 | PRILOCAINA, FELIPRESINA 54mg, 0.054UI | 45917810 | Felypressin / prilocaine | no mapeable | Mapea a la combinacion especifica, pero no es standard y no desglosa dosis |

Lo mas dificl fue encontrar las presentaciones con dosis especificas. Porcentaje altas = 40%.