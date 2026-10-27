Pregunta utilizada: pacientes unicos diagnosticados con epilepsia

|Metodo|Corrida 1|Corrida 2|Corrida 3|Mediana|
|------|---------|---------|---------|-------|
|subconsulta sobre CONCEPT_ANCESTOR|388.648 ms|53.112 ms|27.133 ms|Corrida 2|
|tabla e indice|74.144 ms|51.791 ms|23.483 ms|Corrida 2|

En este caso la diferencia es demasiado sutil como para ser significativa. Aunque entiendo el valor agregado el indice sobre los tiempos de ejecucion se encuentra al evitar realizar un sequential scan sobre tablas completas, en este caso las tablas a recorrer son demasiado pequeñas (en terminos de sql) como para que la diferencia en tiempos sea importante. Esto se ve reflejado en los tiempos medianos reportados para cada version de la consulta. No obstante, cabe mencionar que aunque ambas consultas son extremadamente rapidas (rango de milisegundos), la consulta hecha con tabla e indice arrojo tiempos menores desde la primera corrida comparado con la subconulta sobre concept_ancestor.