import matplotlib
import numpy as np
import pandas as pd
import pytest

from clinlab.processing import merge_full

matplotlib.use("Agg")


@pytest.fixture
def empty_df() -> pd.DataFrame:
    """df vacio"""
    return pd.DataFrame()


@pytest.fixture
def corrupt_patients() -> pd.DataFrame:
    """df malicioso de pacientes"""
    return pd.DataFrame(
        {
            "patient": [
                "p001",
                "p002",
                "p002",
                "p003",
                "p004",
                "p005",
            ],
            "gender": ["M", "F", "F", "X", "M", "M"],
            "age": [26, 32, 32, 12, 180, 24],
            "birthdate": [
                pd.to_datetime(i)
                for i in (
                    "2000-01-01",
                    "1994-01-01",
                    "1994-01-01",
                    "2014-01-01",
                    "1954-01-01",
                    "2002-01-01",
                )
            ],
            "deathdate": [pd.NaT] * 6,
        }
    )


@pytest.fixture
def corrupt_encounters() -> pd.DataFrame:
    """df malicioso de encuentros"""
    return pd.DataFrame(
        {
            "encounter": [
                "e101",
                "e102",
                "e201",
                "e202",
                "e301",
                "e302",
                "e401",
                "e402",
                "e501",
                "e502",
            ],
            "patient": [
                "p001",
                "p001",
                "p002",
                "p002",
                "p003",
                "p003",
                "p004",
                "p004",
                "p005",
                "p005",
            ],
            "start": [
                pd.to_datetime(i)
                for i in (
                    "2020-01-01 08:10:00",
                    "2020-02-02 08:10:00",
                    "2015-01-01 08:20:00",
                    "2015-02-02 08:20:00",
                    "2004-01-01 08:30:00",
                    "2024-02-02 08:30:00",  # fecha imposible aqui -> 2004
                    "2018-01-01 08:40:00",
                    "2018-02-02 08:40:00",
                    "2025-01-01 08:50:00",
                    "2025-02-02 08:50:00",
                )
            ],
            "stop": [
                pd.to_datetime(i)
                for i in (
                    "2020-01-01 08:15:00",
                    "2020-02-02 08:15:00",
                    "2015-01-01 08:25:00",
                    "2015-02-02 08:25:00",
                    "2004-01-01 08:35:00",
                    "2024-02-02 08:35:00",  # fecha imposible aqui -> 2004
                    "2018-01-01 08:45:00",
                    "2018-02-02 08:45:00",
                    "2025-01-01 08:55:00",
                    "2025-02-02 08:55:00",
                )
            ],
        }
    )


@pytest.fixture
def corrupt_observations() -> pd.DataFrame:
    """df malicioso para observaciones"""
    return pd.DataFrame(
        {
            "obs_date": [
                pd.to_datetime(i)
                for i in (
                    "2020-01-01",
                    "2020-02-02",
                    "2015-01-01",
                    "2015-02-02",
                    "2004-01-01",
                    "2024-02-02",  # fecha imposible aqui -> 2004
                    "2018-01-01",
                    "2018-02-02",
                    "2025-01-01",
                    "2025-02-02",
                )
            ],
            "patient": [
                "p001",
                "p001",
                "p002",
                "p002",
                "p003",
                "p003",
                "p004",
                "p004",
                "p005",
                "p005",
            ],
            "encounter": [
                "e101",
                "e102",
                "e201",
                "e202",
                "e301",
                "e302",
                "e401",
                "e401",
                "e501",
                "e502",
            ],
            "obs_desc": [
                "hemoglobin",
                "blood pressure",
                "hemoglobin",
                "blood pressure",
                "hemoglobin",
                "blood pressure",
                "hemoglobin",
                "blood pressure",
                "hemoglobin",
                "blood pressure",
            ],
            "num_val": [
                np.nan,
                117,
                np.nan,
                118,
                np.nan,
                119,
                np.nan,
                120,
                np.nan,
                121,
            ],
        }
    )


@pytest.fixture
def clean_corrupt_full(
    corrupt_patients: pd.DataFrame,
    corrupt_encounters: pd.DataFrame,
    corrupt_observations: pd.DataFrame,
) -> pd.DataFrame:
    """
    fn para crear el dataset completo corrupto con los casos limite eliminando el patient
    id duplicado para que si se pueda crear el objeto
    """
    return merge_full(
        corrupt_patients.drop_duplicates(subset=["patient"]),
        corrupt_encounters,
        corrupt_observations,
    )
