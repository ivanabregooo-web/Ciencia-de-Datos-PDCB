import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


default_physio_ranges = {
    "2708-6": (95.0, 100.0),  # Oxygen saturation
    "8480-6": (90.0, 120.0),  # Systolic Blood Pressure
    "8462-4": (60.0, 80.0),  # Diastolic Blood Pressure
    "9279-1": (12.0, 18.0),  # Respiratory rate
    "8867-4": (60.0, 100.0),  # Heart rate
    "8310-5": (36.1, 37.2),  # Body temperature
    "718-7": (12.0, 18.0),  # Hemoglobin
    "2857-1": (27.0, 32.0),  # MCH
    "777-3": (150.0, 400.0),  # Platelets
    "Oxygen saturation in Arterial blood": (95.0, 100.0),
    "Systolic Blood Pressure": (90.0, 120.0),
    "Diastolic Blood Pressure": (60.0, 80.0),
    "Respiratory rate": (12.0, 18.0),
    "Heart rate": (60.0, 100.0),
    "Body temperature": (36.1, 37.2),
    "Hemoglobin [Mass/volume] in Blood": (12.0, 18.0),
    "MCH [Entitic mass] by Automated count": (27.0, 32.0),
    "Platelets [#/volume] in Blood by Automated count": (150.0, 400.0),
}


def demographic_counts(
    df: pd.DataFrame,
    x_col: str = "ethnicity",
    hue_col: str | None = "gender",
    patient_id_col: str = "patient",
    palette: str = "hls",
    cont: bool = False,
) -> plt.Axes:
    """fn para grafica de barras de conteo demografico agrupado
    parametros:
        df: pd.DataFrame, dataset 'full' creado mediante fn 'merge_full'
    x_col: columna para el eje x
    hue_col: columna para el hue, opcional
    palette: colores para la grafuca
    devuelve: ax, el ax de matplotlib de la grafica
    cont: booleano para graficar o no conteos sobre las barras
    """
    cols_to_group = [x_col]
    if hue_col and hue_col != x_col:
        cols_to_group.append(hue_col)
    agg = (
        df[[patient_id_col] + cols_to_group]
        .drop_duplicates(subset=["patient"])
        .drop(columns=["patient"])
        .value_counts(cols_to_group)
        .reset_index(name="count")
    )

    _, ax = plt.subplots(figsize=(8, 5))
    plot_kwargs = {"data": agg, "x": x_col, "y": "count", "palette": palette, "ax": ax}

    if hue_col:
        plot_kwargs["hue"] = hue_col
    else:
        plot_kwargs["hue"] = x_col
        plot_kwargs["legend"] = False

    sns.barplot(**plot_kwargs)

    if cont:
        for container in ax.containers:
            ax.bar_label(container, fmt="%d", padding=1)

    title = f"Number of patients by {x_col.capitalize()}" + (
        f" and {hue_col.capitalize()}" if hue_col else ""
    )
    ax.set_title(title)
    ax.set_xlabel(x_col.capitalize())
    ax.set_ylabel("Patient Count")

    return ax, agg


def encounter_metrics(
    df: pd.DataFrame,
    hue_col: str | None = "gender",
    palette: str = "Set2",
    cont: bool = True,
) -> plt.Axes:
    """
    fn para plotear metricas (media y mediana) de encuentros por pacientes
    parametros:
        df: pd.DataFrame, full
        x_col : str, default metric, columna para el eje x
        hue_col: str o None, default gender, columna para agrupar
        metrics: lista de str o None, default None, metrica a calcular
        palette: str, colores de seaborn para la grafica
        cont: bool para imprimir o no conteos encima de la barra
    Devuelve:
        ax: plt.Axes de la figura
    """
    metrics = ["mean", "median"]

    cols = ["encounter", "patient"]
    group_cols = ["patient"]
    if hue_col:
        cols.append(hue_col)
        group_cols.append(hue_col)

    patient_counts = (
        df[cols]
        .drop_duplicates(subset=["encounter"])
        .value_counts(subset=group_cols)
        .reset_index(name="count")
    )
    patient_counts = patient_counts[patient_counts["count"] > 0]
    metric_map = {m: m.capitalize() for m in metrics}

    if hue_col is not None:
        agg = (
            patient_counts.groupby(hue_col, observed=True)["count"]
            .agg(metrics)  # type: ignore[arg-type]
            .rename(columns=metric_map)
            .reset_index()
            .melt(id_vars=hue_col, var_name="metric", value_name="value")
        )
    else:
        agg = (
            patient_counts["count"]
            .agg(metrics)  # type: ignore[arg-type]
            .to_frame()
            .T.rename(columns=metric_map)
            .melt(var_name="metric", value_name="value")
        )
    _, ax = plt.subplots(figsize=(8, 5))

    plot_kwargs = {
        "data": agg,
        "x": "metric",
        "y": "value",
        "palette": palette,
        "ax": ax,
        "width": 0.5,
    }
    if hue_col:
        plot_kwargs["hue"] = hue_col
    else:
        plot_kwargs["hue"] = "metric"
        plot_kwargs["legend"] = False
    sns.barplot(**plot_kwargs)

    if cont:
        for container in ax.containers:
            ax.bar_label(container, fmt="%.2f", padding=0.25)

    ax.set_title("Encounter Metrics per Patient")
    ax.set_ylabel("Encounters")

    return ax, agg


