import matplotlib.pyplot as plt
import pandas as pd
import pytest
from clinlab.visualising import (
    demographic_counts,
    encounter_metrics,
    plot_obs_distribution,
    plot_top_observation_codes,
)


@pytest.fixture
def sample_obs_distribution_df() -> pd.DataFrame:
    """fixture para testear plot_obs_distribution"""
    return pd.DataFrame(
        {
            "patient": ["p1", "p1", "p1", "p2", "p2", "p2", "p2", "p3", "p3", "p4"],
            "obs_code": ["718-7"] * 10,
            "obs_desc": ["hemoglobin"] * 10,
            "num_val": [14.0, 15.0, 19.0, 12.5, 13.0, 14.5, 17.0, 11.0, 15.0, None],
        }
    )


@pytest.fixture
def sample_demographic_encounter_df() -> pd.DataFrame:
    """
    fixture para testear funciones de graficacion
    """
    return pd.DataFrame(
        {
            "patient": ["p1", "p1", "p2", "p2", "p3", "p3", "p3", "p4"],
            "encounter": ["e1", "e1", "e2", "e3", "e4", "e5", "e6", "e7"],
            "gender": ["M", "M", "F", "F", "F", "F", "F", "M"],
            "ethnicity": [
                "Hisp",
                "Hisp",
                "Non-hisp",
                "Non-hisp",
                "Hisp",
                "Hisp",
                "Hisp",
                "Non-hisp",
            ],
            "obs_code": ["c1", "c2", "c1", "c1", "c1", "c2", "c3", "c3"],
            "obs_desc": ["Oxy", "Temp", "Oxy", "Oxy", "Oxy", "Temp", "HR", "HR"],
        }
    )


def test_plot_obs_distribution_metrics(sample_obs_distribution_df: pd.DataFrame):
    """
    fn para testear la fn de graficar histograma de distribucion de una variable
    """
    ax, pts_gte_3, out_of_range = plot_obs_distribution(
        df=sample_obs_distribution_df,
        obs_col="obs_desc",
        obs_identifier="hemoglobin",
        physio_range=(12.0, 18.0),
    )

    assert pts_gte_3 == 2  # 2 pacientes con al menos 3 obs
    assert out_of_range == 2  # 2 observaciones fuera del rango
    plt.close(ax.figure)
    # plt.show()


def test_plot_obs_distribution_empty_raises_error(
    sample_obs_distribution_df: pd.DataFrame,
):
    """
    confirmar que intentar graficar un df vacio resulte en error
    """
    with pytest.raises(ValueError, match="No records found"):
        plot_obs_distribution(
            df=sample_obs_distribution_df,
            obs_col="obs_desc",
            obs_identifier="heart_rate",
        )


def test_demographic_counts_with_hue(sample_demographic_encounter_df: pd.DataFrame):
    """
    testear que demographic_counts maneje correctamente el parametro de agrupammiento
    """
    ax, agg = demographic_counts(
        df=sample_demographic_encounter_df, x_col="ethnicity", hue_col="gender"
    )
    hisp_males = agg[(agg["ethnicity"] == "Hisp") & (agg["gender"] == "M")][
        "count"
    ].iloc[0]
    non_hisp_females = agg[(agg["ethnicity"] == "Non-hisp") & (agg["gender"] == "F")][
        "count"
    ].iloc[0]

    assert hisp_males == 1  # verificar que separe correctamente
    assert non_hisp_females == 1
    plt.close(ax.figure)


def test_demographic_counts_no_hue(sample_demographic_encounter_df: pd.DataFrame):
    """
    testear que demographic counts tambien funcione correctamente sin hue
    """
    ax, agg = demographic_counts(
        df=sample_demographic_encounter_df, x_col="gender", hue_col=None
    )

    males = agg[agg["gender"] == "M"]["count"].iloc[0]
    assert males == 2  # verificar que cuente correctamente
    plt.close(ax.figure)


def test_encounter_metrics_with_hue(sample_demographic_encounter_df: pd.DataFrame):
    """
    testear que encounter metrics maneje correctamente el parametro de agrupamiento
    """
    ax, agg = encounter_metrics(df=sample_demographic_encounter_df, hue_col="gender")
    f_metrics = agg[agg["gender"] == "F"]
    f_mean = f_metrics[f_metrics["metric"] == "Mean"]["value"].iloc[0]
    f_median = f_metrics[f_metrics["metric"] == "Median"]["value"].iloc[0]
    m_metrics = agg[agg["gender"] == "M"]
    m_mean = m_metrics[m_metrics["metric"] == "Mean"]["value"].iloc[0]

    assert f_mean == 2.5
    assert f_median == 2.5
    assert m_mean == 1.0
    plt.close(ax.figure)


def test_plot_top_observation_codes(sample_obs_distribution_df: pd.DataFrame):
    """
    testear que la funcion no truene si se pasa un subset con un solo codigo de observacion
    """
    counts, fig = plot_top_observation_codes(
        df=sample_obs_distribution_df,
        top_n=2,  # se que solo hay uno
    )

    assert counts.iloc[0]["obs_code"] == "718-7"
    assert counts.iloc[0]["count"] == 10  # 10 observaciones
    assert len(counts) == 1  # solo deberia devolver un codigo de observacion
    plt.close(fig)
    # plt.show()
