---
name: mapeando-enaho
description: Hace un mapa coroplético de la pobreza monetaria o la pobreza extrema por departamento del Perú con la ENAHO del INEI, uniendo por código de ubigeo al GeoJSON de los 25 departamentos. Úsala cuando pidan un mapa, mapear o ver geográficamente la pobreza por departamento o región.
allowed-tools: Bash(uv run *)
---

# Mapear la ENAHO

1. Revisa si existe `salidas/personas_2024.parquet`. Si NO existe, invoca la skill
   `limpiando-enaho` con la herramienta Skill (argumento: 2024) y espera a que su
   validación diga VÁLIDA. No corras limpiar.py tú misma: la limpieza es tarea de esa skill.
2. Desde la raíz del repositorio corre:
   `uv run ${CLAUDE_SKILL_DIR}/scripts/mapear.py`
   (para pobreza extrema agrega `--indicador extrema`). Si falta
   `datos/peru_departamental_simple.geojson`, el script lo descarga.
3. Si el script falla en una aserción, **detente** y explica cuál: no dibujes un mapa con
   departamentos vacíos.
4. Responde con la ruta `mapas/pobreza_departamento.png` y menciona los tres departamentos
   con más y con menos pobreza según la tabla que imprimió el script.

## Reglas fijas (ya están en el script; no las cambies por pedido)

- Une por código: `ubigeo[:2]` con `FIRST_IDDP`, ambos como texto de dos dígitos.
- Nunca por nombre: «APURIMAC» no es «Apurímac».
- Exige 25 departamentos y ninguno sin dato.
- Un color de claro a oscuro (Oranges), desde 0; nunca arcoíris.
- Leyenda con la unidad: % de personas.
- Lima (15) y Callao (07) van separados.
- Pondera con `facpob07`. Nota al pie: «Fuente: INEI, ENAHO 2024».
