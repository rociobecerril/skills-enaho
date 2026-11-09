"""Mapa de la pobreza monetaria de la ENAHO por departamento.

Lee salidas/personas_<anio>.parquet (creada por la skill limpiando-enaho),
calcula la pobreza ponderada con facpob07 por departamento, la une al GeoJSON
por CÓDIGO (ubigeo[:2] = FIRST_IDDP, nunca por nombre) y guarda
mapas/pobreza_departamento.png.

Uso (desde la raíz del repositorio):
    uv run .claude/skills/mapeando-enaho/scripts/mapear.py
"""

from __future__ import annotations

import argparse
import sys
import urllib.request
from pathlib import Path

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

URL_GEOJSON = (
    "https://raw.githubusercontent.com/d2cml-ai/Data-Science-Python/main/"
    "sessions/06-geoespacial/lab/Data/peru_departamental_simple.geojson"
)
INDICADORES = {
    "pobreza": ("pobre", "Pobreza monetaria"),
    "extrema": ("pobre_extremo", "Pobreza extrema"),
}


def cargar_geojson(ruta: Path) -> gpd.GeoDataFrame:
    if not ruta.exists():
        ruta.parent.mkdir(parents=True, exist_ok=True)
        print(f"Descargando límites departamentales en {ruta} ...")
        urllib.request.urlretrieve(URL_GEOJSON, ruta)
    geo = gpd.read_file(ruta)
    # El código va como texto de dos dígitos: "07" (Callao) no es 7.
    geo["departamento"] = geo["FIRST_IDDP"].astype(str).str.zfill(2)
    return geo


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--indicador", choices=INDICADORES, default="pobreza")
    parser.add_argument("--anio", type=int, default=2024)
    parser.add_argument("--salidas", type=Path, default=Path("salidas"))
    parser.add_argument("--geojson", type=Path, default=Path("datos/peru_departamental_simple.geojson"))
    parser.add_argument("--mapas", type=Path, default=Path("mapas"))
    args = parser.parse_args()

    ruta = args.salidas / f"personas_{args.anio}.parquet"
    if not ruta.exists():
        sys.exit(f"No existe {ruta}. Usa primero la skill limpiando-enaho.")
    base = pd.read_parquet(ruta)
    var, nombre = INDICADORES[args.indicador]

    # Pobreza ponderada por departamento (código de 2 dígitos).
    w = base["facpob07"]
    tabla = pd.DataFrame({
        "valor": (base[var] * w).groupby(base["departamento"]).sum() / w.groupby(base["departamento"]).sum() * 100,
        "nombre": base.groupby("departamento")["nombre_departamento"].first(),
    }).reset_index()

    # Unión por código, validada uno a uno.
    geo = cargar_geojson(args.geojson)
    mapa = geo.merge(tabla, on="departamento", how="left", validate="1:1")
    assert len(mapa) == 25, f"Se esperaban 25 departamentos y hay {len(mapa)}"
    sin_dato = mapa.loc[mapa["valor"].isna(), "NOMBDEP"].tolist()
    assert not sin_dato, f"Departamentos sin dato (revisar la unión): {sin_dato}"
    assert {"07", "15"} <= set(mapa["departamento"]), "Lima (15) y Callao (07) deben ir separados"

    fig, ax = plt.subplots(figsize=(7, 9))
    mapa.plot(
        column="valor", cmap="Oranges", vmin=0, vmax=mapa["valor"].max(),
        edgecolor="white", linewidth=0.6, ax=ax, legend=True,
        legend_kwds={"label": f"{nombre} (% de personas)", "shrink": 0.5},
    )
    ax.set_axis_off()
    ax.set_title(f"{nombre} por departamento, {args.anio}", loc="left", fontsize=13, fontweight="bold")
    fig.text(0.02, 0.02, f"Fuente: INEI, ENAHO {args.anio}. Ponderado con facpob07.", fontsize=8, color="#555555")

    args.mapas.mkdir(parents=True, exist_ok=True)
    sufijo = "" if args.indicador == "pobreza" else f"_{args.indicador}"
    salida = args.mapas / f"pobreza_departamento{sufijo}.png"
    fig.savefig(salida, dpi=200, bbox_inches="tight")
    print(f"Mapa guardado en {salida} (25 departamentos con dato)\n")
    print(tabla.sort_values("valor", ascending=False).set_index("nombre")["valor"].round(1).to_string())


if __name__ == "__main__":
    main()
