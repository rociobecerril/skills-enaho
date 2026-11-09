# Skills ENAHO: limpiar, graficar y mapear la pobreza en el Perú

Tres skills de Claude Code que convierten los módulos de la ENAHO 2024 del INEI en una base
de personas validada contra la pobreza oficial, y a partir de ella hacen gráficos y un mapa
por departamento. Cualquiera que clone el repositorio obtiene la misma base, las mismas
cifras y las mismas figuras.

Sesión 16 de *Data Science con Python* (d2cml-ai) — entrega en el issue #200.

## Las tres skills

| Skill | Entra | Sale |
|---|---|---|
| `limpiando-enaho` | `datos/966-Modulo34.zip`, `datos/966-Modulo02.zip` | `salidas/personas_2024.parquet`, `salidas/validacion.txt` |
| `graficando-enaho` | La base limpia y una pregunta (área, sexo, edad, departamento) | `figuras/*.png` |
| `mapeando-enaho` | La base limpia y el GeoJSON de los 25 departamentos | `mapas/pobreza_departamento.png` |

Se encadenan solas: si `graficando-enaho` o `mapeando-enaho` no encuentran la base limpia,
llaman primero a `limpiando-enaho`. Así un solo pedido («haz un mapa de la pobreza por
departamento») activa dos skills.

Cada skill sigue la misma idea: **lo que no se discute va en el script** (llaves como texto,
filtro de residentes, unión validada, ponderación, reglas de gráficos y mapas); **el criterio
va en el SKILL.md** (qué grupo graficar, cómo explicar el resultado, qué advertir).

## Cómo usarlo

```bash
git clone <este-repo> && cd skills-enaho
uv sync
```

Baja los dos zip del INEI (966 es el código de la ENAHO 2024) y déjalos en `datos/` sin
descomprimir:

- https://proyectos.inei.gob.pe/iinei/srienaho/descarga/STATA/966-Modulo34.zip
- https://proyectos.inei.gob.pe/iinei/srienaho/descarga/STATA/966-Modulo02.zip

El GeoJSON de departamentos ya viene en `datos/`. Luego abre Claude Code en la carpeta y pide,
por ejemplo:

```
¿Cuál fue la pobreza en Cusco en 2024?
Grafica la pobreza urbana y rural
Haz un mapa de la pobreza por departamento
```

O llámalas a mano: `/limpiando-enaho 2024`, `/graficando-enaho sexo`, `/mapeando-enaho`.

Los scripts también corren sin Claude:

```bash
uv run .claude/skills/limpiando-enaho/scripts/limpiar.py --anio 2024
uv run .claude/skills/graficando-enaho/scripts/graficar.py --por area
uv run .claude/skills/mapeando-enaho/scripts/mapear.py
```

## Decisiones de limpieza

1. **Leer** los `.dta` desde el zip con `convert_categoricals=False` (códigos, no etiquetas).
2. **Normalizar** nombres a minúsculas sin tildes (`aÑo` → `anio`) y llaves como texto con
   ceros a la izquierda (`conglome` «015009», `ubigeo` «010101»).
3. **Filtrar** residentes habituales: `(p204 == 1 & p205 == 2) | (p204 == 2 & p206 == 1)`.
4. **Unir** personas con hogares por `conglome, vivienda, hogar` con `validate="m:1"`.
5. **Construir** `departamento = ubigeo[:2]`, `urbano = estrato <= 5`, `pobre = pobreza <= 2`.
6. **Validar** llaves únicas, ninguna fila perdida ni duplicada, 25 departamentos y la pobreza
   oficial (27.6 % total, 5.5 % extrema, 108,664 residentes). Si algo falla, no se guarda la base.
7. **Guardar** `salidas/personas_2024.parquet` y `salidas/validacion.txt`.

Toda cifra va ponderada: en la base de personas con `facpob07`, en la sumaria con
`factor07 × mieperho`. La cifra oficial sale con la sumaria (27.58 %); con la base de personas
sale 27.53 %. Las cifras por grupo pueden diferir en una o dos décimas entre ambos métodos.

## Validación

Ver [`salidas/validacion.txt`](salidas/validacion.txt).

## Evaluación con y sin skills

Ver [`evaluacion.md`](evaluacion.md): los tres pedidos de prueba corridos con
`claude -p` con y sin la herramienta Skill.

## Estructura

```
.claude/skills/
  limpiando-enaho/   SKILL.md · reference.md · scripts/limpiar.py
  graficando-enaho/  SKILL.md · scripts/graficar.py
  mapeando-enaho/    SKILL.md · scripts/mapear.py
datos/      zip del INEI (no se suben) y GeoJSON
salidas/    validacion.txt (la base .parquet no se sube)
figuras/    gráficos PNG
mapas/      pobreza_departamento.png
evaluacion.md · README.md · pyproject.toml
```

Fuente de los datos: INEI, Encuesta Nacional de Hogares (ENAHO) 2024.
