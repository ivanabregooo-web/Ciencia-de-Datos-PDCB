Para la conversion:

- Comando para generar los datos (terminal):
	> .\gradlew.bat run -Dorg.gradle.jvmargs="-Xmx8g" --args="p 10000 -t 1"
	nota: se necesita el formato csv de synthea: `exporter.csv.export` option in the `./src/main/resources/synthea.properties` file needs to be set to TRUE.

- Clonar repositorio de ETL-Synthea (terminal):
	>  git clone https://github.com/OHDSI/ETL-Synthea.git

- Descargar archivo .zip de tablas de OMOP, en especifico version 5.4.2:
	> https://github.com/OHDSI/CommonDataModel/releases#release-v5.4.2

- Montar postgres con docker usando bind mount (terminal):
	> docker run --rm --name my_postgres --env-file .env -p 5432:5432 -v "%cd%:/workspace" -v "C:\Users\IVAN\Documents\postgres_data:/var/lib/postgresql/data" -d postgres:15.4

- Preparar archivos de sql OMOPCDM_postgresql_5.4_constraints.sql, OMOPCDM_postgresql_5.4_ddl.sql, OMOPCDM_postgresql_5.4_primary_keys.sql, OMOPCDM_postgresql_5.4_indices.sql (editor de texto):
	> buscar '@cdmDatabaseSchema' e intercambiar por 'public'

- Ejecutar el script DDL para crear tablas vacias (terminal):
	> docker exec my_postgres psql -U postgres -d postgres -f "workspace/omop_cdm_postgresql/OMOPCDM_postgresql_5.4_ddl.sql"

- Crear esquema nativo (terminal):
	> docker exec my_postgres psql -U postgres -d postgres -f "/workspace/ETL-Synthea/inst/sql/sql_server/synthea_version/v330/create_synthea_tables.sql"

- LLenar tablas vacias con los datos de synthea usando el script de cargado propio (terminal):
	> docker exec my_postgres psql -U postgres -d postgres -f "/workspace/load_synthea.sql"
	nota: se copiaron la mayoria de los archivos pero fallo casi al final, aca debuggeo ese error y copio los archivos faltantes:

- Debuggear: Mi version de synthea genero 1 columna 'NPI' en providers.csv y organizations.csv que las tablas vacias no estaban contemplando, asi que tuve que agregarlas manualmente (terminal):
	> docker exec my_postgres psql -U postgres -d postgres -c "ALTER TABLE native.organizations ADD COLUMN npi VARCHAR(255); ALTER TABLE native.providers ADD COLUMN npi VARCHAR(255);"

- Copiar archivos faltantes (terminal):
	> docker exec my_postgres psql -U postgres -d postgres -c "COPY native.providers FROM '/workspace/data/providers.csv' WITH (FORMAT CSV, HEADER); COPY native.organizations FROM '/workspace/data/organizations.csv' WITH (FORMAT CSV, HEADER);"

- Cargar vocabularios: se creo un script para copiar los archivos .csv de vocabualarios de OMOP (terminal):
	> docker exec my_postgres psql -U postgres -d postgres -f "/workspace/load_vocab.sql"
	nota: en este script se tuvo que especificar el delimitador como tab en vez de coma, porque si no se rompia.

- Identificar las llaves primarias (terminal):
	> docker exec my_postgres psql -U postgres -d postgres -f "/workspace/omop_cdm_postgresql/OMOPCDM_postgresql_5.4_primary_keys.sql"

- Crear los indices (terminal):
	> docker exec my_postgres psql -U postgres -d postgres -f "/workspace/omop_cdm_postgresql/OMOPCDM_postgresql_5.4_indices.sql"

- Preparar archivos de ETL-Synthea/inst/sql/sql_server/cdm_version/v540 (notepad++):
	> en todo el directorio, buscar '@cdm.schema' y reemplazar por 'public' y reemplazar '@synthea.schema' por 'native'

- Preparar ambiente en *RStudio* para correr el ETL:
	> install.packages("remotes")
	> remotes::install_github("OHDSI/DatabaseConnector")
	> library(DatabaseConnector)
	nota: en este punto me encontre un error:
