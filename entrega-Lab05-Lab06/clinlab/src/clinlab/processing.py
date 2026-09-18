import pandas as pd


def process_encounters(enc: pd.DataFrame) -> pd.DataFrame:
    """
    UDF para leer cambiar encounters.csv con dtypes especificos para optimizar memoria
    recibe enc: pandas Dataframe "crudo" de encounters.csv, como lo devuelve pd.read_csv
    devuelve enc: pandas DF procesado
    """
    enc = enc.astype(
        {
            "Id": "category",
            "PATIENT": "category",
            "ORGANIZATION": "category",
            "PROVIDER": "category",
            "PAYER": "category",
            "ENCOUNTERCLASS": "category",
            "CODE": "category",
            "DESCRIPTION": "category",
            "BASE_ENCOUNTER_COST": "float32",
            "TOTAL_CLAIM_COST": "float32",
            "PAYER_COVERAGE": "float32",
            "REASONCODE": "float64",
            "REASONDESCRIPTION": "category",
        }
    )
    enc.columns = enc.columns.str.lower()
    enc = enc.assign(
        start=pd.to_datetime(enc["start"], utc=True, errors="coerce").dt.tz_localize(
            None
        ),
        stop=pd.to_datetime(enc["stop"], utc=True, errors="coerce").dt.tz_localize(
            None
        ),
    ).rename(
        columns={
            "id": "encounter",
            "description": "enc_desc",
            "code": "enc_code",
            "start": "enc_start",
            "stop": "enc_stop",
        }
    )
    return enc


def process_observations(obs: pd.DataFrame) -> pd.DataFrame:
    """
    UDF para cambiar archivo observations.csv con dtypes especificos para optimizar memoria
    recibe obs: pd.DataFrame crudo, como lo devuelve pd.read_csv
    devuelve obs: pd.DataFrame procesado
    """
    obs = obs.astype(
        {
            "PATIENT": "category",
            "ENCOUNTER": "category",
            "DESCRIPTION": "category",
            "VALUE": "string",
            "UNITS": "string",
            "CODE": "category",
            "TYPE": "category",
        }
    )
    obs.columns = obs.columns.str.lower()
    obs = (
        obs.assign(
            units=obs.units.fillna("other").astype("category"),
            num_val=pd.to_numeric(obs["value"], errors="coerce").astype("float32"),
            non_num_val=lambda df: df["value"]
            .where(df["units"] == "other", None)
            .astype("category"),
            date=pd.to_datetime(obs["date"], utc=True, errors="coerce").dt.tz_localize(
                None
            ),
        )
        .drop(columns=["type", "value"])
        .rename(
            columns={"description": "obs_desc", "code": "obs_code", "date": "obs_date"}
        )
    )
    return obs


def process_patients(pat: pd.DataFrame) -> pd.DataFrame:
    """
    UDF para cambiar archivo patients.csv con dtypes especificos para optimizar memoria
    recibe pat: pandas Dataframe "crudo" de patients.csv, como lo devuelve pd.read_csv
    devuelve pat: pd.DataFrame procesado
    """
    pat = pat[
        [
            "Id",
            "BIRTHDATE",
            "DEATHDATE",
            "SSN",
            "RACE",
            "ETHNICITY",
            "GENDER",
            "BIRTHPLACE",
            "LAT",
            "LON",
            "HEALTHCARE_EXPENSES",
            "HEALTHCARE_COVERAGE",
        ]
    ].astype(
        {
            "Id": "category",
            "BIRTHPLACE": "category",
            "RACE": "category",
            "ETHNICITY": "category",
            "GENDER": "category",
            "LAT": "float32",
            "LON": "float32",
            "HEALTHCARE_EXPENSES": "float32",
            "HEALTHCARE_COVERAGE": "float32",
            "SSN": "string",
        }
    )
    pat.columns = pat.columns.str.lower()
    pat = (
        pat.assign(
            ssn=pat.ssn.str.replace("-", "", regex=False).astype("int32"),
            birthdate=pd.to_datetime(
                pat["birthdate"], utc=True, errors="coerce"
            ).dt.tz_localize(None),
            deathdate=pd.to_datetime(
                pat["deathdate"], utc=True, errors="coerce"
            ).dt.tz_localize(None),
        ).rename(columns={"id": "patient"})  # para igualar el nombre de las columnas)
    )
    return pat


def merge_full(pat: pd.DataFrame, enc: pd.DataFrame, obs: pd.DataFrame) -> pd.DataFrame:
    """
    UDF para generar dataFrame "full" que contiene el merge de los archivos patients, encounters y observations
    recibe pat, enc, obs: pd.DataFrames procesados mediante process_patients, _encounters, _observations respectivamente
    devuelve full: pd.DataFrame de los dataFrames unidos y validados
    """
    full = enc.merge(
        obs,  # para corregur issue1:
        on=[
            "patient",
            "encounter",
        ],  # aqui meto un bug intencionalmente para corregirlo despues, deberia...
        how="left",  # ...ser ['patient', 'encounter'] y de esta manera se duplicara la columna patient
        validate="1:m",
        indicator=True,
    )
    full = (
        full.drop(columns={"_merge"}).merge(
            pat,
            # left_on = 'patient_x', # al corregir el issue de arriba tambien debo cambiar aqui
            on="patient",  # originalmente era solo on = 'patient', sin left o right
            how="left",  # para issue2 (perf)
            validate="m:1",  # aqui en indicator hace que me sobre la columna _merge que no es...
            indicator=False,
        )  # ...necesaria para el analisis. No es bug pero puede entrar como issue
    )
    return full
