# CODIGO-MAPAS-1

Repositorio con capas base y un script para QGIS orientado a responder:

> ¿Cómo puede el análisis multicriterio mediante Sistemas de Información Geográfica (SIG) en QGIS contribuir a la identificación de áreas prioritarias para la restauración ecológica en el Complejo de Humedales de la Laguna de Sonso?

## Capas analizadas

Las capas incluidas en el repositorio son archivos ZIP con shapefiles. Los campos útiles para el análisis multicriterio son:

| Capa | Rol en el modelo | Campos utilizados |
| --- | --- | --- |
| `USOS DEL SUELO.zip` | Unidad candidata de análisis y presión/aptitud por uso del suelo. | `CLASE`, `SUBCLASE`, `LIMITANTES`, `USOS_RECOM`, `CARACTERIS`, `PRACTICAS_`, `AREA_ha` |
| `SUELOS.zip` | Potencial ecológico/hídrico del suelo. | `UCS`, `PAISAJE`, `TIPO_RELIE`, `FORMA_TERR`, `MATERIAL_P`, `CARACTERIS`, `AREA_ha` |
| `PENDIENTE LAGUNA.zip` | Restricción física; pendientes menores favorecen restauración de humedal. | `PEND_PROME`, `NOMBRE_ENT`, `COD_MUNICI` |
| `RIO CAUCA.zip` | Conectividad hidrológica; se usa la distancia geométrica al río. | Geometría de la capa; el campo `id` no aporta criterio ambiental. |

## Explicación metodológica

La explicación completa de cómo se realizó el análisis, qué conceptos se tuvieron en cuenta y cómo se interpretan los criterios está en [`ANALISIS_MULTICRITERIO_LAGUNA_SONSO.md`](ANALISIS_MULTICRITERIO_LAGUNA_SONSO.md).

## Código para la consola Python de QGIS

El script listo para pegar en la consola Python de QGIS está en:

- [`scripts/restauracion_laguna_sonso_qgis.py`](scripts/restauracion_laguna_sonso_qgis.py)

### Uso

1. Abra QGIS.
2. Cargue los cuatro ZIP/shapefiles del repositorio: `RIO CAUCA`, `USOS DEL SUELO`, `SUELOS` y `PENDIENTE LAGUNA`.
3. Abra **Complementos > Consola de Python**.
4. Pegue y ejecute todo el contenido de `scripts/restauracion_laguna_sonso_qgis.py`.
5. Revise la nueva capa de memoria `prioridad_restauracion_sonso`.

## Resultado esperado

El script crea una capa poligonal con los polígonos de `USOS DEL SUELO` y añade estos campos:

- `prioridad`: índice final normalizado entre 0 y 1.
- `clase_prio`: clasificación `Alta`, `Media` o `Baja`.
- `score_uso`: puntaje por clase/subclase/limitantes/usos recomendados.
- `score_suelo`: puntaje por condición hídrica del suelo.
- `score_pend`: puntaje por pendiente promedio.
- `score_rio`: puntaje por proximidad al río Cauca.
- `dist_rio_m`: distancia desde el centroide del polígono al río Cauca.
- `pend_prom`: pendiente promedio tomada de `PENDIENTE LAGUNA`.
- `ucs_suelo`: unidad cartográfica de suelos dominante por intersección espacial.

## Criterios y pesos predeterminados

- Uso del suelo: 30 %.
- Suelos con rasgos de humedal/inundación/mal drenaje: 30 %.
- Pendiente: 20 %.
- Proximidad al río Cauca: 20 %.

Estos pesos son editables dentro del diccionario `PESOS` del script.
