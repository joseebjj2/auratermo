"""TERMOFUTURO 2035 | Tercera Solemne de Taller de Programación II.
Aplicación educativa de análisis climático a partir de datos reales.
Ejecutar: streamlit run app.py
"""
from __future__ import annotations
from datetime import date
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from analisis import filtrar, resumen_por_ciudad, simular
from datos import CIUDADES, FUENTE_NOMBRE, FUENTE_URL, combinar_ciudades, exportar_csv, preparar_datos

st.set_page_config(page_title="TermoFuturo 2035 | Chile", page_icon="🌡️", layout="wide")

# Se reutiliza la respuesta para evitar consultas excesivas y mejorar la fluidez.
@st.cache_data(ttl=24 * 3600, show_spinner=False)
def obtener_datos(ciudades: tuple[str, ...], anio: int):
    return combinar_ciudades(list(ciudades), anio)


def encabezado():
    st.title("🌡️ TermoFuturo 2035")
    st.markdown("**Radar ciudadano de calor en Chile** · Datos históricos reales + escenarios hipotéticos")
    st.info("Herramienta educativa para comparar ciudades y explorar cambios de temperatura. "
            "**No genera pronósticos para 2035 ni reemplaza alertas meteorológicas o sanitarias oficiales.**")


def controles():
    st.sidebar.header("⚙️ Centro de control")
    actual = date.today().year
    anios = [y for y in range(min(actual, 2026), 2021, -1)]
    predeterminado = anios.index(2025) if 2025 in anios else 0
    anio = st.sidebar.selectbox("Año del registro histórico", anios, index=predeterminado)
    ciudades = st.sidebar.multiselect(
        "Ciudades para comparar",
        options=sorted(CIUDADES),
        default=["Concepción", "Santiago", "Talca"],
        help="Filtro efectivo: al cambiar ciudades cambian la tabla y todos los gráficos.",
    )
    umbral = st.sidebar.slider("Umbral de día caluroso (°C)", min_value=20, max_value=40, value=30)
    aumento = st.sidebar.slider("Aumento hipotético de temperatura (°C)", min_value=0.0, max_value=4.0, value=1.5, step=0.5)
    solo_verano = st.sidebar.checkbox("Solo verano (dic, ene, feb)", value=False)
    variable = st.sidebar.radio("Temperatura a mostrar en la evolución", ["Máxima", "Mínima"], horizontal=True)
    minimo = st.sidebar.number_input("Días de calor para destacar una ciudad", min_value=1, max_value=366, value=10, step=1)
    recomendaciones = st.sidebar.toggle("Mostrar ideas de prevención", value=True)
    st.sidebar.divider()
    respaldo = st.sidebar.file_uploader("Cargar CSV de respaldo (opcional)", type=["csv"],
        help="Si la API falla, aquí puedes subir el CSV previamente descargado desde la aplicación.")
    if st.sidebar.button("🔄 Limpiar caché y actualizar"):
        obtener_datos.clear()
        st.rerun()
    st.sidebar.link_button("📚 Documentación de la fuente", FUENTE_URL)
    return anio, ciudades, umbral, aumento, solo_verano, variable, minimo, recomendaciones, respaldo


def cargar(archivo, ciudades, anio):
    if archivo is not None:
        try:
            tabla = preparar_datos(pd.read_csv(archivo))
            return tabla, [], "CSV subido por el usuario (comprobar origen en el archivo)"
        except (ValueError, pd.errors.ParserError, UnicodeError) as exc:
            st.error(f"El archivo CSV no tiene el formato esperado: {exc}")
            st.stop()
    with st.spinner("Consultando datos históricos en Open-Meteo…"):
        tabla, errores = obtener_datos(tuple(sorted(ciudades)), anio)
    return tabla, errores, FUENTE_NOMBRE


def indicadores(datos, resumen):
    if datos.empty:
        return
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Días-ciudad analizados", f"{len(datos):,}".replace(",", "."), help="Un registro corresponde a un día de una ciudad.")
    c2.metric("Días calurosos observados", int(resumen["dias_observados"].sum()))
    c3.metric("Días en el escenario", int(resumen["dias_escenario"].sum()),
              delta=f'+{int(resumen["dias_adicionales"].sum())} vs. observado')
    c4.metric("Máxima observada", f'{datos["temp_max_c"].max():.1f} °C')
    st.caption("Los conteos suman días por ciudad: un mismo día calendario en tres ciudades cuenta tres registros.")


