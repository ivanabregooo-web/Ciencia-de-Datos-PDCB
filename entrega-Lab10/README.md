Para reproducir el analisis en el jupyter notebook:

- docker necesario para conectar con postgres. Desde la terminal (anaconda prompt), ubicado en la misma carpeta donde el archivo .env este ubicado:
	>docker run --name my_postgres --env-file .env -p 5432:5432 -d postgres:15.4
- plugin para usar comando magico %%sql dentro del notebook y poder usar directamente comandos de sql sin usar comillas:
	> pip install jupysql
Al finalizar:
	>docker rm -f my_postgres

1. Comando para generar los datos:

.\gradlew.bat run -Dorg.gradle.jvmargs="-Xmx8g" --args="p 10000 -t 1"

2. Elegir motor y justificar:

Eleccion: PostgreSQL. Sí me importa parecerme a lo que usa OHDSI y considero importante prácticar los estándares de la industria. Aunque estoy trabajando en jupyter, por lo cual seria mas conveniente trabajar con DuckDB mediante un import (en vez de mantener mi docker corriendo en segundo plano para tener conectado un container con postgres), me parece que DuckDB es más sencillo y directo, así que no tendría problema en implementarlo si fuera necesario una vez que haya dominado PostgreSQL. 


3. Cargar de forma reproducible:

Conteos de filas por archivo (copiado desde mi notebook:)
|Table|Row count|
|-----|---------|
|conditions|409025|
|encounters|664215|
|medications|551355|
|observations|8603991|
|patients|11122|

7. EL join que multiplica:

Explicacion: si a un paciente se le diagnostican 3 condiciones en un mismo encuentro, el JOIN separa estos diagnosticos en 3 filas individuales con el mismo encounter_id. Esto ocasiona que tanto el conteo como el promedio de encuentros tomen el 3 para ese paciente en particular, cuando en realidad solo tiene un encuentro verdadero. Esto se corrige al agregar antes de hacer el join, de manera que se agrupe por encuenter_id y ese paciente en particular solo aporta 1 visita verdadera al conteo.

8. La trampa del LEFT JOIN

- a) numero de filas con el filtro en el WHERE: 198
- b) numero de filas con el filtro en el ON: 11122
Explicacion: en el escenario a), como se lleva a cabo primero el LEFT JOIN, se unen las condiciones y a los pacientes que no cuentan con la condicion filtro se les deja con NULL. Despues se ejecuta el WHERE y estos NULLs son excluidos de la tabla final ya que no coincide con la condicion filtro, ocasionando que el conteo de pacientes incluya unica y estrictamente a los pacientes diagnosticados con esa condicion. Si el punto de la consulta fuera separar una poblacion epileptica (o cualquier otra condicion) y comparar contra una poblacion control, no podriamos llevar a cabo el analisis.
En cambio, en el escenario b), el filtro es evaluado durante el LEFT JOIN, ocasionando que la columna que describe la condicion mantenga NULL en los pacientes no diagnosticados con la condicion de filtrado. En este caso si se pueden realizar comparaciones entre poblaciones.


9. Medir el rendimiento.

| Escenario | Plan | Execution time |
|-----------|------|----------------|
| Original (obtener primer y ultimo encuentros por paciente) | Parallel Seq Scan on encounters | Execution Time: 75.964 ms |
| Repetir tras agregar indice | Parallel Index Only Scan using idx_encounters_patient_date on encounters | Execution Time: 384.355 ms|

Explicacion: al agregar el indice, ocasionamos que el sequential scan pase a ser un index scan. Esto seria util si nuestra consulta requiriera recorrer toda la tabla para filtrar un resultado especifico (como vimos en el ejemplo WHERE person_id = 4242). Pero la operacion que estamos solicitando (obtener primer y ultimo encuentros por paciente) de cualquier manera exige recorrer toda la tabla, la cual ahora tambien contiene la estructura del indice. En este caso, agregar el indice ocasiona que incremente el tiempo de ejecución casi 5 veces.


10. SQL contra Pandas

| Pregunta | Lineas de codigo (SQL vs Pandas) | Tiempo (SQL vs Pandas) |
|----------|------------------|-------------|
| Pacientes nacidos antes de 1960 | 3 vs 1 | 2.276 ms vs 2.06 ± 0.0368 ms |
| Distribucion de un analito | 12 vs 15 | 2450 ms vs 919 ± 160 ms |
| Pacientes diabeticos pero sin mediciones de hba1c | 7 vs 7 |  2174.115 ms vs 1.01 s ± 67.6 ms |

Explicacion: para agregaciones sencillas, como la pregunta sobre la fecha de nacimiento, ambos motores parecen tener eficiencia parecida. Pero para operaciones tanto de texto como numéricas, Pandas fue mas eficiente. Es posible que la agregacion sea demasiado sencilla como para que se haga evidente una diferencia entre los motores. También es posible que los tiempos de ambos motores cambien si se optimizaran los dtypes de cada base de datos, ya que solo asigne dtypes especificos para fechas. Por otro lado, SQL parece tener la ventaja en cuanto a legibilidad, ya que su sintaxis es bastante sencilla y leible como lenguaje humano. Para este volumen y volumenes mayores, buscaria hacer una division de las tareas: preparar funciones que usen SQL para hacer agregaciones complicadas, considerando agregar un indice cuando sea conveniente. Y preparar funciones de Pandas para operaciones de texto y/o numericas, asi como para graficar.