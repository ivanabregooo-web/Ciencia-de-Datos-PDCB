9. Caracterizar:

Tabla 1:

|Componente|Medida|
|----------|------|
|total_patients|42|
|median_age_years|13.0|
|q25_age|6.25|
|q75_age|17.25|
|count_female|17|
|count_male|25|
|median_follow_up_days|30.0|
|q25_follow_up|30.0|
|q75_follow_up|179.5|


10. Buscar tu propio inmortal time:

Si estaba cayendo en este sesgo, al incluir como criterio de inclusion que tuvieran monoterapia de Medicamentos Anti Epileptico (MAE). Si un paciente era diagnosticado con epilepsia, pero no recibia el MAE, se introduce el sesgo. Lo corregi marcando la fecha de entrada a la cohorte como la fecha en que reciben el MAE, en vez de la fecha en que son diagnosticados con epilepsia. Esto cambio los resultados del histograma de duracion en cohorte (comparar figura 6 contra figura 10), revelando que muchos pacientes tenian duracion de 0 dias en la cohorte, debido a que Synthea genera varios pacientes con una sola prescripcion en la que su days supply quedaba en 0. Para corregir esto, agregue una suposicion en la cual si recibieron la prescripcion pero su start_date y end_date son iguales, se asume un days_supply de 30 dias, asumiendo que los pacientes hayan tomado es unica prescripcion que recibieron. Esto modifico la mediana de seguimiento desde 151 dias (con el sesgo) hasta 30 dias (con la correcion).