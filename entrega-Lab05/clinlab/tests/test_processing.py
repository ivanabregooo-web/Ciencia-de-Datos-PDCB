import pandas as pd
import pytest
from clinlab.processing import merge_full


def test_merge_full_corrupt_dfs(
    corrupt_patients: pd.DataFrame,
    corrupt_encounters: pd.DataFrame,
    corrupt_observations: pd.DataFrame,
):
    """
    7.4: person_id duplicado
    fn para testear el join de dfs incluyendo un person_id duplicado
    en este caso falla y debe ser manejado con un MergeError para que pytest pase
    hallazgo lab2: este es el comportamiento esperado, ya que la validacion uno a muchos (1:m) impide que se realice el join que multiplicaria filas y anuncia el error.
    """
    with pytest.raises(pd.errors.MergeError):
        merge_full(corrupt_patients, corrupt_encounters, corrupt_observations)
