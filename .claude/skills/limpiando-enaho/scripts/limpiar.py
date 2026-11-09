"""Limpia los módulos 34 (sumaria) y 02 (miembros) de la ENAHO del INEI.

Arma una base de personas (residentes habituales) con pobreza y factor de
expansión, la valida contra la cifra oficial del INEI y la guarda en
salidas/personas_<anio>.parquet junto con salidas/validacion.txt.

Uso (desde la raíz del repositorio):
    uv run .claude/skills/limpiando-enaho/scripts/limpiar.py --anio 2024

Las decisiones de limpieza están fijas aquí a propósito: no se discuten en
cada pedido.
"""

from __future__ import annotations

import argparse
import io
import sys
import unicodedata
import zipfile
from pathlib import Path

import pandas as pd

# Código de cada año en el portal de microdatos del INEI.
CODIGO_INEI = {2024: "966"}

# Cifras oficiales del INEI (% de personas) para validar.
OFICIAL = {2024: {"pobreza": 27.6, "extrema": 5.5, "residentes": 108_664}}
TOLERANCIA = 0.1  # puntos porcentuales

LLAVES_HOGAR = ["conglome", "vivienda", "hogar"]
LLAVES_PERSONA = LLAVES_HOGAR + ["codperso"]
ANCHO_LLAVE = {"conglome": 6, "vivienda": 3, "hogar": 2, "codperso": 2, "ubigeo": 6}

COLS_SUMARIA = LLAVES_HOGAR + ["ubigeo", "dominio", "estrato", "pobreza", "mieperho", "factor07"]
COLS_PERSONAS = LLAVES_PERSONA + ["p203", "p204", "p205", "p206", "p207", "p208a", "facpob07"]

DEPARTAMENTOS = {
    "01": "Amazonas", "02": "Áncash", "03": "Apurímac", "04": "Arequipa",
    "05": "Ayacucho", "06": "Cajamarca", "07": "Callao", "08": "Cusco",
    "09": "Huancavelica", "10": "Huánuco", "11": "Ica", "12": "Junín",
    "13": "La Libertad", "14": "Lambayeque", "15": "Lima", "16": "Loreto",
    "17": "Madre de Dios", "18": "Moquegua", "19": "Pasco", "20": "Piura",
    "21": "Puno", "22": "San Martín", "23": "Tacna", "24": "Tumbes",
    "25": "Ucayali",
}


# ---------------------------------------------------------------- 1. Leer
def leer_dta_de_zip(ruta_zip: Path, nombre_dta: str) -> pd.DataFrame:
    """Busca nombre_dta dentro del zip (en cualquier subcarpeta) y lo lee."""
    if not ruta_zip.exists():
        sys.exit(
            f"Falta {ruta_zip}. Descárgalo de "
            f"https://proyectos.inei.gob.pe/iinei/srienaho/descarga/STATA/{ruta_zip.name}"
        )
    with zipfile.ZipFile(ruta_zip) as z:
        candidatos = [n for n in z.namelist() if Path(n).name.lower() == nombre_dta.lower()]
        if not candidatos:
            sys.exit(f"No encontré {nombre_dta} dentro de {ruta_zip}")
        datos = io.BytesIO(z.read(candidatos[0]))
    # Códigos como números, sin convertir a etiquetas.
    return pd.read_stata(datos, convert_categoricals=False)


def llave_como_texto(serie: pd.Series, ancho: int) -> pd.Series:
    """Convierte una llave a texto con ceros a la izquierda ("15009" -> "015009")."""
    if pd.api.types.is_numeric_dtype(serie):
        serie = serie.astype("Int64").astype(str)
    return serie.astype(str).str.strip().str.zfill(ancho)


# ----------------------------------------------------------- 2. Normalizar
def normalizar_nombre(col: str) -> str:
    """Minúsculas y sin tildes; «aÑo» pasa a «anio»."""
    col = col.strip().lower().replace("ñ", "ni")
    col = unicodedata.normalize("NFKD", col).encode("ascii", "ignore").decode()
    return col


def normalizar(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns=normalizar_nombre)
    for col, ancho in ANCHO_LLAVE.items():
        if col in df.columns:
            df[col] = llave_como_texto(df[col], ancho)
    return df