def tab_evolucion(datos, ciudad_foco, variable, aumento):
    st.subheader("Evolución de temperaturas")
    foco = datos[datos["ciudad"] == ciudad_foco].sort_values("fecha")
    if variable == "Máxima":
        serie = foco.set_index("fecha")[["temp_max_c", "max_escenario_c"]].rename(columns={
            "temp_max_c": "Máxima observada (°C)", "max_escenario_c": "Máxima hipotética (°C)"})
    else:
        serie = foco.set_index("fecha")[["temp_min_c"]].rename(columns={"temp_min_c": "Mínima observada (°C)"})
    st.line_chart(serie, x_label="Fecha", y_label="Temperatura (°C)")
    st.caption(f"Ciudad: {ciudad_foco}. Para máximas, la curva hipotética suma +{aumento:g} °C cada día; no es un pronóstico.")
    st.subheader("Temperaturas máximas y precipitación")
    puntos = datos.dropna(subset=["temp_max_c", "precip_mm"])
    if not puntos.empty:
        st.scatter_chart(puntos, x="temp_max_c", y="precip_mm", color="ciudad", x_label="Máxima diaria (°C)", y_label="Precipitación diaria (mm)")
    else:
        st.warning("No existen suficientes registros completos para el gráfico de dispersión.")


def tab_comparacion(resumen, datos, minimo, umbral):
    st.subheader("Ciudades frente a días calurosos")
    barras = resumen.rename(columns={"dias_observados": "Observados", "dias_escenario": "Escenario"})
    st.bar_chart(barras, x="ciudad", y=["Observados", "Escenario"], x_label="Ciudad", y_label="Cantidad de días")
    st.caption("La barra representa días con temperatura máxima ≥ al umbral elegido, no episodios de ola de calor.")
    prioritarias = resumen[resumen["dias_escenario"] >= minimo]
    st.markdown(f"**Ciudades a revisar:** {len(prioritarias)} alcanzan al menos {minimo} días en el escenario seleccionado.")
    st.dataframe(
        resumen.rename(columns={"ciudad": "Ciudad", "dias_analizados": "Días disponibles",
        "dias_observados": "Días observados ≥ umbral", "dias_escenario": "Días del escenario ≥ umbral",
        "dias_adicionales": "Días adicionales", "max_observada_c": "Máxima observada (°C)"}),
        hide_index=True, use_container_width=True,
    )
    with st.expander("📍 Ubicación de las ciudades analizadas"):
        ubicaciones = datos[["ciudad", "latitud", "longitud"]].drop_duplicates()
        st.map(ubicaciones, latitude="latitud", longitude="longitud", zoom=4)
        st.caption("Marcadores de coordenadas de referencia por ciudad, no estaciones de medición.")
    st.subheader("Distribución de las temperaturas máximas")
    fig, ax = plt.subplots(figsize=(9, 3.5))
    ax.hist(datos["temp_max_c"].dropna(), bins=16, edgecolor="#e2e8f0", color="#0d9488")
    ax.axvline(umbral, color="#b91c1c", linestyle="--", linewidth=2, label=f"Umbral: {umbral} °C")
    ax.set_title("Frecuencia de temperaturas máximas diarias")
    ax.set_xlabel("Temperatura máxima (°C)")
    ax.set_ylabel("Días-ciudad")
    ax.legend()
    st.pyplot(fig, clear_figure=True)
    plt.close(fig)


def tab_datos(datos, origen, anio):
    st.subheader("Tabla de registros preparados")
    st.markdown(f"**Modalidad:** {'CSV local' if 'CSV' in origen else 'API REST'} · **Fuente:** {origen}")
    mostrar = st.checkbox("Ver tabla completa", value=True)
    if mostrar:
        tabla = datos.drop(columns=["latitud", "longitud"], errors="ignore").copy()
        st.dataframe(tabla, hide_index=True, use_container_width=True)
    st.download_button("⬇️ Descargar datos filtrados en CSV (compatible con Excel)",
        data=exportar_csv(datos), file_name=f"termofuturo_datos_{anio}.csv", mime="text/csv")
    with st.expander("¿Qué hacemos para preparar los datos?"):
        st.write("1. Convertimos las fechas y los números a sus tipos adecuados; "
                 "2. retiramos registros sin fecha, ciudad o temperatura máxima; "
                 "3. descartamos duplicados de ciudad-fecha; "
                 "4. descartamos temperaturas máximas y coordenadas físicamente inverosímiles; "
                 "5. conservamos mínimos y precipitaciones faltantes como valores ausentes; "
                 "6. aplicamos filtros antes de los cálculos.")
        st.code('pd.to_datetime(df["fecha"], errors="coerce")\n'
                'df.drop_duplicates(subset=["ciudad", "fecha"])', language="python")
    st.caption("Cada fila corresponde a un día modelado de una ciudad, no a una observación puntual de una estación.")


