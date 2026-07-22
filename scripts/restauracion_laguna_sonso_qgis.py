# -*- coding: utf-8 -*-
"""
Análisis multicriterio para priorizar restauración ecológica en Laguna de Sonso.
Uso: cargue en QGIS las capas RIO CAUCA, USOS DEL SUELO, SUELOS y PENDIENTE LAGUNA;
luego pegue y ejecute este archivo completo en la consola Python de QGIS.
"""
from qgis.PyQt.QtCore import QVariant
from qgis.core import (
    QgsField, QgsFeature, QgsGeometry, QgsProject, QgsSpatialIndex,
    QgsVectorLayer
)

# Pesos del modelo: pueden ajustarse según criterio experto.
PESOS = {
    "uso_suelo": 0.30,       # presión/aptitud de uso actual/recomendado
    "suelos_humedal": 0.30,  # suelos hídricos, inundables o mal drenados
    "pendiente": 0.20,       # pendientes bajas favorecen restauración de humedal
    "proximidad_rio": 0.20,  # conectividad hidrológica con el río Cauca
}
DIST_MAX_M = 5000.0          # distancia de referencia para normalizar proximidad al río


def buscar_capa(*tokens):
    """Devuelve la primera capa cargada cuyo nombre contiene todos los tokens."""
    tokens = [t.lower() for t in tokens]
    for lyr in QgsProject.instance().mapLayers().values():
        if not hasattr(lyr, "fields"):
            continue
        nombre = lyr.name().lower()
        if all(t in nombre for t in tokens):
            return lyr
    raise RuntimeError("No se encontró una capa cargada con tokens: {}".format(tokens))


def valor(feature, campo, default=""):
    return feature[campo] if campo in feature.fields().names() and feature[campo] is not None else default


def texto(feature, *campos):
    return " ".join(str(valor(feature, c, "")) for c in campos).lower()


def puntaje_uso(f):
    clase = str(valor(f, "CLASE", "")).strip()
    subclase = str(valor(f, "SUBCLASE", "")).lower()
    contenido = texto(f, "LIMITANTES", "USOS_RECOM", "CARACTERIS", "PRACTICAS_")
    score = 0.2
    if clase.isdigit():
        # Clases agrológicas mayores suelen tener más limitaciones y mejor oportunidad de restauración.
        score += min(max((int(clase) - 1) / 7.0, 0), 1) * 0.45
    if "h" in subclase or "inund" in contenido or "drenaje" in contenido or "nivel fre" in contenido:
        score += 0.25
    if "pastoreo" in contenido or "cultivo" in contenido:
        score += 0.10
    return min(score, 1.0)


def puntaje_suelo(f):
    contenido = texto(f, "PAISAJE", "TIPO_RELIE", "FORMA_TERR", "CARACTERIS", "MATERIAL_P")
    score = 0.15
    reglas = [
        ("cuerpo de agua", 0.95), ("plano de inund", 0.90), ("cubeta", 0.85),
        ("humedal", 0.90), ("muy pobremente dren", 0.90), ("pobremente dren", 0.85),
        ("nivel fre", 0.80), ("depósitos aluviales", 0.70), ("valle", 0.55),
        ("antr", 0.35),
    ]
    for patron, val in reglas:
        if patron in contenido:
            score = max(score, val)
    return min(score, 1.0)


def puntaje_pendiente(pend):
    try:
        p = float(pend)
    except Exception:
        return 0.5
    if p <= 3:
        return 1.0
    if p <= 7:
        return 0.85
    if p <= 12:
        return 0.65
    if p <= 25:
        return 0.40
    return 0.20


def puntaje_distancia(dist_m):
    if dist_m is None:
        return 0.0
    return max(0.0, min(1.0, 1.0 - (float(dist_m) / DIST_MAX_M)))


def mejor_interseccion(geom, capa, indice):
    mejor = None
    mejor_area = -1
    for fid in indice.intersects(geom.boundingBox()):
        f = capa.getFeature(fid)
        if not f.hasGeometry() or not geom.intersects(f.geometry()):
            continue
        area = geom.intersection(f.geometry()).area()
        if area > mejor_area:
            mejor_area = area
            mejor = f
    return mejor


def unir_geometrias(capa):
    geoms = [f.geometry() for f in capa.getFeatures() if f.hasGeometry()]
    if not geoms:
        return None
    g = QgsGeometry(geoms[0])
    for otra in geoms[1:]:
        g = g.combine(otra)
    return g


usos = buscar_capa("usos")
suelos = buscar_capa("suelos")
pendiente = buscar_capa("pendiente")
rio = buscar_capa("rio")

print("Capas detectadas y campos disponibles:")
for lyr in [usos, suelos, pendiente, rio]:
    print("- {}: {}".format(lyr.name(), ", ".join(lyr.fields().names())))

idx_suelos = QgsSpatialIndex(suelos.getFeatures())
idx_pend = QgsSpatialIndex(pendiente.getFeatures())
rio_geom = unir_geometrias(rio)
crs = usos.crs().authid()
salida = QgsVectorLayer("Polygon?crs={}".format(crs), "prioridad_restauracion_sonso", "memory")
prov = salida.dataProvider()
prov.addAttributes(usos.fields())
prov.addAttributes([
    QgsField("score_uso", QVariant.Double), QgsField("score_suelo", QVariant.Double),
    QgsField("score_pend", QVariant.Double), QgsField("score_rio", QVariant.Double),
    QgsField("dist_rio_m", QVariant.Double), QgsField("pend_prom", QVariant.Double),
    QgsField("ucs_suelo", QVariant.String), QgsField("prioridad", QVariant.Double),
    QgsField("clase_prio", QVariant.String),
])
salida.updateFields()

n = 0
for f in usos.getFeatures():
    if not f.hasGeometry():
        continue
    geom = f.geometry()
    fsuelo = mejor_interseccion(geom, suelos, idx_suelos)
    fpend = mejor_interseccion(geom, pendiente, idx_pend)
    s_uso = puntaje_uso(f)
    s_suelo = puntaje_suelo(fsuelo) if fsuelo else 0.5
    pend_prom = valor(fpend, "PEND_PROME", None) if fpend else None
    s_pend = puntaje_pendiente(pend_prom)
    dist = geom.centroid().distance(rio_geom) if rio_geom else None
    s_rio = puntaje_distancia(dist)
    total = (s_uso * PESOS["uso_suelo"] + s_suelo * PESOS["suelos_humedal"] +
             s_pend * PESOS["pendiente"] + s_rio * PESOS["proximidad_rio"])
    clase = "Alta" if total >= 0.70 else "Media" if total >= 0.45 else "Baja"
    out = QgsFeature(salida.fields())
    out.setGeometry(geom)
    ucs_suelo = valor(fsuelo, "UCS", "") if fsuelo else ""
    out.setAttributes(list(f.attributes()) + [s_uso, s_suelo, s_pend, s_rio, dist, pend_prom, ucs_suelo, total, clase])
    prov.addFeature(out)
    n += 1

salida.updateExtents()
QgsProject.instance().addMapLayer(salida)
print("Listo: se creó la capa 'prioridad_restauracion_sonso' con {} polígonos.".format(n))
print("Campos clave: prioridad (0-1), clase_prio, score_uso, score_suelo, score_pend, score_rio, dist_rio_m, pend_prom, ucs_suelo.")
