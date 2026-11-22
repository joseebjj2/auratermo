"""Cálculos reproducibles y escenario hipotético (NO pronóstico)."""
from __future__ import annotations
import pandas as pd


def filtrar(datos: pd.DataFrame, anio: int, ciudades: list[str], solo_verano: bool) -> pd.DataFrame:
    copia = datos.copy()
    copia["fecha"] = pd.to_datetime(copia["fecha"])
    copia = copia[(copia["fecha"].dt.year == anio) & copia["ciudad"].isin(ciudades)]
    if solo_verano:
        # Verano meteorológico del hemisferio sur, en los meses del año consultado.
        copia = copia[copia["fecha"].dt.month.isin([12, 1, 2])]
    return copia.sort_values(["ciudad", "fecha"]).reset_index(drop=True)


def simular(datos: pd.DataFrame, umbral_c: float, aumento_c: float) -> pd.DataFrame:
    """Desplaza solo la máxima de cada día: comparación de sensibilidad, no predicción."""
    copia = datos.copy()
    copia["max_escenario_c"] = copia["temp_max_c"] + aumento_c
    copia["dia_caluroso_observado"] = copia["temp_max_c"] >= umbral_c
    copia["dia_caluroso_escenario"] = copia["max_escenario_c"] >= umbral_c
    return copia


def resumen_por_ciudad(datos_simulados: pd.DataFrame) -> pd.DataFrame:
    if datos_simulados.empty:
        return pd.DataFrame(columns=["ciudad", "dias_analizados", "dias_observados", "dias_escenario", "dias_adicionales", "max_observada_c"])
    resumen = datos_simulados.groupby("ciudad", as_index=False).agg(
        dias_analizados=("fecha", "size"),
        dias_observados=("dia_caluroso_observado", "sum"),
        dias_escenario=("dia_caluroso_escenario", "sum"),
        max_observada_c=("temp_max_c", "max"),
    )
    resumen["dias_adicionales"] = resumen["dias_escenario"] - resumen["dias_observados"]
    return resumen.sort_values(["dias_adicionales", "dias_escenario"], ascending=False).reset_index(drop=True)
