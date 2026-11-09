# Evaluación: tres pedidos, con y sin skills

Cada pedido se corrió dos veces desde la raíz del repositorio, en una sesión nueva:

```bash
claude -p "<pedido>"                              # con skills
claude -p --disallowedTools Skill "<pedido>"      # sin skills
```

Para ver qué skills se activaron, agregar `--output-format stream-json --verbose` y buscar
las llamadas a la herramienta `Skill`, o revisar la salida de texto.

Referencias (sumaria 2024, ponderando con `factor07 × mieperho`): Cusco 18.5 %, urbana 24.8 %,
rural 39.3 %, Cajamarca 45.0 %, Ica 6.0 %.

## Resultados

| # | Pedido | Modo | Skills activadas | Cifra obtenida | Esperada | ¿Ponderó? | Figura / observaciones |
|---|---|---|---|---|---|---|---|
| 1 | ¿Cuál fue la pobreza en Cusco en 2024? | Con skills | | | 18.5 % | | |
| 1 | ¿Cuál fue la pobreza en Cusco en 2024? | Sin skills | — | | 18.5 % | | |
| 2 | Grafica la pobreza urbana y rural | Con skills | | | 24.8 % y 39.3 % | | |
| 2 | Grafica la pobreza urbana y rural | Sin skills | — | | 24.8 % y 39.3 % | | |
| 3 | Haz un mapa de la pobreza por departamento | Con skills | | | Cajamarca 45.0 %, Ica 6.0 % | | |
| 3 | Haz un mapa de la pobreza por departamento | Sin skills | — | | Cajamarca 45.0 %, Ica 6.0 % | | |

## Qué cambió

<!-- Dos o tres frases: ¿sin skills qué filtro, peso o llave eligió Claude?, ¿la cifra cuadró?,
¿el mapa unió por nombre y dejó departamentos vacíos?, ¿cuánto tiempo o pasos tomó cada modo? -->

## Ajustes a las descriptions

<!-- Si alguna skill no se activó, anotar la description original, la nueva y si con el cambio
ya se activa. -->
