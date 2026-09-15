import pandas as pd


def count_nans(df: pd.DataFrame) -> pd.DataFrame:
    """Funcion para contar el porcentaje de NaNs por un columna de un pd.DataFrame"""
    nan_percentage = (
        (df.isna().mean() * 100).rename_axis("Column").to_frame("NaN percentage")
    )
    return nan_percentage


def duplicate_entries(df: pd.DataFrame, col: str) -> bool:
    """
    Fn para contar si hay entradas duplicadas en cierta columna de un DataFrame
    parametros:
        df: pd.DataFrame a analizar
        col: string indicando la llave de la columna sobre la cual buscar duplicados
    devuelve:
        dup: bool True si encuentra duplicados, False si no
    """
    x = df[col]
    a = x.nunique()
    b = x.size
    print(f"{a} vs {b}")
    return (a) != (b)


def time_coherence(pat: pd.DataFrame, obs: pd.DataFrame) -> pd.DataFrame | bool:
    """
    fn para evaluar si hay observaciones antes de la fecha de nacimiento o despues de la
    fecha de muerte de un paciente
    parametros:
        pat: pd.DataFrame de pacientes procesado mediante process_patients
        obs: pd.DataFrame de observaciones procesado mediante process_observations
    devuelve:
        x: pd.DataFrame con las observacions incoherentes, su id, las fechas y el paciente
        bool: True, si no encuentra niguna observacion incoherente
    """
    x = pat[["patient", "birthdate", "deathdate"]].merge(
        obs[["patient", "obs_date", "obs_desc"]],
        on="patient",
        how="right",
        validate="1:m",
    )
    x["coherence"] = (x["obs_date"] >= x["birthdate"]) & (
        x["obs_date"] <= x["deathdate"].fillna(pd.Timestamp.max)
    )
    if x["coherence"].sum() == x.shape[0]:  # si suma de trues = # de observaciones:
        return True
    else:
        print("Incoherent observations:")
        return x[~x["coherence"]]


def filter_by_condition(df: pd.DataFrame, col: str, mask: str) -> pd.DataFrame:
    """
    fn para filtrar el DataFrame full dada cierta condicion de cierta columna
    la condicion debe ser exacta, e.g. gender == F
    """
    return df[df[col] == mask]


def filter_by_value(
    df: pd.DataFrame,
    col: str,
    lower: float | None = None,
    upper: float | None = None,
    inclusive: bool = True,
) -> pd.DataFrame:
    """
    fn para filtrar un df dados dados ciertos limites de columnas numericas
    si se pasa unicamente lower, se devuelve filtrado con valores por encima
    si se pasa unicamente upper, se devuelve filtrado con valores por debajo
    si se pasan ambos, se devuelve filtrado con valores en medio de ellos
    parametro inclusive controla si el limite debe ser incluido o no
    """
    if lower is not None and upper is None:
        mask = df[col] >= lower if inclusive else df[col] > lower
    elif lower is None and upper is not None:
        mask = df[col] <= upper if inclusive else df[col] < upper
    elif lower is not None and upper is not None:
        if inclusive:
            mask = (df[col] >= lower) & (df[col] <= upper)
        else:
            mask = (df[col] > lower) & (df[col] < upper)
    else:
        return df.copy()

    return df[mask]
