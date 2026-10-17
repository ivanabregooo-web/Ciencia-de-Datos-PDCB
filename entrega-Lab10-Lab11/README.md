Para reproducir el analisis en el jupyter notebook:

- docker necesario para conectar con postgres. Desde la terminal (anaconda prompt), ubicado en la misma carpeta donde el archivo .env este ubicado:
	>docker run --rm --name my_postgres --env-file .env -p 5432:5432 -d postgres:15.4
- plugin para usar comando magico %%sql dentro del notebook y poder usar directamente comandos de sql sin usar comillas:
	> pip install jupysql
Al finalizar:
	>docker stop my_postgres

*Entrega Lab10:*



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



*Entrega Lab11:*



1. De anidado a legible:

Nota: cuando hice el lab10 no habia notado que esta actividad requeria reescribir consultas anidads como CTEs, y escribi algunas como CTEs desde el inicio. Entonces, para hacer la comparacion, hice la actividad al reves, rescribiendo mis consultas en CTEs como anidadas.

a) rehacer consulta 6: numero medio y mediano de encuentros por paciente
La diferencia mas grande es que la consulta anidada (fig 1_1, izquierda) solicita primero que se hagan los calculos matematicos (ROUND, PERCENTILE) y despues especifica la seleccion de tabla agrupada sobre la cual se hacen. Por el contrario, la consulta hecha con CTEs (fig 1_1, derecha) usa el comando WITH para establecer primero la seleccion agrupada y posteriormente realiza los calculos. En lo personal, prefiero la sintaxis de la consulta con CTEs, ya que al escribir (o releer) la consulta, se me hace mas legible o con un "logica mas humana" tomar primero la seleccion de la tabla y sobre eso hacer los calculos. Pero es una preferencia personal. Para esta consulta especifica, no veo una diferencia significativa entre la legibilidad de ambos metodos.

b) encuentro la misma logica para la consulta 12: pacientes diabeticos pero sin mediciones de hba1c. Al hacer la consulta anidada (fig 1_2, izquierda), se solicita primero el conteo y despues se establece la sub-tabla sobre la cual hacer dicho conteo, utilizando un comando EXCEPT para hacer un tipo de anti join. Por el contrario, la misma consulta en CTEs (fig 1_2, derecha) envuelve la primera seleccion en un with y sobre esa lleva a cabo el antijoin. Para este par de consultas sencillas, la diferencia en legibilidad entre consultas anidadas y CTEs no se hace tan evidente. Sin embargo, a mi parecer, CTEs tienen la ventaja en cuanto a la sintaxis logica con la cual se le dan instrucciones a SQL.



3. Primera y ultima visita por paciente

Definitivamente prefiero la consulta hecha con GROUP BY (fig 3_1). La consulta hecha con FIRST_VALUE y LAST_VALUE (fig 3_1) requiere pasos intermedios y redundantes para hacerla funcionar, como PARTITION BY y ORDER BY en cada operacion. Ademas requiere que uno se acuerde de agregar DISTINCT al SELECT para que agrupe por paciente y ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING dentro del LAST VALUE para que la ventana se actualice correctamente. En cambio, GROUP BY automaticamente maneja los PARTITION BY, y puede usar MIN/MAX para manejar los ORDER BY en una sola linea en vez de repetirlos en cada operacion. Tambien hace el SELECT DISTINCT por default. GROUP BY es mucho menos redundante, exige menos operaciones intermedias, tiene una sintaxis mas corta, exige que se recuerden menos detalles particulares y es mucho mas legible en lenguaje humano.



4. Dias entre visitas consecutivas

- La primera visita de cada paciente devuelve NULL porque no hay visita 0, no hay contra que comparar. Si esta bien.
- Para el calculo de la mediana, use IS NOT NULL para omitirlos.



5. Readmision a 30 Dias

Decisiones:
- Estoy contando todas las readmisiones (de hecho las muestro por paciente)
- El dia 30 no cuenta: se me hace plausible que despues de un alta hospitalaria, la indicacion del medico pudiera ser "vuelve en 1 mes para darte seguimiento". Por lo tanto, dejo el limite entre 0 y 29.



6. Gaps and islands:

Explicacion: el histograma cambia enormemente al cambiar la persistencia. Con 30 dias, encontramos una distribucion exponencial, encontrado la mayoria de las observaciones para episodios de tratamiento de pocos dias. Pero oculta las observaciones de conteo muy bajo para episodios largos, de mas de 250 dias. Por el contrario, con persistencia de 30 y 90 dias, los grandes conteos de tratamientos de pocos dias se colapsan en un solo bin y encontramos algo mas parecido a una distribucion uniforme para duraciones de episodios desde 0 hasta 2000 dias.



7. Deduplicar con ROW_NUMBER

Analito elegido para las pruebas: 'Hemoglobin A1c/Hemoglobin.total in Blood'
Con la deduplicacion bajamos de 89080 a 4782 observaciones, que corresponden unicamente a la ultima observacion de cada paciente. 

No se puede usar rn = 1 dentro del WHERE por la misma logica de ejecucion de operaciones de SQL. Primero se ejecuta primero el FROM, luego el WHERE de filtrado, luego se usan las window functions y finalmente el select.



10. Rendimiento: ventana contra join

| Plan | Tiempo (ms) | Legibilidad |
|------|--------|-------------|
| LAG | 990.705 | mayor |
| JOIN | 14094.937 | menor |

En este caso, encuentro la sintaxis de la window function mas legible y mas parecida al "lenguaje humano" que la version con join. Ademas, la version con el join fue aprox 14 veces mas lenta.
