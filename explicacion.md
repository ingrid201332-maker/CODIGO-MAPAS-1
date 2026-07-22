# Explicación detallada del análisis multicriterio para restauración ecológica en Laguna de Sonso

Este documento explica **por qué** se hizo el análisis de esta manera, **cómo** se construyó el modelo en QGIS y **de dónde salió la información** utilizada para definir los criterios. También resalta una interpretación importante: **por qué el modelo puede no generar áreas de prioridad alta** con las capas actuales y los pesos definidos.

## 1. ¿Por qué se hizo un análisis multicriterio?

La pregunta del proyecto busca identificar áreas prioritarias para restauración ecológica en el Complejo de Humedales de la Laguna de Sonso. Para responderla no basta con mirar una sola variable, porque la restauración depende de varias condiciones al mismo tiempo:

- Condiciones del suelo.
- Uso actual o recomendado del territorio.
- Pendiente del terreno.
- Relación espacial con cuerpos de agua o corredores hídricos.
- Presencia de limitaciones ambientales o productivas.

Por eso se propuso un **análisis multicriterio en SIG**. Este tipo de análisis permite transformar varias capas geográficas en puntajes comparables y combinarlos en un índice final. En este caso, el índice final se llama `prioridad` y se guarda en una capa nueva de QGIS.

La lógica general es:

```text
mayor coincidencia de condiciones favorables para restauración
= mayor puntaje multicriterio
= mayor prioridad de restauración
```

## 2. ¿De dónde salió la información usada?

La información usada salió principalmente de **las capas geográficas incluidas en este repositorio**. No se inventaron campos externos: el análisis se construyó revisando los atributos disponibles en los shapefiles cargados.

Las capas base son:

| Capa del repositorio | Información que aporta | Campos revisados |
| --- | --- | --- |
| `USOS DEL SUELO.zip` | Información sobre unidades de uso/capacidad, limitantes y recomendaciones de manejo. | `CLASE`, `SUBCLASE`, `LIMITANTES`, `USOS_RECOM`, `CARACTERIS`, `PRACTICAS_`, `AREA_ha` |
| `SUELOS.zip` | Información de paisaje, relieve, forma del terreno, material parental y características del suelo. | `UCS`, `PAISAJE`, `TIPO_RELIE`, `FORMA_TERR`, `MATERIAL_P`, `CARACTERIS`, `AREA_ha` |
| `PENDIENTE LAGUNA.zip` | Información de pendiente promedio del área. | `PEND_PROME`, `NOMBRE_ENT`, `COD_MUNICI` |
| `RIO CAUCA.zip` | Geometría del río Cauca para calcular distancia. | Se usó principalmente la geometría; el campo `id` no aporta criterio ambiental suficiente. |

Además de los datos del repositorio, se usaron **conceptos generales de análisis espacial y restauración ecológica de humedales**, especialmente:

- Los humedales dependen de condiciones hídricas, suelos húmedos, zonas inundables y conectividad con fuentes de agua.
- Las pendientes bajas suelen favorecer procesos de acumulación de agua y restauración de ambientes palustres o inundables.
- La cercanía a ríos o corredores hídricos puede aumentar la conectividad ecológica e hidrológica.
- Los usos agropecuarios, limitaciones de drenaje, inundación o nivel freático pueden indicar zonas donde conviene revisar alternativas de restauración, manejo o reconversión.

Por eso el modelo no se basó solamente en un campo, sino en la combinación de variables espaciales y atributos descriptivos.

## 3. ¿Cómo se realizó el análisis?

El análisis se implementó en el archivo:

```text
scripts/restauracion_laguna_sonso_qgis.py
```

El script se diseñó para ejecutarse directamente en la **consola Python de QGIS** después de cargar las capas del repositorio.

### 3.1 Detección de capas cargadas

El código busca automáticamente capas cuyo nombre contenga palabras clave:

- `usos` para `USOS DEL SUELO`.
- `suelos` para `SUELOS`.
- `pendiente` para `PENDIENTE LAGUNA`.
- `rio` para `RIO CAUCA`.

Esto evita tener que escribir rutas manuales y permite trabajar con las capas ya cargadas en el proyecto QGIS.

### 3.2 Selección de la unidad base

La capa `USOS DEL SUELO` se usó como **unidad base del análisis**. Esto significa que cada polígono de esa capa se evalúa y recibe un valor de prioridad.

Se tomó esta decisión porque esta capa divide el territorio en unidades que ya contienen información útil para manejo del suelo, limitantes y usos recomendados. En restauración ecológica, estas unidades permiten identificar dónde hay presión, limitaciones o posibilidades de cambio de manejo.

