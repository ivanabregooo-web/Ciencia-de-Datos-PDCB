1. Explorar antes de programar:

| API | Endpoint | Parámetros clave | ¿Cómo página? | ¿Límite de tasa? |
|-----|----------|------------------|---------------|------------------|
| NCBI e-utilities (PubMed)| einfo.fcgi |db, term, id, retmode, rettype, usehistory | usando usehistory retstart y retmax, se extraen resultados por lotes y el resto se mantiene cacheado en sus servidores | 3 requests por segundo, 10 con la llave |
| ClinicalTrials.gov | studies | query.cond, query.intr, query.term, fields, pageSize | usando pageSize y pageToken, se extrae cierta cantidad de estudios y se va a apuntando al siguiente lote | no tiene como tal pero pageSize tiene un máximo de 1000 estudios devueltos por página |
| OpenFDA | drug | search, count, limit, skip, sort | usando skip y limit, te va devolviendo links que apuntan a la siguiente página | 240 por minuto, máximo 1000 al día |


2. Una petición decente:

- Al no usar raise_for_status (fig. 2_1), una petición inexistente no arroja ningún tipo de error y solo devuelve un diccionario vacío.
- Al usar params incorrectamente, pero sin usar raise_for_status (fig. 2_2), sale un error raro tipo JSONDecodeError que no es intuitivo de identificar y por lo tanto debuggear. El mismo uso inadecuado de params pero usando raise_for_status (fig. 2_3) maneja el error y lo traduce a in HTTPError que en el que fácilmente se identifica que el error es de parte del cliente y la request está mal construida.

4. El cliente robusto:

| Código | ¿Se reintenta? |
|--------|----------------|
| 400 | no, la petición está mal formada, es error del usuario |
| 401 | no, hace falta autenticar o no se tiene permiso, es error del usuario |
| 404 | no, no existe respuesta, es error del usuario |
| 429 | sí, es error del usuario por hacer demasiadas peticiones, pero el Retry con exponential backoff y respetando el retry after lo maneja |
| 500<br>503<br>504  | sí, son errores del servidor |

5. Guardar el crudo:

Parametros usados y fecha de descarga (guardado como metadatos en el mismo archivo .json de los datos crudos):

"metadata": {
        "download_date": "2026-09-28T20:26:43.729897",
        "source_url": "https://clinicaltrials.gov/api/v2/studies",
        "parameters": {
            "query.cond": "epilepsy",
            "pageSize": 300
Importante para la reproducibilidad porque tanto los parámetros usados como la fecha de descaraga pueden cambiar enormemente los registros recuperados.

6. Validar en la frontera

| Fuente | Registros conservados (/300) | Ejemplo fallo en validacion |
|--------|------------------------------|---------------|
| ClinicalTrials | 299 | el ensayo fue marcado como completado pero tenía enrollment de 0 |
| OpenFDA | 270 | FDA registra el genero(+) como 1 (male), 2 (female) o 0 (unknown). Defini una validacion para desahcerse de los 0's ya que los rangos fisiológicos de algunas variables dependenden del genero y mantener registros con genero desconocido puede introducir artefactos |

+: https://open.fda.gov/apis/drug/event/searchable-fields/

9. Medir la cortesía:
El conteo lo hice sobre clinical trials, que fue la base de datos sobre la que más peticiones hice. En la figura 9 muestro que se hicieron 11 peticiones totales, de las cuales 0 fueron reales y 11 fueron manejadas por la cache. Supongo que sto se debe a que el conteo lo implemente dentro de la clase que defini para extraer los ensayos clinicos, para la actividad inicio del notebook, en las pruebas sobre la actvidad 4 del cliente robusto. Pero la primera peticion que hago en el notebook se hace al inicio para la actividad 3 de medición de memoria al paginar. Esto quiere decir que en realidad se trata de una sola peticion real a partir de la cual el cache provee los datos para el resto del notebook. Como solo se trata de una llamada real y el resto son manejadas por la cache, si 1000 personas corrieran el script a la vez, no creo que se tumbaría el servicio.