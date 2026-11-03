WITH epilepsy_concepts AS (
    SELECT descendant_concept_id AS concept_id
    FROM public.concept_ancestor
    WHERE ancestor_concept_id = (
        SELECT concept_id FROM public.concept 
        WHERE LOWER(concept_name) = 'epilepsy' AND standard_concept = 'S' LIMIT 1
    )
),
aed_concepts AS (
    SELECT descendant_concept_id AS concept_id
    FROM public.concept_ancestor
    WHERE ancestor_concept_id = (
        SELECT concept_id FROM public.concept 
        WHERE LOWER(concept_name) = 'antiepileptics' AND vocabulary_id = 'ATC' LIMIT 1
    )
),
initial_event AS (
    SELECT co.person_id, MIN(co.condition_start_date) AS index_date
    FROM public.condition_occurrence co
    JOIN epilepsy_concepts ec ON co.condition_concept_id = ec.concept_id
    GROUP BY co.person_id
),
patient_aed_exposures AS (
    SELECT 
        ie.person_id, 
        ie.index_date,
        de.drug_concept_id,
        de.drug_exposure_start_date,
        de.drug_exposure_end_date
    FROM initial_event ie
    JOIN public.drug_exposure de ON ie.person_id = de.person_id
    JOIN aed_concepts ac ON de.drug_concept_id = ac.concept_id
    WHERE de.drug_exposure_start_date >= ie.index_date
),
inclusion_criteria AS (
    SELECT 
        pae.person_id, 
        pae.index_date, 
        MIN(pae.drug_exposure_start_date) AS monotherapy_start_date,
        MAX(pae.drug_concept_id) AS primary_aed_concept_id
    FROM patient_aed_exposures pae
    WHERE pae.drug_exposure_start_date = (
        SELECT MIN(drug_exposure_start_date) 
        FROM patient_aed_exposures p2 
        WHERE p2.person_id = pae.person_id
    )
    GROUP BY pae.person_id, pae.index_date
    HAVING COUNT(DISTINCT pae.drug_concept_id) = 1
),
exit_strategy AS (
    SELECT 
        ic.person_id,
        MAX(CASE WHEN pae.drug_concept_id = ic.primary_aed_concept_id 
                 THEN pae.drug_exposure_end_date END) AS abandonment_date,
        MIN(CASE WHEN pae.drug_concept_id <> ic.primary_aed_concept_id 
                 THEN pae.drug_exposure_start_date END) AS polytherapy_date
    FROM inclusion_criteria ic
    LEFT JOIN patient_aed_exposures pae ON ic.person_id = pae.person_id
    GROUP BY ic.person_id
),
censorship AS (
    SELECT 
        op.person_id, 
        d.death_date,
        MAX(op.observation_period_end_date) AS observation_end_date
    FROM public.observation_period op
    LEFT JOIN public.death d ON op.person_id = d.person_id
    GROUP BY op.person_id, d.death_date
),
cohort_a_final AS (
    SELECT 
        ic.person_id,
        ic.index_date,
        ic.monotherapy_start_date,
        ic.primary_aed_concept_id,
        LEAST(
            es.abandonment_date, 
            es.polytherapy_date, 
            c.death_date, 
            c.observation_end_date
        ) AS cohort_exit_date,
        CASE 
            WHEN LEAST(es.abandonment_date, es.polytherapy_date, c.death_date, c.observation_end_date) = es.polytherapy_date THEN 'Polytherapy'
            WHEN LEAST(es.abandonment_date, es.polytherapy_date, c.death_date, c.observation_end_date) = c.death_date THEN 'Death'
            WHEN LEAST(es.abandonment_date, es.polytherapy_date, c.death_date, c.observation_end_date) = c.observation_end_date THEN 'Observation Ended'
            ELSE 'Treatment Abandoned'
        END AS exit_reason
    FROM inclusion_criteria ic
    JOIN exit_strategy es ON ic.person_id = es.person_id
    JOIN censorship c ON ic.person_id = c.person_id
)
SELECT * FROM cohort_a_final
ORDER BY index_date;