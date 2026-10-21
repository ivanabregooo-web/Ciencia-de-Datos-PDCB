WITH target_concepts AS (
    SELECT UNNEST(:concept_ids::int[]) AS concept_id
),
ranked_diagnoses AS (
    SELECT 
        co.person_id,
        co.condition_concept_id,
        c.concept_name AS condition_name,
        co.condition_start_date AS index_date,
        ROW_NUMBER() OVER (
            PARTITION BY co.person_id 
            ORDER BY co.condition_start_date ASC, co.condition_occurrence_id ASC
        ) AS rn,
        COUNT(*) OVER (PARTITION BY co.person_id) AS total_occurrences
    FROM public.condition_occurrence co
    JOIN target_concepts tc 
        ON co.condition_concept_id = tc.concept_id
    JOIN public.concept c 
        ON co.condition_concept_id = c.concept_id
)
SELECT 
    person_id,
    index_date,
    condition_concept_id AS index_concept_id,
    condition_name AS index_concept_name,
    total_occurrences
FROM ranked_diagnoses
WHERE rn = 1
ORDER BY index_date ASC, person_id;