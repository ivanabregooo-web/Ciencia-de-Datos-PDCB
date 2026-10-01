import pandas as pd
import pytest

from clinlab.analysing import (
    count_nans,
    duplicate_entries,
    filter_by_condition,
    filter_by_value,
    time_coherence,
)


@pytest.fixture
def sample_patient_df() -> pd.DataFrame:
    """fixture para testear un caso normal"""
    return pd.DataFrame(
        {
            "patient": ["P001", "P002", "P003", "P004"],
            "gender": ["F", "M", "F", "M"],
            "ethnicity": ["hispanic", "nonhispanic", "hispanic", "hispanic"],
        }
    )


@pytest.fixture
def numeric_df() -> pd.DataFrame:
    """fixture de df numerico para testear filter_by_value"""
    return pd.DataFrame(
        {
            "patient": ["P1", "P2", "P3", "P4", "P5"],
            "num": [-10.5, 0.0, 5.0, 15.0, 20.5],
        }
    )


def test_filter_by_condition_ok(sample_patient_df: pd.DataFrame):
    """
    testear filtrado por condicion
    caso normal : filtrar por genero, obtener pacientes masculinos
    """
    result = filter_by_condition(sample_patient_df, col="gender", mask="F")

    assert len(result) == 2  # se recuperan 2
    assert list(result["patient"]) == ["P001", "P003"]  # se recuperan los correctos


def test_filter_by_condition_wrong_column(sample_patient_df: pd.DataFrame):
    """
    testear filtrado por condicion
    caso de error esperado: pedir genero sobre columna equivocada
    """
    with pytest.raises(KeyError):
        filter_by_condition(sample_patient_df, col="obs_desc", mask="F")


def test_filter_by_value_lower_only(numeric_df: pd.DataFrame):
    """testear solo con limite inferior"""
    result = filter_by_value(numeric_df, col="num", lower=5.0, upper=None)

    assert len(result) == 3
    assert list(result["num"]) == pytest.approx([5.0, 15.0, 20.5])


def test_filter_by_value_upper_only(numeric_df: pd.DataFrame):
    """testear solo con limite superior"""
    result = filter_by_value(numeric_df, col="num", lower=None, upper=5.0)

    assert len(result) == 3
    assert list(result["num"]) == pytest.approx([-10.5, 0.0, 5.0])


def test_filter_by_value_both_bounds(numeric_df: pd.DataFrame):
    """testear con ambos limites"""
    result = filter_by_value(numeric_df, col="num", lower=0.0, upper=15.0)

    assert len(result) == 3
    assert list(result["num"]) == pytest.approx([0.0, 5.0, 15.0])


def test_empty_df_count_nans(empty_df: pd.DataFrame):
    """
    7.1: DataFrame vacio
    fn para testear como la fn count_nans maneja un df vacio
    en este caso no truena, efectivamente devuelve un dataframe que correctamente
    se assertea que esta vacio y pytest pasa. Eso es correcto dado que el df vacio
    no contiene ningún nan, asi que este es un comportamiento esperado
    hallazgo lab2: a veces pandas puede devolver un df vacio sin marcar ningun error, a partir de algunos tipos de sub-seleccion del df. Es importante saber en que punto tronara el df vacio que en su declaracion no tuvo error.
    """
    assert count_nans(empty_df).empty


def test_filter_by_value_corrupt_df(clean_corrupt_full: pd.DataFrame):
    """
    7.2 columna entera de nan
    fn para testear como la funcion de filtrado maneja una columna entera de nan
    en este caso no truena ni devuelve error, sino que devuelve un df vacio
    es un comportamiento esperado a medias, ya que la fn filter_by_value no incluye manejo de nans
    hallazgo lab2: algunas funciones, no solo UDFs, sino tambien funciones nativas de python y pandas manejan a los nans silenciosamente, como en este ejemplo. Lo ideal es usar un dropna() antes de usar la funcion o incorporarlo dentro de ella si se trata de una UDF
    """
    filtered = filter_by_condition(
        clean_corrupt_full,  # primero extraer columna de nans
        col="obs_desc",
        mask="hemoglobin",
    )
    result = filter_by_value(filtered, col="num_val", lower=5.0, upper=None)
    assert (
        filtered["patient"]
        .reset_index(drop=True)
        .equals(pd.Series(["p001", "p002", "p003", "p004", "p005"]))
    )  # asegurar que haya tomado todos los pacientes
    assert count_nans(filtered).at["num_val", "NaN percentage"] == pytest.approx(
        100.0
    )  # asegurar que la col tenga puros nans
    assert result.empty  # el df resultante esta vacio


def test_time_coherence_corrupt_df_observation_before_birth(
    corrupt_patients: pd.DataFrame, corrupt_observations: pd.DataFrame
):
    """
    7.3 fecha de visita anterior al nacimiento
    fn para testear que time coherence capture correctamente la fecha imposible
    el df corrupto incluye una observacion hecha antes de la fecha de nacimiento
    hallazgo lab2: personalmente, el dataset que use en el lab2 no tenia observaciones anteriores a la fecha de nacimiento. Encontre observaciones posteriores a la fecha de muerte pero eran certificados de muerte asi que tiene sentido. De cualquier manera es bueno testear que la funcion tambien captura correctamente este tipo de incoherencia
    """
    result = time_coherence(
        corrupt_patients.drop_duplicates(subset=["patient"]), corrupt_observations
    )
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 1  # asegurar que se capturo la unica obs incoherente
    assert result["patient"].item() == "p003"  # se capturo la obs del paciente correcto
    assert result.keys().to_list() == [
        "patient",
        "birthdate",
        "deathdate",
        "obs_date",
        "obs_desc",
        "coherence",
    ]  # se capturaron los datos necesarios para identificar la obs incoherente
    assert (result["obs_date"] < result["birthdate"]).item()  # verificar incoherencia


def test_filter_by_sentinel_value_age_180(clean_corrupt_full: pd.DataFrame):
    """
    7.5 valor sentinela
    fn para testear si el valor sentinela de edad de 180 cumple su funcion
    en este caso todo funciona correctamente, se excluye la entry corrupta
    hallazgo lab2: esto tendria mayor utilidad si durante la creacion de un dataset, por alguna razon, algun dato no se capture y tampoco pueda ser marcado como NaN. En ese caso, seria util marcarlo con un valor que inmediatamente salte a la vista y sea identificado y tratado correctamente, ya sea reemplazandolo por NaN o eliminando la entry por completo.
    """
    result = filter_by_value(clean_corrupt_full, col="age", upper=180, inclusive=False)
    assert "p004" not in result["patient"].unique()  # se excluyo al paciente correcto
    assert (
        result.drop_duplicates(subset=["patient"])["age"] <= 110
    ).all()  # los entries restantes estan dentro de un rango biologico aceptable


def test_duplicate_entries(corrupt_patients: pd.DataFrame):
    """fn para testear que el patient id duplicado sea capturado correctamente"""
    result = duplicate_entries(corrupt_patients, col="patient")
    assert result is True  # devuelve true si capturo la entry duplicada
