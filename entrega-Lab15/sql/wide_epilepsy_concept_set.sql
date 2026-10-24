SELECT 
    c.concept_id,
    c.concept_name,
    c.domain_id,
    c.vocabulary_id,
    c.concept_code,
    ca.min_levels_of_separation
FROM public.concept_ancestor ca
JOIN public.concept c 
    ON ca.descendant_concept_id = c.concept_id
WHERE ca.ancestor_concept_id = 4029498 -- 380378
    AND c.invalid_reason IS NULL
ORDER BY ca.min_levels_of_separation ASC, c.concept_name;