Error: package or namespace load failed for ‘DatabaseConnector’:
.onLoad falló en loadNamespace() para 'rJava', detalles:
llamada: fun(libname, pkgname)
error: JAVA_HOME cannot be determined from the Registry
Para solucionarlo, tuve que instalar java (https://adoptium.net/en-GB), version JDK 25 LTS, windows, x64.
	> library(DatabaseConnector)
	> library(ETLSyntheaBuilder)
	drivers para comunicacion R-Docker:
	> downloadJdbcDrivers("postgresql", pathToDriver = getwd())
	conectar con base de datos:
	> cd <- createConnectionDetails(
            dbms = "postgresql",
            server = "localhost/postgres",
            user = "postgres",
            password = "password", 
            port = 5432,
            pathToDriver = getwd()
            )
	nota: en este punto RStudio se atoraba con este error:
	Running: insert_visit_occurrence.sql
	| | 0%Error in `.createErrorReport()`:! Error executing SQL: org.postgresql.util.PSQLException: ERROR: relation "public.all_visits" does not exist
	Position: 1185
	Me estaba haciendo falta pre construir una tabla temporal que ayuda a pasar encuentros continuos de synthea como una sola visita de larga duracion.
	construir tabla de visitas:
	> CreateVisitRollupTables(
			connectionDetails = cd,
			cdmSchema = "public",
			syntheaSchema = "native",
			cdmVersion = "5.4"
			)
	Transformar datos de eventos synthea a esquema omop (este paso tardo 66 minutos) :
	> LoadEventTables(
		connectionDetails = cd,
	    cdmSchema = "public",
	    syntheaSchema = "native",
	    cdmVersion = "5.4",
	    syntheaVersion = "3.3.0"
	    )
	Finalmente, correr script para aplicar mapeo de llaves foraneas (terminal):
	> docker exec my_postgres psql -U postgres -d postgres -f "/workspace/omop_cdm_postgresql/OMOPCDM_postgresql_5.4_constraints.sql"



2. Convertir:

Conteo de filas por tablas:

| table_name | row_count |
|------------|-----------|
| measurement | 5875466 |
| observation | 3059641|
| cost | 1740419 |
| procedure_occurrence | 1015698 |
| drug_exposure | 697826 |
| visit_occurrence | 604979 |
| condition_occurrence | 190298 |
| condition_era | 187352 |
| drug_era | 127947 |
| person | 11122 |


3. Cargar vocabualarios

Conteo de conceptos:

| concept_type | total_concepts |
|--------------|----------------|
| Non-Standard (NULL) | 1086670 |
| Standard | 849381 |
| Classification | 93424 |


4. Dibujar el modelo

Como cargue todas las tablas, hacer el ERD (fig 4_1) a mano iba a tomarme mucho tiempo, asi que lo automatice usando un analizador de metadatos de bases de datos (SchemaSpy: https://github.com/schemaspy/schemaspy). Asumiendo que haya hecho su trabajo correctamente, encontre algunas diferencias con las especificaciones de la v5.4:
- En mi base de datos se generaron un par de tablas, source_to_source_vocab_map y source_to_standard_vocab_map que no aparecen en la documentacion del OMOP-CDM. Mas que una simplificacion del ELT, entiendo que son tablas intermedias necesarias para la traduccion synthea-omop, pero que no son necesarias de acuerdo con la convencion.
- En mi base de datos, existe una tabla llamada all_visits que no aparece en la documentacion (lo mas cercano es visit_occurrence, la cual tambien tengo). Ademas, quedo clasificada como una tabla huerfana, sin llaves foraneas. Sin embargo, su primera columan corresponde a encounter_id, que probablemente pudo haber sido traducida a un visit_occurrence_id de manera que no quedara huerfana. Es un error mio ya que esta tabla resulto de mi proceso de debuggear el error en el que mi RStudio se estaba atorando que describi arriba, y debi asignarle manualmente sus llaves foraneas o de plano hacerle DROP a la tabla. Espero no afecte en nada, ya que visit_occurrence deberia condensar la misma informacion que se quedo sin referenciar en la tabla temporal.



5. La primera metrica de calidad: contar ceros.
Porcentajde de concept_id = 0 por dominio:

|domain|total_rows|unmapped_rows|unmapped_pct|
|------|----------|-------------|------------|
|device_exposure|51901|0|0.00
|condition_occurrence|190298|0|0.00|
|visit_occurrence|604979|0|0.00|
|drug_exposure|697826|0|0.00|
|procedure_occurrence|1015698|0|0.00|
|observation|3059641|0|0.00
|measurement|5875466|0|0.00|

Encontramos 0% de concept_id=0. Al principio me parecio muy sospechoso pero tiene sentido considerando que use datos de Synthea y para la conversion use ETL-Synthea, ocasionando que los scripts de conversion manejen perfectamente los datos sinteticos y se obtenga un mapeo perfecto.


7. Estandar contra origen

Para la condicion "anemia", encontramos el mismo conteo de diagnosticos ya sea usando condition_concept_id o condition_source_value (4044). Esto nuevamente es debido al efecto del mapeo perfecto que hace ETL-Synthea sobre los datos de Synthea. No se cuenta con ese realismo de tener entries heterogeneas de "anemia" y de "low red blood cell count" por ejemplo. En cambio, synthea genera unicamente entries con el codigo de SNOMED-CT propio de anemia, ocasionando que el mapeo perfecto se vea reflejado en este conteo



8. Respetar observation_period

|total_conditions|conditions_within_observation|conditions_outside_observation|percent_within_window|
|------|-----|------|-----|
|190298|189576|722|99.62|

Practicamente todas las observaciones caen dentro del periodo de observacion. Muy posiblemente indica que synthea genera un periodo de observacion que abarca desde el nacimiento hasta la muerte del paciente, nuevamente quitandole realismo a la base de datos. De acuerdo con uno de los hallazgos que recuerdo del laboratorio 02, es muy probable que la pequeña cantidad de condiciones que cayeron fuera del periodo de observacion correspondan a algo relacionado con la muerte de los pacientes, como la incorporacion de su certificado de muerte a la base de datos. No obstante, ignorar esa ventana en un estudio real podria introducir variables extrañas que contaminen los resultados. Al tratarse de observaciones fuera del periodo de observacion, no se cuenta con un control exacto de la temporalidad de estas observaciones. Es decir, un medico puede registrar en la base de datos un hallazgo de anemia que el paciente haya tenido en su infancia. Esto ocasionaria que se pierda el control temporal, ya que ese hallazgo no corresponde a un test o prueba que se haya hecho durante la adultez del adulto y que se pueda ligar a otra tabla mediante una llave foranea. Funciona mas como un registro historico que no podria o no deberia ser considerado en conteos/distribuciones/operaciones/etc.



9. Explorar en Athena

| Concepto | concept_id | vocabulario | dominio | es estandar | conceptos hijo | codigo de origen que mapea a el |
|----------|------------|-------------|---------|-------------|-----------------|------------|
|  Anemia  |  439777  | SNOMED |condition | si | 580 | 191232001 (SNOMED, Aplastic and other anemias) |
| Diabetes mellitus | 201820 | SNOMED |condition | si | 132 | E13.1 (ICD10CM, Other specified diabetes mellitus with ketoacidosis) |
| Cisplatin | 1397599 | RxNorm | drug | si | 14 | 303282001 (SNOMED, Diaminedichloroplatinum) |



10. Comparacion con Eunomia:
- a) en cuanto a la cantidad de pacientes, no se puede hacer una comparacion limpia ya que con synthea yo controlo ese parametro.
- b) para la distribucion de edad, se encuentra algo parecido para ambas bases de datos. Aunque no dibuje el histograma, parece mostrar algo parecido a una distribucion normal, con la mayoria de los pacientes en rangos de edad interemdios y menos pacientes en los extremos.
- c) En cuanto a mediana de dias de observacion, con mis datos de synthea encontre una media de 10777 (~ 29.5 años), mientras que en eunomia se cuenta con una mediana de 13867 dias (~ 37.9 años). No veo una gran diferencia entre ellos. Mas bien, se me hace poco realista que a tantos pacientes se les de seguimiento por tanto tiempo en un mismo hospital o que tantos años de registros queden almacenados en una misma base de datos. Veo en el github de eunomia que algunos de sus datasets https://github.com/OHDSI/EunomiaDatasets/tree/main/datasets) tambien estan generados con synthea, lo cual explicaria estas similitudes. Sin embargo, no encuentro informacion especifica que diga que el dataset que utilice (GiBleed) tambien haya sido generado con Synthea.

