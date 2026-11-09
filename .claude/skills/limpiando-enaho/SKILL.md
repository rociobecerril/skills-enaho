---
name: limpiando-enaho
description: Limpia los módulos 34 (sumaria) y 02 (miembros del hogar) de la ENAHO del INEI y arma una base de personas residentes con pobreza monetaria y factor de expansión, validada contra la cifra oficial. Úsala cuando pidan limpiar, unir, preparar o analizar la ENAHO, o calcular pobreza o pobreza extrema en el Perú por región, departamento, área, sexo o edad.
argument-hint: "[año]"
allowed-tools: Bash(uv run *)
---

# Limpiar la ENAHO

Año pedido: $ARGUMENTS (si viene vacío, usa 2024).

1. Revisa que existan `datos/966-Modulo34.zip` y `datos/966-Modulo02.zip` (966 = ENAHO 2024).
   Si faltan, pide al usuario que los baje de
   `https://proyectos.inei.gob.pe/iinei/srienaho/descarga/STATA/966-Modulo34.zip` y `.../966-Modulo02.zip`
   y los deje en `datos/`. No los descomprimas: el script lee el zip.
2. Desde la raíz del repositorio corre exactamente:
   `uv run ${CLAUDE_SKILL_DIR}/scripts/limpiar.py --anio 2024`
   No reescribas la limpieza a mano ni cambies filtros, llaves o pesos.
3. Lee `salidas/validacion.txt`. Si dice NO VÁLIDA, o la pobreza difiere del INEI en más de
   0.1 puntos, **detente** y muéstrale al usuario qué chequeo falló. No respondas con cifras.
4. Responde usando `salidas/personas_2024.parquet`. Toda cifra va ponderada con `facpob07`
   (porcentaje de personas, nunca conteo de encuestas). `pobre` = pobreza ≤ 2.
5. Antes de usar una variable que no está en la base, lee [reference.md](reference.md).

## Al responder

- Da la cifra con un decimal y di que es % de personas, ENAHO 2024, INEI.
- Si la pregunta es por un departamento, filtra por `departamento` (código de 2 dígitos),
  no por nombre. Lima (15) no incluye al Callao (07).
- Si piden un gráfico, usa la skill graficando-enaho; si piden un mapa, mapeando-enaho.
- Advierte si un grupo tiene pocas observaciones sin expandir (menos de 100): la cifra es imprecisa.
