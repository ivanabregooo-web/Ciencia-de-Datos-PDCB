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
WHERE ca.ancestor_concept_id = 4029498 -- 315021
  AND c.invalid_reason IS NULL
  AND c.concept_id NOT IN (
  37160959,
  37472166,
  762729,
  36674191,
  37156904,
  44783583,
  37160838,
  4046219,
  37205773,
  37167962,
  137613
  )
ORDER BY ca.min_levels_of_separation ASC, c.concept_name;