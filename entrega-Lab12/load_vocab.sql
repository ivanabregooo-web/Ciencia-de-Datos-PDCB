COPY public.concept FROM '/workspace/omop_vocabularies/CONCEPT.csv' WITH (FORMAT CSV, DELIMITER E'\t', HEADER, QUOTE E'\b');
COPY public.vocabulary FROM '/workspace/omop_vocabularies/VOCABULARY.csv' WITH (FORMAT CSV, DELIMITER E'\t', HEADER, QUOTE E'\b');
COPY public.domain FROM '/workspace/omop_vocabularies/DOMAIN.csv' WITH (FORMAT CSV, DELIMITER E'\t', HEADER, QUOTE E'\b');
COPY public.concept_class FROM '/workspace/omop_vocabularies/CONCEPT_CLASS.csv' WITH (FORMAT CSV, DELIMITER E'\t', HEADER, QUOTE E'\b');
COPY public.concept_relationship FROM '/workspace/omop_vocabularies/CONCEPT_RELATIONSHIP.csv' WITH (FORMAT CSV, DELIMITER E'\t', HEADER, QUOTE E'\b');
COPY public.concept_synonym FROM '/workspace/omop_vocabularies/CONCEPT_SYNONYM.csv' WITH (FORMAT CSV, DELIMITER E'\t', HEADER, QUOTE E'\b');
COPY public.concept_ancestor FROM '/workspace/omop_vocabularies/CONCEPT_ANCESTOR.csv' WITH (FORMAT CSV, DELIMITER E'\t', HEADER, QUOTE E'\b');
COPY public.drug_strength FROM '/workspace/omop_vocabularies/DRUG_STRENGTH.csv' WITH (FORMAT CSV, DELIMITER E'\t', HEADER, QUOTE E'\b');