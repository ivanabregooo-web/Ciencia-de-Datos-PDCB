COPY native.patients FROM '/workspace/synthea_data/patients.csv' WITH (FORMAT CSV, HEADER);
COPY native.encounters FROM '/workspace/synthea_data/encounters.csv' WITH (FORMAT CSV, HEADER);
COPY native.conditions FROM '/workspace/synthea_data/conditions.csv' WITH (FORMAT CSV, HEADER);
COPY native.observations FROM '/workspace/synthea_data/observations.csv' WITH (FORMAT CSV, HEADER);
COPY native.medications FROM '/workspace/synthea_data/medications.csv' WITH (FORMAT CSV, HEADER);
COPY native.procedures FROM '/workspace/synthea_data/procedures.csv' WITH (FORMAT CSV, HEADER);
COPY native.immunizations FROM '/workspace/synthea_data/immunizations.csv' WITH (FORMAT CSV, HEADER);
COPY native.allergies FROM '/workspace/synthea_data/allergies.csv' WITH (FORMAT CSV, HEADER);
COPY native.careplans FROM '/workspace/synthea_data/careplans.csv' WITH (FORMAT CSV, HEADER);
COPY native.devices FROM '/workspace/synthea_data/devices.csv' WITH (FORMAT CSV, HEADER);
COPY native.imaging_studies FROM '/workspace/synthea_data/imaging_studies.csv' WITH (FORMAT CSV, HEADER);
COPY native.providers FROM '/workspace/synthea_data/providers.csv' WITH (FORMAT CSV, HEADER);
COPY native.organizations FROM '/workspace/synthea_data/organizations.csv' WITH (FORMAT CSV, HEADER);