### 3.3 Cruce espacial con suelos y pendiente

Para cada polígono de `USOS DEL SUELO`, el script hace cruces espaciales con:

- `SUELOS`.
- `PENDIENTE LAGUNA`.

Cuando un polígono se cruza con varias unidades, se selecciona la entidad con **mayor área de intersección**. Esto se hizo para asignar la condición dominante de suelo y pendiente a cada polígono base.

### 3.4 Cálculo de distancia al río Cauca

El script une la geometría del `RIO CAUCA` y calcula la distancia desde el centroide de cada polígono de `USOS DEL SUELO` hasta el río.

La distancia se almacena en el campo:

```text
dist_rio_m
```

Luego se transforma en un puntaje llamado:

```text
score_rio
```

Mientras más cerca está un polígono del río, mayor es su puntaje de conectividad hidrológica.

## 4. Criterios usados y justificación

El modelo usa cuatro criterios, cada uno convertido a un puntaje entre 0 y 1.

| Criterio | Campo de salida | Peso | Justificación |
| --- | --- | ---: | --- |
| Uso del suelo | `score_uso` | 30 % | Evalúa clases, subclases, limitantes y recomendaciones; ayuda a reconocer presión antrópica o restricciones productivas. |
| Suelos con potencial de humedal | `score_suelo` | 30 % | Evalúa si hay señales de inundación, drenaje pobre, cubetas, depósitos aluviales o cuerpos de agua. |
| Pendiente | `score_pend` | 20 % | Favorece áreas planas o de baja pendiente, más compatibles con restauración de humedales. |
| Proximidad al río Cauca | `score_rio` | 20 % | Favorece áreas cercanas al río por conectividad hidrológica y ecológica potencial. |

La fórmula aplicada fue:

```text
prioridad = score_uso   × 0.30
          + score_suelo × 0.30
          + score_pend  × 0.20
          + score_rio   × 0.20
```

## 5. ¿Por qué se usaron estos pesos?

Los pesos se definieron como una propuesta inicial equilibrada, dando mayor importancia a:

1. **Uso del suelo**, porque indica presión, manejo y restricciones del territorio.
2. **Suelos**, porque en humedales las condiciones edáficas e hidrológicas son fundamentales.

Por eso ambos criterios tienen 30 % cada uno.

La pendiente y la proximidad al río también son importantes, pero se asignaron con 20 % cada una porque funcionan como criterios complementarios:

- La pendiente indica facilidad física para restaurar o reconectar áreas inundables.
- La proximidad al río indica conectividad, pero por sí sola no garantiza que el área sea restaurable.

Estos pesos no son definitivos. Se pueden ajustar si una autoridad ambiental, docente, experto local o validación de campo considera que otro criterio debe tener más peso.

## 6. Clasificación final de prioridad

Después de calcular el índice `prioridad`, se clasifica así:

| Índice `prioridad` | Clase asignada |
| ---: | --- |
| `>= 0.70` | Alta |
| `>= 0.45` y `< 0.70` | Media |
| `< 0.45` | Baja |

Esta clasificación se diseñó para que la prioridad alta represente polígonos donde coinciden varias condiciones fuertes al mismo tiempo. Es decir, una zona no queda como prioridad alta solo por estar cerca del río o solo por tener un tipo de suelo; debe sumar bien en la mayoría de los criterios.

## 7. ¿Por qué puede no aparecer prioridad alta?

Es importante resaltar que **si al ejecutar el modelo no aparece prioridad alta, eso no significa que no existan áreas importantes para restaurar**. Significa que, con los pesos, umbrales y capas actuales, ningún polígono alcanzó el valor mínimo de `0.70` exigido para clasificarse como prioridad alta.

Las razones principales pueden ser las siguientes:

### 7.1 El umbral de prioridad alta es exigente

El valor mínimo para prioridad alta es `0.70`. Para alcanzarlo, un polígono necesita tener puntajes altos en varios criterios al mismo tiempo.

Por ejemplo, si un polígono tiene buen puntaje de suelo, pero pendiente desfavorable o está lejos del río, el promedio ponderado puede quedarse en prioridad media.

### 7.2 La pendiente promedio reduce el puntaje final

La capa `PENDIENTE LAGUNA` tiene el campo `PEND_PROME`. En el modelo, las pendientes altas reciben menor puntaje porque la restauración de humedales suele favorecer áreas más planas.

Si los valores de pendiente promedio son altos, el campo `score_pend` baja. Como la pendiente pesa 20 %, esto puede impedir que el índice final llegue a prioridad alta.

### 7.3 La prioridad alta requiere coincidencia espacial de criterios

