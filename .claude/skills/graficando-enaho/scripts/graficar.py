"""Grafica la pobreza monetaria de la ENAHO por área, sexo, grupo de edad o departamento.

Lee salidas/personas_<anio>.parquet (creada por la skill limpiando-enaho),
pondera con facpob07 y guarda un PNG a 200 dpi en figuras/.

Uso (desde la raíz del repositorio):
    uv run .claude/skills/graficando-enaho/scripts/graficar.py --por area
    uv run .claude/skills/graficando-enaho/scripts/graficar.py --por sexo --indicador extrema
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

COLOR = "#B5512D"  # un solo color para todas las barras

GRUPOS = {
    "area": ("area", "área de residencia"),
    "sexo": ("sexo", "sexo"),
    "edad": ("grupo_edad", "grupo de edad"),
    "departamento": ("nombre_departamento", "departamento"),
}
INDICADORES = {
    "pobreza": ("pobre", "Pobreza monetaria"),
    "extrema": ("pobre_extremo", "Pobreza extrema"),
}


def pobreza_por(base: pd.DataFrame, columna: str, indicador: str) -> pd.Series:
    """Porcentaje de personas pobres por grupo, ponderado con facpob07."""
    w = base["facpob07"]
    num = (base[indicador] * w).groupby(base[columna]).sum()
    den = w.groupby(base[columna]).sum()
    return (num / den * 100).sort_values(ascending=False)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--por", choices=GRUPOS, required=True)
    parser.add_argument("--indicador", choices=INDICADORES, default="pobreza")
    parser.add_argument("--anio", type=int, default=2024)
    parser.add_argument("--salidas", type=Path, default=Path("salidas"))
    parser.add_argument("--figuras", type=Path, default=Path("figuras"))
    args = parser.parse_args()

    ruta = args.salidas / f"personas_{args.anio}.parquet"
    if not ruta.exists():
        sys.exit(f"No existe {ruta}. Usa primero la skill limpiando-enaho.")
    base = pd.read_parquet(ruta)

    columna, etiqueta = GRUPOS[args.por]
    var, nombre = INDICADORES[args.indicador]
    serie = pobreza_por(base, columna, var)

    # Barras horizontales para departamentos (25 nombres), verticales para el resto.
    horizontal = args.por == "departamento"
    alto = 7.5 if horizontal else 4.5
    fig, ax = plt.subplots(figsize=(8, alto))
    if horizontal:
        s = serie.sort_values()
        barras = ax.barh(s.index, s.values, color=COLOR)
        ax.set_xlim(0, s.max() * 1.15)
        ax.set_xlabel("% de personas")
    else:
        barras = ax.bar(serie.index, serie.values, color=COLOR, width=0.6)
        ax.set_ylim(0, serie.max() * 1.15)  # siempre desde cero
        ax.set_ylabel("% de personas")
    ax.bar_label(barras, fmt="%.1f %%", padding=3, fontsize=9)

    ax.set_title(f"{nombre} por {etiqueta}, {args.anio}", loc="left", fontsize=13, fontweight="bold")
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    fig.text(0.01, 0.01, f"Fuente: INEI, ENAHO {args.anio}. Ponderado con facpob07.", fontsize=8, color="#555555")
    fig.tight_layout(rect=(0, 0.03, 1, 1))

    args.figuras.mkdir(parents=True, exist_ok=True)
    salida = args.figuras / f"{args.indicador}_{args.por}_{args.anio}.png"
    fig.savefig(salida, dpi=200)
    print(f"Figura guardada en {salida}\n")
    print(serie.round(1).rename(f"{nombre} (%)").to_string())


if __name__ == "__main__":
    main()
