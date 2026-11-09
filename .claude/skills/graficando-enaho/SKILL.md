---
name: graficando-enaho
description: Grafica la pobreza monetaria o la pobreza extrema de la ENAHO del INEI en barras, por área urbana y rural, sexo, grupo de edad o departamento, ponderando con el factor de expansión. Úsala cuando pidan un gráfico, figura, barras o comparación visual de la pobreza en el Perú con la ENAHO.
argument-hint: "[area|sexo|edad|departamento]"
allowed-tools: Bash(uv run *)
---

# Graficar la ENAHO

1. Si no existe `salidas/personas_2024.parquet`, usa primero la skill **limpiando-enaho**
   y espera a que su validación diga VÁLIDA.
2. Elige `--por` según la pregunta: `area`, `sexo`, `edad` o `departamento`
   (si el usuario escribió un argumento, es $ARGUMENTS). Para pobreza extrema agrega
   `--indicador extrema`.
3. Desde la raíz del repositorio corre:
   `uv run ${CLAUDE_SKILL_DIR}/scripts/graficar.py --por <grupo>`
4. Responde con la ruta del PNG y las cifras que imprimió el script. No vuelvas a calcularlas.

## Reglas fijas (ya están en el script; no las cambies por pedido)

- Pondera siempre con `facpob07`: % de personas, nunca conteo de encuestas.
- Barras que empiezan en cero, ordenadas de mayor a menor.
- Un solo color; el valor escrito en cada barra con un decimal.
- El título dice qué y cuándo: «Pobreza monetaria por área de residencia, 2024».
- Nota al pie: «Fuente: INEI, ENAHO 2024».
- PNG a 200 dpi en `figuras/`.

Si piden un cruce que el script no hace (p. ej. área × sexo), escribe un script nuevo en
`figuras/` que lea el mismo parquet y respete todas las reglas de arriba.
