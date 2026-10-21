SELECT 
    concept_id,
    concept_name,
    domain_id,
    vocabulary_id,
    concept_code,
    0 AS min_levels_of_separation
FROM public.concept
WHERE concept_id = 380378 -- 4029498
    AND invalid_reason IS NULL;