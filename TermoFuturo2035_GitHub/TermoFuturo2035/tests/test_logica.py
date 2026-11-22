from datetime import date
from unittest.mock import Mock, patch
import pandas as pd
import pytest
from analisis import filtrar, simular, resumen_por_ciudad
from datos import preparar_datos, consultar_ciudad, exportar_csv, COLUMNAS


def fixture():
    return pd.DataFrame([
        ["Santiago", "2025-01-01", 29, 13, 0, -33.4489, -70.6693],
        ["Santiago", "2025-01-02", 31, 15, 0, -33.4489, -70.6693],
        ["Concepción", "2025-01-01", 24, 11, 2, -36.827, -73.05],
        ["Santiago", "2025-01-02", 31, 15, 0, -33.4489, -70.6693],
    ], columns=COLUMNAS)


def test_preparacion_elimina_duplicados_y_convierte_fechas():
    datos = preparar_datos(fixture())
    assert len(datos) == 3
    assert pd.api.types.is_datetime64_any_dtype(datos["fecha"])


def test_filtros_ciudad_y_verano():
    df = preparar_datos(fixture())
    assert len(filtrar(df, 2025, ["Santiago"], False)) == 2
    assert len(filtrar(df, 2025, ["Santiago"], True)) == 2
    assert filtrar(df, 2024, ["Santiago"], False).empty


def test_simulacion_es_hipotetica_y_no_modifica_observado():
    df = preparar_datos(fixture())
    calculado = simular(df, umbral_c=30, aumento_c=2)
    santiago = resumen_por_ciudad(calculado).set_index("ciudad").loc["Santiago"]
    assert santiago["dias_observados"] == 1
    assert santiago["dias_escenario"] == 2
    assert santiago["dias_adicionales"] == 1
    assert (calculado["max_escenario_c"] == calculado["temp_max_c"] + 2).all()


def test_exportacion_csv_con_acentos():
    csv = exportar_csv(preparar_datos(fixture()))
    assert csv.startswith(b"\xef\xbb\xbf")
    assert "Concepción" in csv.decode("utf-8-sig")


def test_consulta_api_parsea_json_realista_sin_necesidad_de_red():
    respuesta = Mock()
    respuesta.json.return_value = {"daily": {"time": ["2025-01-01", "2025-01-02"],
            "temperature_2m_max": [28.5, 30.1], "temperature_2m_min": [15.3, 16.5],
            "precipitation_sum": [0.0, 0.2]}}
    respuesta.raise_for_status.return_value = None
    with patch("datos.requests.get", return_value=respuesta) as get:
        df = consultar_ciudad("Santiago", 2025)
    assert len(df) == 2
    assert get.call_args.kwargs["params"]["timezone"] == "America/Santiago"
    assert get.call_args.kwargs["params"]["daily"].startswith("temperature_2m_max")