def plot_top_observation_codes(
    df: pd.DataFrame,
    top_n: int = 10,
    palette: str = "tab20",
    cont: bool = True,
) -> tuple[pd.DataFrame, plt.Figure]:
    """
    calcula y grafica los top_n codigos de observacion mas frecuentes
    parametros:
        df: pd.DataFrame, full
        top_n: int, default 10, n de codigos a graficar
        palette: str, default "tab20", colores de seaborn para la grafica
        cont: bool para imprimir o no conteos encima de la barra
    devuelve: tuple[pd.DataFrame, plt.Figure]
        el df de codigos mas frecuentes y la figura
    """
    df = df.copy()
    cols = ["obs_code", "obs_desc"]
    filtered = df.dropna(subset=["obs_code"])

    counts = (
        filtered.groupby(cols, observed=True)
        .size()
        .reset_index(name="count")
        .sort_values(["count"], ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )

    counts["obs_desc"] = counts["obs_desc"].astype(str)
    counts["obs_code"] = counts["obs_code"].astype(str)
    unique_descs = counts["obs_desc"].unique().tolist()
    palette_colors = sns.color_palette(palette, n_colors=max(len(unique_descs), 1))
    color_map = dict(zip(unique_descs, palette_colors))

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(
        data=counts,
        x="obs_code",
        y="count",
        hue="obs_desc",
        palette=color_map,
        ax=ax,
        legend=False,
    )

    ax.tick_params(axis="x", rotation=45)
    if cont:
        for container in ax.containers:
            ax.bar_label(container, padding=0.2)

    ax.set_title(f"Top {top_n} most-common observation codes")
    ax.set_ylabel("Count")
    ax.set_xlabel("Observation Code")
    handles = [plt.Rectangle((0, 0), 1, 1, color=color_map[d]) for d in unique_descs]
    fig.legend(
        handles=handles,
        labels=unique_descs,
        title="Description",
        bbox_to_anchor=(1.02, 0.5),
        loc="center left",
        frameon=True,
    )
    plt.tight_layout()

    return counts, fig


def plot_obs_distribution(
    df: pd.DataFrame,
    obs_col: str,
    obs_identifier: str,
    physio_range: tuple[float, float] | None = None,
    bins: int = 40,
    color: str = "#1B998B",
    kde: bool = False,
) -> plt.Axes:
    """
    fn para graficar la distribucion de una variable dado su codigo o descripcion
    parametros:
        df: pd.DataFrame, full
        obs_identifier: str, obs_code u obs_desc. Identificador de la observacion
        obs_col: str, estrictamente 'obs_code' u 'obs_desc'
        physio_range: tuple[float, float] o None, default None
            (min, max) rango fisiologico de la variable. El paquete incluye por default:
                '2708-6': (95.0, 100.0),  # Oxygen saturation in Arterial blood (%)
                '8480-6': (90.0, 120.0),  # Systolic Blood Pressure (mm[Hg])
                '8462-4': (60.0, 80.0),   # Diastolic Blood Pressure (mm[Hg])
                '9279-1': (12.0, 18.0),   # Respiratory rate (/min)
                '8867-4': (60.0, 100.0),  # Heart rate (/min)
                '8310-5': (36.1, 37.2),   # Body temperature (Cel)
                '718-7': (12.0, 18.0),    # Hemoglobin [Mass/volume] in Blood (g/dL))
                '2857-1': (27.0, 32.0),   # MCH [Entitic mass] by Automated count (pg)
                '777-3': (150.0, 400.0),  # Platelets [#/volume] in Blood by Automated count ((# * 10e3)/uL)
            El usuario debe proveer el rango fisiologico (a manera de tupla) de cualquier otra variable a graficar si desea marcar valores atípicos
        bins: # de bins para el histograma
        color: str, default '#1B998B', color para el histograma
        kde: bool, default False para decidir si se ajusta gaussiana sobre histograma
    devuelve:
        plt.Axes de la figura
    """
    data = df[df[obs_col] == obs_identifier].dropna(subset=["num_val"])
    if data.empty:
        raise ValueError(f"No records found for {obs_col}='{obs_identifier}'")

    target_range = physio_range
    if target_range is None:
        if obs_identifier in default_physio_ranges:
            target_range = default_physio_ranges[obs_identifier]

    patient_obs_counts = (
        data.groupby("patient", observed=True)
        .size()
        .loc[lambda s: s >= 3]  # al menos 3 observaciones
    )
    patients_gte_3 = len(patient_obs_counts)

    out_of_range_text = ""
    out_of_range_count = None

    if target_range:
        low, high = target_range
        out_of_range_count = ((data["num_val"] < low) | (data["num_val"] > high)).sum()
        total_obs = len(data)
        out_of_range_pct = (out_of_range_count / total_obs) * 100
        out_of_range_text = (
            f"\n\n\u2022 Out of range:\n"
            f"{out_of_range_count:,} obs ({out_of_range_pct:.1f}%)"
        )

    _, ax = plt.subplots(figsize=(8, 5))

    sns.histplot(
        data["num_val"],
        ax=ax,
        bins=bins,
        fill=False,
        color=color,
        kde=kde,
    )

    if target_range:
        low, high = target_range
        ax.axvline(low, color="crimson", linestyle="--", linewidth=1.5)
        ax.axvline(
            high, color="crimson", linestyle="--", linewidth=1.5, label="Normal range"
        )
        ax.legend(loc="upper left", frameon=True)

    annotation_text = (
        f"\u2022 Patients w/ \u22653 obs:\n  {patients_gte_3:,}" f"{out_of_range_text}"
    )
    ax.text(
        1.02,
        0.5,
        annotation_text,
        transform=ax.transAxes,
        fontsize=10,
        verticalalignment="center",
        bbox=dict(
            boxstyle="round,pad=0.5", facecolor="white", edgecolor="gray", alpha=0.8
        ),
    )

    ax.set_title(f"Distribution of {obs_identifier}")
    ax.set_xlabel("Value")
    ax.set_ylabel("Count")

    plt.tight_layout()
    return ax, patients_gte_3, out_of_range_count
