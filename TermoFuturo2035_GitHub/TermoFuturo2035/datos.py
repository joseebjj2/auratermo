"""Obtención y preparación de datos reales de Open-Meteo.
No contiene observaciones meteorológicas sintéticas.
"""
from __future__ import annotations

from datetime import date, timedelta
import pandas as pd
import requests

FUENTE_NOMBRE = "Open-Meteo Historical Weather API"
FUENTE_URL = "https://open-meteo.com/en/docs/historical-weather-api"
API_URL = "https://archive-api.open-meteo.com/v1/archive"
VARIABLES = "temperature_2m_max,temperature_2m_min,precipitation_sum"

# Coordenadas centrales de referencia, no sensores de estaciones particulares.
CIUDADES = {
    "Antofagasta": (-23.6509, -70.3975),
    "Arica": (-18.4783, -70.3126),
    "Concepción": (-36.8270, -73.0503),
    "Chillán": (-36.6066, -72.1034),
    "Iquique": (-20.2133, -70.1503),
    "Rancagua": (-34.1708, -70.7444),
    "Santiago": (-33.4489, -70.6693),
    "Talca": (-35.4264, -71.6554),
    "Temuco": (-38.7359, -72.5904),
    "Valparaíso": (-33.0472, -71.6127),
}

COLUMNAS = ["ciudad", "fecha", "temp_max_c", "temp_min_c", "precip_mm", "latitud", "longitud"]


def fechas_del_anio(anio: int) -> tuple[str, str]:
    """Fechas para un año terminado o hasta una fecha segura de 10 días de retraso."""
    hoy = date.today()
    inicio = date(anio, 1, 1)
    fin = min(date(anio, 12, 31), hoy - timedelta(days=10))
    if inicio > fin:
        raise ValueError("No hay días históricos disponibles para ese año.")
    return inicio.isoformat(), fin.isoformat()


def consultar_ciudad(ciudad: str, anio: int, timeout: int = 30) -> pd.DataFrame:
    """GET a Open-Meteo; convierte el JSON de series diarias a DataFrame."""
    if ciudad not in CIUDADES:
        raise ValueError(f"Ciudad no configurada: {ciudad}")
    lat, lon = CIUDADES[ciudad]
    inicio, fin = fechas_del_anio(anio)
    parametros = {
        "latitude": lat,
        "longitude": lon,
        "start_date": inicio,
        "end_date": fin,
        "daily": VARIABLES,
        "timezone": "America/Santiago",
    }
    respuesta = requests.get(API_URL, params=parametros, timeout=timeout)
    respuesta.raise_for_status()
    contenido = respuesta.json()
    if contenido.get("error"):
        raise ValueError(f"Open-Meteo respondió con un error: {contenido.get('reason', 'sin detalle')}")
    diario = contenido.get("daily") or {}
    claves = ["time", "temperature_2m_max", "temperature_2m_min", "precipitation_sum"]
    if not all(k in diario and isinstance(diario[k], list) for k in claves):
        raise ValueError("La API devolvió un formato inesperado: faltan series diarias.")
    if len({len(diario[k]) for k in claves}) != 1:
        raise ValueError("Las series diarias recibidas tienen diferentes tamaños.")
    tabla = pd.DataFrame({
        "ciudad": ciudad,
        "fecha": diario["time"],
        "temp_max_c": diario["temperature_2m_max"],
        "temp_min_c": diario["temperature_2m_min"],
        "precip_mm": diario["precipitation_sum"],
        "latitud": lat,
        "longitud": lon,
    })
    return preparar_datos(tabla)


def preparar_datos(datos: pd.DataFrame) -> pd.DataFrame:
    """Valida columnas, tipos, duplicados, fechas y faltantes antes de calcular."""
    faltantes = set(COLUMNAS).difference(datos.columns)
    if faltantes:
        raise ValueError("Faltan columnas requeridas: " + ", ".join(sorted(faltantes)))
    limpio = datos[COLUMNAS].copy()
    limpio["ciudad"] = limpio["ciudad"].astype("string").str.strip()
    limpio["fecha"] = pd.to_datetime(limpio["fecha"], errors="coerce")
    for c in ["temp_max_c", "temp_min_c", "precip_mm", "latitud", "longitud"]:
        limpio[c] = pd.to_numeric(limpio[c], errors="coerce")
    limpio = limpio.dropna(subset=["ciudad", "fecha", "temp_max_c", "latitud", "longitud"])
    limpio = limpio[limpio["ciudad"].str.len() > 0]
    limpio = limpio[(limpio["temp_max_c"].between(-90, 65)) & (limpio["latitud"].between(-90, 90)) & (limpio["longitud"].between(-180, 180))]
    limpio = limpio.drop_duplicates(subset=["ciudad", "fecha"], keep="last")
    return limpio.sort_values(["ciudad", "fecha"]).reset_index(drop=True)


def combinar_ciudades(ciudades: list[str], anio: int) -> tuple[pd.DataFrame, list[str]]:
    """No inventa valores cuando falla un servicio: informa y conserva datos válidos."""
    tablas = []
    errores = []
    for ciudad in ciudades:
        try:
            datos = consultar_ciudad(ciudad, anio)
            if datos.empty:
                errores.append(f"{ciudad}: sin registros disponibles")
            else:
                tablas.append(datos)
        except (requests.RequestException, ValueError, KeyError) as exc:
            errores.append(f"{ciudad}: {exc}")
    if not tablas:
        return pd.DataFrame(columns=COLUMNAS), errores
    return preparar_datos(pd.concat(tablas, ignore_index=True)), errores


def exportar_csv(datos: pd.DataFrame) -> bytes:
    """CSV UTF-8 con BOM para que Excel conserve acentos en nombres de ciudades."""
    exportar = datos.copy()
    if "fecha" in exportar.columns:
        exportar["fecha"] = pd.to_datetime(exportar["fecha"]).dt.strftime("%Y-%m-%d")
    return exportar.to_csv(index=False).encode("utf-8-sig")
