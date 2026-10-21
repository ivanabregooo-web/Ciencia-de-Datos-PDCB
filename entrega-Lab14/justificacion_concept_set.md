Para montar la base de datos:

Debido al bind mount usado cuando se hizo la conversion a OMOP-CDM (ver reporte_calidad.md de entrega-Lab12), unicamente es necesario volver a conectarse utilizando docker. En mi caso:

En terminal, en la misma ruta donde se encuentre el archivo .env con las credenciales:
	>docker run --rm --name my_postgres --env-file .env -p 5432:5432 -v "%cd%:/workspace" -v "C:\Users\IVAN\Documents\postgres_data:/var/lib/postgresql/data" -d postgres:15.4



1. Elige tu condicion:

Epilepsia, relacionada con mi tesis. Quisiera estudiar diferencias en analitos fisiologicos relevantes y en el progreso de la enfermedad (inicialmente con el numero de visitas y el tiempo entre ellas), según si los pacientes reciben monoterapia (tratamiento con un solo medicamente) o politerapia (varios medicamentos a la vez). Tendria que evaluar si es viable según el número de pacientes que reciban exclusivamente cada tipo de tratamiento.



2. Encuentra el concepto semilla en ATHENA:

- concept_id: 380378
- concept_name: Epilepsy
- domain_id: Condition
- vocabulary_id: SNOMED
- concept_class_id: Disorder
- standard_concept: Standard
- Padre inmediato: Seizure Disorder
- Numero de descendientes totales: 217
- Hijos directos: 69



3. Traduce ICD-10 a estandar:

Codigos:
	G40,
	G40.0,
	G40.1,
	G40,2,
	G40.3,
	G40.4,
	G40.8,
	G40.9,
	G40.31,
	G40.411,
	G40.B,
	F80.3,
	Z15.1,
	Z82.0,

|icd10_code|origin_concept_id|origin_nam|standard_concept_id|standard_name|mapped_targets_per_code|
|----------|-----------|----------------|-------------------|-------------|-----------------------|
|G40.411|45591173|Other generalized epilepsy and epileptic syndromes, intractable, with status epilepticus|37167166|Drug resistance to anti-seizure medication|3|
|G40.411|45591173|Other generalized epilepsy and epileptic syndromes, intractable, with status epilepticus|4055361|Generalized epilepsy|3|
|G40.411|45591173|Other generalized epilepsy and epileptic syndromes, intractable, with status epilepticus|4332304|Status epilepticus|3|
|G40.31|1568312|Generalized idiopathic epilepsy and epileptic syndromes, intractable|4055361|Generalized epilepsy|2|
|G40.31|1568312|Generalized idiopathic epilepsy and epileptic syndromes, intractable|443615|Refractory migraine|2|
|F80.3|35207247|Acquired aphasia with epilepsy (Landau-Kleffner)|4046219|Landau-Kleffner syndrome|1|



4. Construye tres versiones del concept_set y 5. Mide el impacto en pacientes
Por ser una base de datos sintetica, no encontre diferencias en la primera aproximacion entre epilepsia y sus descendientes. Al parecer synthea no genera pacientes diagnosticados con descendientes de epilepsia. Entonces, para el ejercico, hice las busquedas a partir de su padre inmediato (Seizure disorder):


| Version | Numero de conceptos | Numero de pacientes |
|---------|---------------------|---------------------|
| Estricta | 1 | 198 |
| Amplia | 257 | 619 (+312.62%) |
| Razonada | 246 | 389 (+196.46%) |


6. Revision manual de 20 conceptos y 7. Documenta la decision:

|concept_id|concept_name| ¿entra? | razon |
|----------|------------|---------|-------|
|36675141|Early-onset spastic ataxia, myoclonic epilepsy...| si | tipo de epilepsia |
|37160959|Global developmental delay, neuro-ophthalmolog...| no | no se busca estudiar trastornos del desarrllo |
|36716897|Epileptic encephalopathy| si | tipo de epilepsia |
|37472166|Neuronal ceroid lipofuscinosis type 1| no |
|36676621|Early-onset epileptic encephalopathy, cortical...| no se busca incluir enfermedades neurodegenrativas hereditarias raras |
|36674784|Benign occipital lobe epilepsy| si | tipo de epilepsia |
|762729|Lennox-Gastaut syndrome, refractory| no | no se busca estudiar sindromes epilepticos en poblacion infantil |
|35622261|Reflex epilepsy with startle-induced seizures| si | tipo de epilepsia |
|36674191|Intellectual disability, seizures, hypotonia, ...| no | incluir una condicion con varios trastornos distintos meteria mucho ruido al estudio |
|37156904|Seizures, scoliosis, macrocephaly syndrome| no | incluir una condicion con varios trastornos distintos meteria mucho ruido al estudio |
|4102345|Temporal lobe epilepsy| si | el tipo de epilepsia mas comun |
|37164081|Progressive myoclonic epilepsy type 9| si | tipo de epilepsia |
|4185733|Self-limited epilepsy with centrotemporal spikes| si | tipo de epilepsia |
|37204409|Progressive myoclonic epilepsy type 3| si | tipo de epilepsia |
|44783583|Genetic epilepsy with febrile seizures plus| no | no se busca estudiar trastornos geneticos ni con convulsiones no provocadas por epilepsia, como las febriles |
|37160838|Epilepsy due to parasitic disease| no | no se busca estudiar una condicion epileptica consecuencia de una infeccion |
|4046219|Landau-Kleffner syndrome| no | no se busca estudiar sindromes epilepticos en poblacion infantil |
|37205773|Multiple congenital anomalies, hypotonia, seiz...| no | incluir una condicion con varios trastornos distintos meteria mucho ruido al estudio |
|44784595|Post-cerebrovascular accident epilepsy| no | no se busca estudiar una condicion epileptica consecuencia de un evento vascular |
|37167962|Primary hypomagnesemia, refractory seizures, i...| no | incluir una condicion con varios trastornos distintos meteria mucho ruido al estudio |
|137613|Preclampsia| no | no se busca estudiar trastornos del embarazo |


Sobre sensibilidad y valor predictivo positivo (PPV):

Como explique antes, parece que synthea no tiene la capacidad para generar pacientes diagnosticados con conceptos descendientes de epilepsia, unicamente genera de dos tipos: Seizure disorder (padre directo) y Epilepsy. Para ver el impacto de las decisiones tomadas en los ejercicios, tome Seizure disorder como la base para las busquedas amplia y razonada. Por lo tanto, la cohorte amplia inlcuye demasiados conceptos que si bien exhiben sintomas parecidos a la epilepsia, son ocasionados por otros factores que escapan al objetivo del estudio. De manera que la cohorte estricta la construi unicamente con concept_id Epilepsy, la cohorte amplia con Seizure disorder + descendientes (incluyendo epilepsia), y la cohort razonada quitando a mano algunos descendientes de Seizure.

A pesar de haber tomado estas decisones debido a las caracteristicas de los datos generados por Synthea, el ejercicio me permite darme cuenta de que tomar un cohorte estricta tomando como base un unico concept_id semilla, maximiza el PPV , ya que garantiza que se tomen unicamente pacientes diagnosticados con el concepto base y elimina la probabilidad de tomar falsos positivos; pero disminuye la sensibilidad, ya que descendientes muy directos pero con una ligera diferencia (e.g "epilepsia del lobulo temporal" vs solo "epilepsia") no son tomados en cuenta cuando si deberian serlo. Por otro lado, el efecto inverso ocurre con la cohorte amplia, con sensibilidad alta debido a que captura todos los casos posibles de la base + sus descendientes directos, pero disminuye el PPV al reducir la confianza en que todos los descendientes sean de una condicion que efectivamente querramos estudiar, aumentando los falsos negativos. Finalmente, la cohorte razonada es un buen punto medio ambos, ya que nos permite controlar hasta cierta medida (y podria ser perfectamente si uno se da el tiempo de elegir manualmente los descendientes a ser incluidos) las omisiones a los descendientes que meterian ruido a nuestro estudio, mientras al mismo tiempo aumenta la N de pacientes que si queremos estudiar.