Una zona puede tener suelos adecuados, pero si no coincide espacialmente con baja pendiente, cercanía al río y señales de presión o limitación en el uso del suelo, el resultado no llega a prioridad alta.

El modelo busca coincidencia de criterios, no valores altos aislados.

### 7.4 La capa del río aporta distancia, no calidad ecológica

`RIO CAUCA` se usó por su geometría para calcular distancia. Sin embargo, la capa no contiene información sobre calidad del agua, conectividad real, barreras hidráulicas, diques, canales, estado de rondas hídricas o vegetación ribereña.

Por eso, la cercanía al río suma al índice, pero no garantiza prioridad alta si los demás criterios no acompañan.

### 7.5 Faltan variables ecológicas directas

El modelo trabaja con las capas disponibles en el repositorio. No incluye todavía variables como:

- Cobertura vegetal actual.
- Fragmentación del hábitat.
- Presencia de especies nativas o invasoras.
- Áreas degradadas confirmadas en campo.
- Calidad del agua.
- Régimen de inundación actual.
- Conflictos de uso del suelo.

La ausencia de estas variables puede hacer que el modelo sea conservador y que muchas áreas queden en prioridad media en lugar de alta.

### 7.6 Los pesos distribuyen la importancia entre cuatro criterios

Ningún criterio por sí solo define la prioridad. Aunque un polígono tenga `score_suelo` alto, ese criterio pesa 30 %. Para llegar a `0.70`, necesita que los otros criterios también aporten valores importantes.

Por eso la prioridad alta es más difícil de alcanzar.

## 8. Cómo interpretar que no haya prioridad alta

Si el mapa resultante no muestra polígonos de prioridad alta, la interpretación recomendada es:

- Las áreas de prioridad **media** deben revisarse con atención, porque pueden ser las candidatas más viables bajo la información disponible.
- La ausencia de prioridad alta puede indicar que el umbral `0.70` es muy estricto para las capas actuales.
- Puede ser necesario ajustar pesos o umbrales después de validación de campo.
- Puede ser necesario incluir nuevas capas ambientales para captar mejor la degradación o el potencial ecológico real.
- El resultado debe entenderse como una **priorización preliminar**, no como una decisión final.

En otras palabras, no tener prioridad alta no invalida el análisis. Más bien indica que el modelo está siendo prudente y que no clasifica una zona como altamente prioritaria si no hay evidencia suficiente en varias capas al mismo tiempo.

## 9. Qué hacer si se necesita obtener prioridad alta

Si el objetivo académico o técnico requiere identificar zonas de intervención principal, se pueden realizar ajustes metodológicos justificados, por ejemplo:

### 9.1 Ajustar el umbral de clasificación

Se podría cambiar la clasificación de prioridad alta de `0.70` a `0.65`, siempre explicando que el ajuste responde a la distribución real de los datos.

### 9.2 Aumentar el peso del criterio de suelos

Si el interés principal es restauración de humedales, puede tener sentido aumentar el peso de `score_suelo`, porque los suelos hídricos o inundables son determinantes.

Ejemplo alternativo:

| Criterio | Peso alternativo |
| --- | ---: |
| Suelos | 40 % |
| Uso del suelo | 25 % |
| Proximidad al río | 20 % |
| Pendiente | 15 % |

### 9.3 Usar clasificación por cuantiles

Otra opción es clasificar como prioridad alta el 20 % de polígonos con mayor puntaje, aunque sus valores no superen `0.70`. Esto sirve cuando se necesita seleccionar las mejores áreas relativas dentro del conjunto analizado.

### 9.4 Incorporar nuevas capas

La mejor alternativa técnica es incorporar variables adicionales, como cobertura vegetal, rondas hídricas, zonas degradadas, conectividad ecológica, amenaza por uso agropecuario o información de campo.

## 10. Conclusión

El análisis se realizó combinando información de uso del suelo, suelos, pendiente y proximidad al río Cauca porque esos criterios representan componentes importantes para evaluar restauración ecológica en un complejo de humedales.

La información proviene de los shapefiles del repositorio y de conceptos generales de análisis multicriterio SIG aplicados a restauración de humedales. El resultado permite generar una capa de priorización en QGIS, útil para discusión técnica, revisión cartográfica y toma de decisiones preliminares.

La ausencia de prioridad alta, si ocurre al ejecutar el script, se explica porque el modelo exige que varios criterios coincidan con puntajes altos. Con las capas actuales, es posible que ningún polígono alcance el umbral `0.70`. Por eso las áreas de prioridad media deben revisarse como candidatas principales y el modelo debe ajustarse o complementarse con más información si se requiere una priorización definitiva.
