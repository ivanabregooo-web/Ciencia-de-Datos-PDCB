1. Subir a la raiz con WITH RECURSIVE:

Condicion: epilepsia

Camino completo 1: Epilepsy -> Seizure disorder -> Disorder of brain -> Disorder of the central nervous system -> Disorder of nervous system -> Disorder of body system -> Disorder by body site -> Disease -> Clinical finding -> SNOMED CT Concept

Camino completo 2: Epilepsy -> Seizure disorder -> Disorder of brain -> Disorder of head -> Head finding -> Finding of head and neck region -> Finding of body region -> Finding by site -> Clinical finding -> SNOMED CT Concept

Profundidad: 9 niveles


2. El mismo problema con CONCEPT_ANCESTOR

Camino completo:

|Paso|Ancestro|
|----|--------|
|0|                                   Epilepsy|
|1|                           Seizure disorder|
|2|                          Disorder of brain|
|3|                                    Seizure|
|4|                           Disorder of head|
|5|     Disorder of the central nervous system|
|6|                           Finding of brain|
|7|                    Seizure related finding|
|8|             Central nervous system finding|
|9|                                    Disease|
|10|                Disorder of nervous system|
|11|                              Head finding|
|12|                      Neurological finding|
|13|                          Clinical finding|
|14|                   Disorder of body system|

Profundidad: 7 niveles.

Si devuelven lo mismo, pero no son exactamente identicos. WITH RECURSIVE explora varias relaciones para los conceptos que tienen mas de un ancestro. En la solucion del ejercicio 1 muestro que a partir de WITH RECURSIVE se pueden obtener varios caminos. El camino va igual hasta que se busca los padres de Disorder of brain, donde encuentra tanto a Disorder of the central nervous system como a Disorder of head, y a partir de ahi se ramifica a dos soluciones distintas pero igualmente validas. Por otro lado, la solucion con CONCEPT_ANCESTOR acomoda los ancestros de manera distinta, ya que primero muestra a Disorder of the head y sigue sus padres hasta Disease. Posteriormente pone a Disorder of the nervous system y lo sigue hasta a Disorder of body system. Tambien le hicieron falta dos niveles adicionales que WITH RECURSIVE si encontro: Disorder by body site y la raiz mas profunda que encontro: directamene un SNOMED CT concept.


3. La tabla que explica las diferencias

- Existen 724 tipos de relaciones
- 124 de ellas tienen is_hierarchical = 1
- 63 relaciones tienen defines_ancestry = 1
- de las dos anteriores, 55 relaciones son parte de los conjuntos tanto is_hierarchical como defines_ancestry

|relationship_id|relationship_name|total_connections|explicacion|
|RxNorm ing of|Ingredient of (RxNorm)|24|farmacos de los cuales la carbamazepina es un ingrediente|
|Mapped from|Standard to Non-standard map (OMOP)|19|concepto original desde el cual se extrajo el concepto estandar|
|Has brand name|Has brand name (OMOP)|8|marcas de medicamentos en las cuales hay carbamazepina|
|RxNorm - SNOMED eq|RxNorm to SNOMED equivalent (RxNorm)|2|traduccion desde RxNorm hacia SNOMED|
|Maps to|Non-standard to Standard map (OMOP)|1|paso invertido de la tercera fila|


4. Encontrar un caso real en tu base

Conceptos: epilepsy, disease

Caminos:
- a) Epilepsy -> Seizure disorder -> Disorder of brain -> Disorder of head -> Disease
- b) Epilepsy -> Seizure disorder -> Disorder of brain -> Disorder of the central nervous system -> Disorder of nervous system -> Disorder of body system -> Disorder by body site -> Disease

Esto tambien explica las diferencias que encontramos en el ejercicio 1. Mientras que una relacion puede ser jerarquica, no necesariamente tiene que ser tambien ancestral. Esto quiere decir que es posible llegar por dos caminos distintos al mismo concepto raiz, incluso pudiendo saltar algunos padres. En el sentido clinico, es perfectamente valido clasificar a la epilepsia como un Disorder of brain que a su vez puede ser clasificado como Disorder of head. Asi mismo, tambien es posible ser mas especifico en las clasificaciones intermedias e incluir Disorder of the central nervous system, a partir del cual tambien se extrae el ancescro Disorder of body system. Aunque se llega a la misma raiz de Disease, la unica diferencia esta en que tantos pasos intermedios cada vez mas especificos se incluyen.


5. Medir el daño:

|condition_group|ancestor_join_count|distinct_concept_count|distinct_person_count|
|---------------|-------------------|----------------------|---------------------|
|1| Epilepsy|218|218|198|
|2| Seizure Disorder|257|257|619|

Para el caso de epilepsy, encontramos el mismo conteo para el join sobre ancestor y para distinct concept. Esto quiere decir que CONCEPT_ANCESTOR simplifica las rutas con mas de un camino y en vez de agregar el paso extra, simplemente actualiza el conteo de max_levels_of_separation. Esto tambien explica por que la solucion mostrada en la actividad dos se salto un par de ancestros en los niveles de profundidad que WITH RECURSIVE si logro extraer. Por su parte, distinct person id es el unico que verdaderemente muestra cuantos pacientes realmente fueron diagnosticados con epilespsia. A su vez, el conteo de person_id para seizure disorder (padre directo de epilepsy) muestra un conteo inflado de pacientes, ya que incluye tanto epilepsia como cualquier otro seizure disorder diagnosticado en la base de datos.


6. ¿Por que no entro este paciente?

|person_id|event_date|raw_source_code|source_concept_name|standard_concept_id|standard_concept_name|branch_to_epilepsy|
|---------|----------|---------------|-------------------|-------------------|---------------------|------------------|
|304|1990-01-02|84757009|Epilepsy|380378|Epilepsy|Epilepsy|
|22|1921-10-19|84757009|Epilepsy|380378|Epilepsy|Epilepsy|
|15|          |        |        |      |        |        |

Me parece que nuevamente vemos un efecto de la base sintetica en la cual no encontramos un paciente que haya entrado a la cohorte por una condicion descendiente a epilepsy, sino que directamente genera pacientes epilepticos. De cualquier manera, los primeros dos ejemplos muestran que la consulta filtra correctamente a los pacientes epilepticos, ya que esos person_id los pase de antemano sabiendo que eran parte la cohorte. Por otro lado, el person_id 15 lo dejo vacio porque realmente esa es la salida que devuelve la consulta cuando se le pasa un paciente que NO fue diagnosticado con epilepsia.


7. Cazar conceptos muertos

Como ocurrio con el patient_id 15 del ejercicio 6, el output de esta consulta resulto vacio. Esto me indica que la base de datos no genero pacientes con conceptos invalidos. Tanto epilepsia como seizure disorder son conceptos estandar, validos y vigentes. No han sido reemplazados.




