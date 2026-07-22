# Análisis multicriterio SIG para priorizar restauración ecológica en la Laguna de Sonso

Este documento explica cómo se planteó el análisis multicriterio en QGIS para identificar áreas prioritarias de restauración ecológica en el Complejo de Humedales de la Laguna de Sonso, usando las capas disponibles en el repositorio.

## 1. Objetivo del análisis

El objetivo es generar una capa de salida que clasifique el territorio en prioridades de restauración **Alta**, **Media** o **Baja**. Para ello se combinan criterios ambientales y territoriales que ayudan a responder dónde conviene enfocar acciones de restauración ecológica, reconexión hídrica, recuperación de coberturas y manejo del suelo.

El análisis multicriterio mediante SIG contribuye porque permite:

- Integrar varias fuentes de información espacial en una sola evaluación.
- Comparar polígonos con criterios homogéneos y reproducibles.
- Identificar zonas donde coinciden condiciones favorables para restauración, como suelos de humedal, baja pendiente y cercanía a fuentes hídricas.
- Priorizar áreas donde los usos actuales o recomendados indican presión antrópica o limitaciones productivas.
- Generar una capa cartográfica que puede revisarse visualmente en QGIS y ajustarse con criterio experto.

## 2. Capas utilizadas

Las capas disponibles son shapefiles comprimidos en ZIP. El script está diseñado para trabajar con las capas cargadas en QGIS.

| Capa | Función dentro del análisis | Campos considerados |
| --- | --- | --- |
| `USOS DEL SUELO.zip` | Define los polígonos base que se evaluarán. Aporta información de capacidad/uso, limitantes y recomendaciones de manejo. | `CLASE`, `SUBCLASE`, `LIMITANTES`, `USOS_RECOM`, `CARACTERIS`, `PRACTICAS_`, `AREA_ha` |
| `SUELOS.zip` | Aporta información edáfica y geomorfológica para reconocer condiciones asociadas a humedales, inundación, drenaje deficiente o depósitos aluviales. | `UCS`, `PAISAJE`, `TIPO_RELIE`, `FORMA_TERR`, `MATERIAL_P`, `CARACTERIS`, `AREA_ha` |
| `PENDIENTE LAGUNA.zip` | Aporta la pendiente promedio por unidad administrativa/territorial. Se usa como criterio físico para estimar facilidad de restauración de humedales. | `PEND_PROME`, `NOMBRE_ENT`, `COD_MUNICI` |
| `RIO CAUCA.zip` | Aporta la geometría del río Cauca para calcular distancia y conectividad hidrológica potencial. | Geometría; el campo `id` no se usa como criterio ambiental. |

## 3. Conceptos considerados

### 3.1 Restauración ecológica

La restauración ecológica busca apoyar la recuperación de ecosistemas degradados, dañados o transformados. En un complejo de humedales, esto puede incluir recuperación de coberturas vegetales, rehabilitación de áreas inundables, manejo de suelos, control de presiones antrópicas y fortalecimiento de la conectividad hídrica y ecológica.

### 3.2 Humedales y conectividad hidrológica

En humedales, la relación con cuerpos de agua, ríos, planos de inundación y suelos con drenaje deficiente es fundamental. Por eso el análisis considera la cercanía al río Cauca y los atributos de suelos asociados a inundación, cubetas de desborde, depósitos aluviales, nivel freático y drenaje pobre.

### 3.3 Análisis multicriterio

El análisis multicriterio combina varias variables que no necesariamente tienen la misma unidad de medida. Para poder sumarlas, cada criterio se transforma en un puntaje normalizado entre **0 y 1**, donde:

- **0** representa baja prioridad o baja favorabilidad para restauración.
- **1** representa alta prioridad o alta favorabilidad para restauración.

Después, cada criterio recibe un peso según su importancia relativa. El resultado final es un índice de prioridad.

### 3.4 Ponderación de criterios

El modelo usa cuatro criterios principales:

