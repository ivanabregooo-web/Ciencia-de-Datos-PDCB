DROP TABLE IF EXISTS conditions;
CREATE TABLE conditions (
	condition_start DATE,
	condition_stop DATE,
	patient_id TEXT,
	encounter_id TEXT,
	system TEXT,
	condition_code TEXT,
	condition_description TEXT
);

DROP TABLE IF EXISTS encounters;
CREATE TABLE encounters (
	encounter_id TEXT,
	encounter_start DATE,
	encounter_stop DATE,
	patient_id TEXT,
	organization TEXT,
	encounter_provider TEXT,
	encounter_payer TEXT,
	encounterclass TEXT,
	encounter_code TEXT,
	encounter_description TEXT,
	base_encounter_cost FLOAT,
	total_claim_cost FLOAT,
	encounter_payer_coverage FLOAT,
	encounter_reasoncode TEXT,
	encounter_resondescription TEXT
);

DROP TABLE IF EXISTS medications;
CREATE TABLE medications (
	medication_start DATE,
	medication_stop DATE,
	patient_id TEXT,
	medication_payer TEXT,
	encounter_id TEXT,
	medication_code TEXT,
	medication_description TEXT,
	base_medication_cost FLOAT,
	medication_payer_coverage FLOAT,
	medication_dispenses INT,
	medication_totalcost FLOAT,
	medication_reasoncode TEXT,
	medication_reasondescription TEXT
);

DROP TABLE IF EXISTS observations;
CREATE TABLE observations (
	observation_date DATE,
	patient_id TEXT,
	encounter_id TEXT,
	observation_category TEXT,
	observation_code TEXT,
	observation_description TEXT,
	observation_value TEXT,
	observation_units TEXT,
	observation_units_type TEXT
);

DROP TABLE IF EXISTS patients;
DROP TYPE IF EXISTS gender_type;
CREATE TYPE gender_type AS ENUM ('M', 'F');


CREATE TABLE patients (
	patient_id TEXT,
	patient_birthdate DATE,
	patient_deathdate DATE,
	ssn TEXT,
	drivers TEXT,
	passport TEXT,
	p_prefix TEXT,
	p_first TEXT,
	p_middle TEXT,
	p_last TEXT,
	p_suffix TEXT,
	p_maiden TEXT,
	p_marital TEXT,
	race TEXT,
	ethnicity TEXT,
	gender gender_type,
	birthplace TEXT,
	address TEXT,
	city TEXT,
	p_state TEXT,
	county TEXT,
	fips FLOAT,
	zip INT,
	lat FLOAT,
	lon FLOAT,
	healthcare_expenses FLOAT,
	healthcare_coverage FLOAT,
	income INT
);