def tasa(df: pd.DataFrame, indicador: pd.Series, peso: str | pd.Series) -> float:
    w = df[peso] if isinstance(peso, str) else peso
    return float((indicador * w).sum() / w.sum() * 100)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--anio", type=int, default=2024)
    parser.add_argument("--datos", type=Path, default=Path("datos"))
    parser.add_argument("--salidas", type=Path, default=Path("salidas"))
    args = parser.parse_args()

    anio = args.anio
    if anio not in CODIGO_INEI:
        sys.exit(f"No conozco el código INEI del año {anio}. Agrégalo a CODIGO_INEI.")
    codigo = CODIGO_INEI[anio]

    # 1-2. Leer y normalizar
    sumaria = normalizar(leer_dta_de_zip(args.datos / f"{codigo}-Modulo34.zip", f"sumaria-{anio}.dta"))
    miembros = normalizar(leer_dta_de_zip(args.datos / f"{codigo}-Modulo02.zip", f"enaho01-{anio}-200.dta"))
    sumaria = sumaria[COLS_SUMARIA]
    miembros = miembros[COLS_PERSONAS]
    n_miembros = len(miembros)

    assert not sumaria.duplicated(LLAVES_HOGAR).any(), "La sumaria tiene hogares repetidos"
    assert not miembros.duplicated(LLAVES_PERSONA).any(), "Miembros tiene personas repetidas"

    # 3. Filtrar residentes habituales
    residente = ((miembros["p204"] == 1) & (miembros["p205"] == 2)) | (
        (miembros["p204"] == 2) & (miembros["p206"] == 1)
    )
    personas = miembros[residente].copy()

    # 4. Unir personas con hogares (muchas personas, un hogar)
    base = personas.merge(sumaria, on=LLAVES_HOGAR, how="left", validate="m:1", indicator=True)
    sin_hogar = int((base["_merge"] != "both").sum())
    base = base.drop(columns="_merge")

    # 5. Construir variables
    base["departamento"] = base["ubigeo"].str[:2]
    base["nombre_departamento"] = base["departamento"].map(DEPARTAMENTOS)
    base["urbano"] = base["estrato"] <= 5
    base["area"] = base["urbano"].map({True: "Urbana", False: "Rural"})
    base["pobre"] = base["pobreza"] <= 2
    base["pobre_extremo"] = base["pobreza"] == 1
    base["sexo"] = base["p207"].map({1: "Hombre", 2: "Mujer"})
    base["edad"] = base["p208a"]
    base["grupo_edad"] = pd.cut(
        base["edad"], bins=[-1, 13, 29, 44, 64, 200],
        labels=["0-13", "14-29", "30-44", "45-64", "65 y más"],
    ).astype(str)
    base["anio"] = anio

    # 6. Validar
    pob_sumaria = tasa(sumaria, sumaria["pobreza"] <= 2, sumaria["factor07"] * sumaria["mieperho"])
    ext_sumaria = tasa(sumaria, sumaria["pobreza"] == 1, sumaria["factor07"] * sumaria["mieperho"])
    pob_personas = tasa(base, base["pobre"], "facpob07")
    ext_personas = tasa(base, base["pobre_extremo"], "facpob07")
    poblacion = base["facpob07"].sum()

    oficial = OFICIAL.get(anio, {})
    checks = {
        "llaves de persona únicas": not base.duplicated(LLAVES_PERSONA).any(),
        "la unión no perdió ni duplicó filas": len(base) == len(personas),
        "todas las personas tienen hogar": sin_hogar == 0,
        "25 departamentos": base["departamento"].nunique() == 25,
        "ningún departamento sin nombre": base["nombre_departamento"].notna().all(),
    }
    if oficial:
        checks[f"pobreza = {oficial['pobreza']} % (±{TOLERANCIA})"] = abs(pob_sumaria - oficial["pobreza"]) < TOLERANCIA
        checks[f"pobreza extrema = {oficial['extrema']} % (±{TOLERANCIA})"] = abs(ext_sumaria - oficial["extrema"]) < TOLERANCIA
        checks[f"residentes habituales = {oficial['residentes']:,}"] = len(base) == oficial["residentes"]

    lineas = [
        f"VALIDACIÓN ENAHO {anio} (código INEI {codigo})",
        "=" * 50,
        f"Hogares en la sumaria:                {len(sumaria):>12,}",
        f"Filas en el módulo 200:               {n_miembros:>12,}",
        f"Residentes habituales (base):         {len(base):>12,}",
        f"Población expandida (facpob07):       {poblacion:>12,.0f}",
        "",
        "Pobreza monetaria (% de personas)",
        f"  sumaria, factor07 × mieperho:       {pob_sumaria:>11.2f} %",
        f"  base de personas, facpob07:         {pob_personas:>11.2f} %",
        f"  cifra oficial INEI:                 {oficial.get('pobreza', float('nan')):>11.1f} %",
        "Pobreza extrema (% de personas)",
        f"  sumaria, factor07 × mieperho:       {ext_sumaria:>11.2f} %",
        f"  base de personas, facpob07:         {ext_personas:>11.2f} %",
        f"  cifra oficial INEI:                 {oficial.get('extrema', float('nan')):>11.1f} %",
        "",
        "Chequeos",
    ]
    lineas += [f"  [{'OK' if ok else 'FALLA'}] {nombre}" for nombre, ok in checks.items()]
    todo_ok = all(checks.values())
    lineas += ["", "RESULTADO: " + ("VÁLIDA" if todo_ok else "NO VÁLIDA — revisar antes de usar")]
    texto = "\n".join(lineas) + "\n"

    # 7. Guardar
    args.salidas.mkdir(parents=True, exist_ok=True)
    (args.salidas / "validacion.txt").write_text(texto, encoding="utf-8")
    if todo_ok:
        base.to_parquet(args.salidas / f"personas_{anio}.parquet", index=False)
    print(texto)
    if not todo_ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
