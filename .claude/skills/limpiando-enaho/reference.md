# Referencia: base de personas ENAHO

Archivo: `salidas/personas_<anio>.parquet` — una fila por residente habitual.

## Llaves (texto, con ceros a la izquierda)

| Variable | Ancho | Ejemplo | Nota |
|---|---|---|---|
| conglome | 6 | "015009" | Conglomerado |
| vivienda | 3 | "045" | |
| hogar | 2 | "11" | |
| codperso | 2 | "01" | Solo en personas |
| ubigeo | 6 | "010101" | Departamento, provincia, distrito |

Llave de hogar: `conglome + vivienda + hogar`. Llave de persona: las tres + `codperso`.
Nunca las conviertas a número: pierden el cero y las uniones fallan.

## Variables de la sumaria (módulo 34, una por hogar)

| Variable | Significado |
|---|---|
| pobreza | 1 pobre extremo, 2 pobre no extremo, 3 no pobre. Es un código, no se promedia |
| mieperho | Miembros del hogar |
| factor07 | Factor de expansión del hogar |
| estrato | 1–5 urbano, 6–8 rural |
| dominio | 1–3 Costa, 4–6 Sierra, 7 Selva, 8 Lima Metropolitana |

## Variables de miembros (módulo 02, una por persona)

| Variable | Significado |
|---|---|
| p203 | Parentesco con el jefe (1 jefe, 2 cónyuge, 3 hijo, …) |
| p204 | ¿Es miembro del hogar? 1 sí, 2 no |
| p205 | ¿Estuvo ausente 30 días o más? 1 sí, 2 no |
| p206 | ¿Estuvo presente los últimos 30 días? (no miembros) 1 sí, 2 no |
| p207 | Sexo: 1 hombre, 2 mujer |
| p208a | Edad en años cumplidos |
| facpob07 | Factor de expansión de la población |

Residente habitual: `(p204 == 1 & p205 == 2) | (p204 == 2 & p206 == 1)`.

## Variables construidas por limpiar.py

| Variable | Definición |
|---|---|
| departamento | `ubigeo[:2]`, texto "01"–"25" |
| nombre_departamento | Nombre con tildes (Áncash, Apurímac…) |
| urbano / area | `estrato <= 5` / "Urbana" o "Rural" |
| pobre | `pobreza <= 2` |
| pobre_extremo | `pobreza == 1` |
| sexo | "Hombre" / "Mujer" |
| edad, grupo_edad | p208a; 0-13, 14-29, 30-44, 45-64, 65 y más |
| anio | Año de la encuesta |

## Cálculo de una tasa

```python
w = base["facpob07"]
tasa = (base["pobre"] * w).sum() / w.sum() * 100
```

Por grupo: misma fórmula dentro de `groupby`. La cifra oficial del INEI se calcula en la
sumaria con `factor07 × mieperho`; en la base de personas con `facpob07` puede diferir
en unas centésimas (27.58 % vs 27.53 % en 2024).

## Otras variables

Si piden algo que no está (gasto, ingreso, educación, empleo), dile al usuario qué módulo
del INEI haría falta (p. ej. módulo 03 educación, 05 empleo) en lugar de inventar la variable.
La sumaria trae además `gashog2d` (gasto total anual), `inghog2d` (ingreso total anual),
`linea` y `linpe` (líneas de pobreza total y extrema, per cápita mensual).