- d) 

Synthea, propios, top20 diagnosticos:
Gingivitis	30115
Limited social contact	11453
Viral sinusitis	11334
Social isolation	11127
Gingival disease	8874
Primary dental caries	6740
Acute viral pharyngitis	6531
Acute bronchitis	5426
Body mass index 30+ - obesity	5339
Normal pregnancy	4835
Prediabetes	4238
Anemia	4044
Risk activity involvement	2844
Chronic pain	2653
Essential hypertension	2507
Chronic sinusitis	2341
Abnormal findings diagnostic imaging heart+coronary circulat	2118
Ischemic heart disease	2109
Infection of tooth	1998
Chronic low back pain	1949


Eunomia, top 20 diagnosticos:
Viral sinusitis	17268
Acute viral pharyngitis	10217
Acute bronchitis	8184
Otitis media	3605
Osteoarthritis	2694
Streptococcal sore throat	2656
Sprain of ankle	1915
Concussion with no loss of consciousness	1013
Sinusitis	1001
Acute bacterial sinusitis	939
Whiplash injury to neck	825
Chronic sinusitis	825
Peptic ulcer	802
Sprain of wrist	770
Fracture of forearm	569
Laceration of forearm	507
Laceration of hand	500
Laceration of thigh	499
Facial laceration	497
Fracture subluxation of wrist	493


En este caso no se parecen tanto, solo veo sinusitis y bronquitis compartidas entre ambas. Sin embargo, todas las condiciones encontradas aqui son habituales, lo cual si le da cierto realismo a ambos datasets.