def tab_utilidad(resumen, recomendaciones, umbral, aumento):
    st.subheader("¿Cómo puede ayudar a la comunidad?")
    st.markdown("**Uso sugerido:** comparar localidades y preparar preguntas sobre protección de personas "
                "expuestas al calor, horarios de actividades y disponibilidad de sombra e hidratación.")
    if recomendaciones and not resumen.empty:
        mayor = resumen.iloc[0]
        st.warning(f"En este escenario, **{mayor['ciudad']}** presenta "
                   f"{int(mayor['dias_escenario'])} días sobre el umbral de {umbral} °C "
                   f"y {int(mayor['dias_adicionales'])} días adicionales frente al registro histórico.")
        st.markdown("**Acciones para debatir:** habilitar zonas de sombra, revisar horarios de actividades "
                    "al aire libre, disponer de agua y consultar los avisos oficiales antes de eventos.")
    with st.expander("Límites del modelo y uso responsable", expanded=True):
        st.write(f"El aumento de +{aumento:g} °C se aplica de forma uniforme a cada máxima diaria. "
                 "Este ejercicio de sensibilidad no representa escenarios climáticos regionalizados, "
                 "cambios de humedad, adaptación, isla de calor urbana o pronósticos para 2035. "
                 "El conteo de días sobre un umbral elegido no equivale a una alerta sanitaria oficial ni "
                 "identifica por sí solo a personas vulnerables. La cobertura y resolución espacial dependen de la API.")
    st.link_button("🔎 Consultar la metodología de Open-Meteo", FUENTE_URL)


def principal():
    encabezado()
    anio, ciudades, umbral, aumento, verano, variable, minimo, recomendaciones, respaldo = controles()
    if not ciudades:
        st.warning("Selecciona al menos una ciudad en la barra lateral.")
        st.stop()
    originales, errores, origen = cargar(respaldo, ciudades, anio)
    for problema in errores:
        st.warning(f"No se pudo consultar un conjunto de datos: {problema}")
    datos = filtrar(originales, anio, ciudades, verano)
    if datos.empty:
        st.error("No hay datos para los filtros seleccionados. Verifica el año/ciudades, "
                 "la conexión o carga un CSV de respaldo generado previamente.")
        st.stop()
    resultado = simular(datos, umbral_c=umbral, aumento_c=aumento)
    resumen = resumen_por_ciudad(resultado)
    fuente_visible = (f"[{origen}]({FUENTE_URL})" if respaldo is None else origen)
    st.markdown(f"**Fuente:** {fuente_visible} · **Año:** {anio} · "
                f"**Ciudades analizadas:** {resultado['ciudad'].nunique()}")
    indicadores(resultado, resumen)
    disponibles = sorted(resultado["ciudad"].unique().tolist())
    ciudad_foco = st.selectbox("Ciudad para analizar la evolución diaria", disponibles,
                              index=disponibles.index("Santiago") if "Santiago" in disponibles else 0)
    t1, t2, t3, t4 = st.tabs(["📈 Evolución", "🧭 Comparar ciudades", "📋 Datos y Excel", "💡 Utilidad social"])
    with t1:
        tab_evolucion(resultado, ciudad_foco, variable, aumento)
    with t2:
        tab_comparacion(resumen, resultado, minimo, umbral)
    with t3:
        tab_datos(resultado, origen, anio)
    with t4:
        tab_utilidad(resumen, recomendaciones, umbral, aumento)
    st.divider()
    st.caption("Proyecto educativo · Taller de Programación II · Open-Meteo Historical Weather API. "
               "Sin datos ficticios ni pronóstico meteorológico para 2035.")


if __name__ == "__main__":
    principal()