| Criterio | Peso | Justificación |
| --- | ---: | --- |
| Uso del suelo | 30 % | Permite reconocer áreas con usos agropecuarios, limitaciones o prácticas que pueden indicar presión o necesidad de manejo/restauración. |
| Suelos con potencial de humedal | 30 % | Identifica áreas con características físicas y edáficas asociadas a ambientes húmedos, inundables o de drenaje deficiente. |
| Pendiente | 20 % | Las pendientes bajas suelen favorecer procesos de restauración de humedales y reconexión hídrica. |
| Proximidad al río Cauca | 20 % | La cercanía al río puede indicar mayor conectividad hidrológica y potencial de recuperación ecológica. |

La suma de los pesos es 100 %. Estos valores son una propuesta inicial y pueden ajustarse con criterio experto, validación en campo o participación institucional/comunitaria.

## 4. Desarrollo metodológico

### 4.1 Carga y reconocimiento de capas

Primero se cargan en QGIS las capas del repositorio. El script busca automáticamente capas cuyos nombres contengan palabras clave como `usos`, `suelos`, `pendiente` y `rio`.

Luego imprime en la consola los campos disponibles de cada capa. Esto permite verificar que QGIS está leyendo correctamente las tablas de atributos y confirmar cuáles campos se usarán en el análisis.

### 4.2 Definición de la unidad de análisis

La capa `USOS DEL SUELO` se toma como unidad base porque contiene polígonos que dividen el territorio en unidades manejables para evaluación y priorización. Cada polígono de esta capa recibe puntajes de los demás criterios.

### 4.3 Evaluación del uso del suelo

Para cada polígono de `USOS DEL SUELO`, el script calcula `score_uso` usando:

- `CLASE`: clases agrológicas mayores suelen representar más limitaciones para producción intensiva y pueden ser más apropiadas para restauración.
- `SUBCLASE`: la presencia de la letra `h` se interpreta como señal de limitantes hídricas.
- `LIMITANTES`, `USOS_RECOM`, `CARACTERIS` y `PRACTICAS_`: se buscan palabras relacionadas con drenaje, inundación, nivel freático, cultivo y pastoreo.

El criterio favorece áreas con señales de limitación hídrica, uso agropecuario o necesidad de manejo especial.

### 4.4 Evaluación de suelos con potencial de humedal

Para asignar el puntaje de suelo, el script cruza espacialmente cada polígono de `USOS DEL SUELO` con la capa `SUELOS` y selecciona la unidad de suelo con mayor área de intersección.

El campo de salida `ucs_suelo` almacena la unidad cartográfica `UCS` dominante. El puntaje `score_suelo` aumenta cuando los campos de suelos contienen conceptos como:

- `Cuerpo de agua`.
- `Plano de inundación`.
- `Cubeta`.
- `Humedal`.
- `Muy pobremente drenado` o `pobremente drenado`.
- `Nivel freático`.
- `Depósitos aluviales`.
- `Valle`.

Estos conceptos son importantes porque indican condiciones físicas compatibles con procesos de restauración de humedales.

### 4.5 Evaluación de pendiente

La pendiente se toma del campo `PEND_PROME` de la capa `PENDIENTE LAGUNA`. El script cruza espacialmente cada polígono de uso del suelo con la capa de pendiente y asigna el valor de la entidad con mayor intersección.

El criterio `score_pend` da mayor puntaje a pendientes bajas, porque estas zonas suelen facilitar:

- Acumulación o permanencia de agua.
- Procesos de revegetación en zonas planas.
- Reconexión con áreas inundables.
- Menor riesgo de erosión por escorrentía concentrada.

La clasificación propuesta en el script es:

| Pendiente promedio | Puntaje |
| --- | ---: |
| Menor o igual a 3 % | 1.00 |
| Mayor a 3 % y menor o igual a 7 % | 0.85 |
| Mayor a 7 % y menor o igual a 12 % | 0.65 |
| Mayor a 12 % y menor o igual a 25 % | 0.40 |
| Mayor a 25 % | 0.20 |

