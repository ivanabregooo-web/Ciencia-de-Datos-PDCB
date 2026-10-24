-- define al ingrediente 'simvastatin' a partir de todas las exposiciones a medicamentos
-- que tienen simvastatina o simvastatina + otro medicamento
-- devuelve: 5 conceptos
-- version de vocabulario: RxNorm 20260601
-- fecha: 23/10/2026
-- decisiones: se omitieron presentaciones de simvastatin de 40 MG


WITH metformin_ingredient AS (
    SELECT concept_id, concept_name
    FROM public.concept
    WHERE LOWER(concept_name) = 'simvastatin'
      AND concept_class_id = 'Ingredient'
      AND standard_concept = 'S'
      AND vocabulary_id = 'RxNorm'
      AND invalid_reason IS NULL
    LIMIT 1
),
metformin_candidate_products AS (
    SELECT DISTINCT
        ca.descendant_concept_id AS drug_concept_id
    FROM metformin_ingredient mi
    JOIN public.concept_ancestor ca 
        ON mi.concept_id = ca.ancestor_concept_id
),
all_metformin_products AS (
    SELECT 
        mcp.drug_concept_id,
        COUNT(DISTINCT c_ing.concept_id) AS ingredient_count,
        STRING_AGG(c_ing.concept_name, ' + ' ORDER BY c_ing.concept_name) AS all_ingredients
    FROM metformin_candidate_products mcp
    JOIN public.concept_ancestor ca 
        ON mcp.drug_concept_id = ca.descendant_concept_id
    JOIN public.concept c_ing 
        ON ca.ancestor_concept_id = c_ing.concept_id
    WHERE c_ing.concept_class_id = 'Ingredient'
      AND c_ing.standard_concept = 'S'
    GROUP BY mcp.drug_concept_id
)
SELECT 
    c_prod.concept_id AS drug_concept_id,
    c_prod.concept_name AS drug_name,
    amp.ingredient_count,
    amp.all_ingredients,
    COUNT(DISTINCT de.person_id) AS patient_count,
    COUNT(de.drug_exposure_id) AS total_exposures
FROM all_metformin_products amp
JOIN public.concept c_prod 
    ON amp.drug_concept_id = c_prod.concept_id
JOIN public.drug_exposure de 
    ON amp.drug_concept_id = de.drug_concept_id
GROUP BY 
    c_prod.concept_id,
    c_prod.concept_name,
    amp.ingredient_count,
    amp.all_ingredients
ORDER BY patient_count DESC;