### 4.6 Evaluación de proximidad al río Cauca

El script une la geometría de la capa `RIO CAUCA` y calcula la distancia desde el centroide de cada polígono de `USOS DEL SUELO` hasta el río.

El campo `dist_rio_m` almacena esa distancia. Luego se calcula `score_rio`, donde las zonas más cercanas al río reciben mayor puntaje. La distancia de referencia usada para normalización es de 5.000 metros (`DIST_MAX_M`).

Este criterio representa conectividad hidrológica potencial, posibilidad de interacción con corredores ribereños y relevancia para procesos ecológicos asociados al sistema río-humedal.

## 5. Cálculo del índice final

El índice final se guarda en el campo `prioridad` y se calcula así:

```text
prioridad = score_uso   × 0.30
          + score_suelo × 0.30
          + score_pend  × 0.20
          + score_rio   × 0.20
```

El resultado queda entre 0 y 1.

## 6. Clasificación de prioridad

Después de calcular el índice final, el script asigna una categoría en el campo `clase_prio`:

| Valor de `prioridad` | Categoría |
| ---: | --- |
| Mayor o igual a 0.70 | Alta |
| Mayor o igual a 0.45 y menor a 0.70 | Media |
| Menor a 0.45 | Baja |

Las zonas con prioridad **Alta** son aquellas donde coinciden varios factores favorables o estratégicos para restauración: suelos con rasgos de humedal, baja pendiente, cercanía al río y/o usos del suelo con limitaciones o presión antrópica.

## 7. Interpretación de resultados

La capa `prioridad_restauracion_sonso` permite responder la pregunta de investigación de forma espacial. El análisis muestra qué sectores tienen mayor coincidencia de condiciones ecológicas, físicas e hidrológicas para orientar acciones de restauración.

La interpretación recomendada es:

- **Prioridad Alta**: áreas candidatas para intervención temprana, validación de campo, acuerdos de manejo, restauración activa o recuperación de conectividad hídrica.
- **Prioridad Media**: áreas que requieren revisión complementaria, posible restauración pasiva, monitoreo o manejo gradual.
- **Prioridad Baja**: áreas donde los criterios evaluados no indican una urgencia alta dentro del modelo; no significa ausencia de valor ambiental.

## 8. Limitaciones del análisis

Este modelo es una aproximación inicial. Para una priorización definitiva se recomienda complementar con:

- Cobertura vegetal actual o imágenes satelitales recientes.
- Información de biodiversidad, presencia de especies focales o corredores ecológicos.
- Tenencia de la tierra y restricciones sociales o legales.
- Amenazas como incendios, expansión agrícola, drenajes artificiales o contaminación.
- Validación de campo.
- Ajuste participativo de pesos con expertos, autoridades ambientales y comunidades locales.

## 9. Producto final esperado en QGIS

Al ejecutar el script se obtiene una capa de memoria llamada `prioridad_restauracion_sonso`, con los polígonos de uso del suelo y campos adicionales que permiten simbolizar el resultado por prioridad.

Los campos principales para visualizar el mapa son:

- `prioridad`: índice numérico de 0 a 1.
- `clase_prio`: clase final Alta, Media o Baja.
- `score_uso`: contribución del uso del suelo.
- `score_suelo`: contribución del suelo.
- `score_pend`: contribución de la pendiente.
- `score_rio`: contribución de proximidad al río.
- `dist_rio_m`: distancia al río Cauca.
- `pend_prom`: pendiente promedio asignada.
- `ucs_suelo`: unidad de suelos dominante.

## 10. Recomendación cartográfica

Para presentar el resultado en QGIS se recomienda simbolizar `clase_prio` con tres colores:

- **Alta**: rojo o naranja intenso.
- **Media**: amarillo.
- **Baja**: verde claro o gris.

También puede usarse una rampa continua sobre `prioridad`, donde valores cercanos a 1 representen mayor prioridad de restauración.
