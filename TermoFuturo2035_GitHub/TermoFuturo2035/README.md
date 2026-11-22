# 🌡️ TERMOFUTURO 2035 · Chile

**Radar ciudadano para estudiar el calor con datos históricos reales y ensayar escenarios hipotéticos.** Proyecto académico para Taller de Programación II (Universidad San Sebastián, 2026).

> [!IMPORTANT]
> El año 2035 es parte del nombre conceptual. El simulador **no predice** el clima de 2035, no emite alertas oficiales y no permite inferir riesgo sanitario individual.

## Cómo ejecutar

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

Python 3.11+. Requiere Internet para consultar [Open-Meteo Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api) salvo que cargues un respaldo CSV real.

## ¿De dónde salen los datos y cómo obtener Excel?

La API proporciona máximas/mínimas diarias (°C) y precipitación (mm). El programa usa `requests.get()`, convierte el JSON en un DataFrame con pandas y lo prepara. En la pestaña **Datos y Excel** puedes descargar los registros filtrados en `.csv`, un formato que Excel importa. Para preparar un respaldo de 2025 en un equipo con Internet:

```bash
python descargar_respaldo.py
```

Aparecerá `data/respaldo_chile_2025.csv`. Puedes subirlo en la barra lateral si falla la API durante la defensa. **No se incluyen observaciones sintéticas** ni se rellena el respaldo con números inventados.

## Organización del repositorio

```text
TermoFuturo2035/
├── app.py                    # Interfaz y navegación (pestañas)
├── datos.py                  # requests.get, fechas, DataFrame y limpieza
├── analisis.py               # filtros, indicadores y simulación
├── descargar_respaldo.py     # crea CSV real para uso sin API
├── requirements.txt         # dependencias
├── README.txt                # archivo obligatorio para la rúbrica
├── README.md                 # instrucciones del repositorio
├── .streamlit/config.toml    # estilo visual
├── data/COMO_GENERAR_CSV.txt
├── docs/Informe_breve.pdf    # máximo tres páginas
├── docs/Presentacion.pptx    # diapositivas de apoyo
├── docs/GUIA_DEFENSA.md      # demostración y preguntas
└── tests/test_logica.py      # pruebas de funciones
```

## Cumplimiento de la rúbrica

- Fuente API REST y mención de procedencia; CSV opcional por `pd.read_csv`.
- 12+ instancias y 6+ tipos de componentes, con 3+ tipos de entrada.
- Filtros efectivos: año, ciudades, verano; umbral y desplazamiento modifican análisis.
- Tabla `st.dataframe` y cuatro indicadores `st.metric`.
- Cuatro tipos de gráficos: líneas, barras, dispersión e histograma con Matplotlib.
- Funciones de lectura, validación, cálculos, filtros y visualización.
- Interfaz con barra lateral, columnas y cuatro pestañas.
- Resultados interpretables con unidades y límites explícitos.
- Archivos reproducibles y un informe de apoyo.

## Publicación en Streamlit Community Cloud

1. Crear un repositorio GitHub con estos archivos en su raíz (incluida la carpeta oculta `.streamlit`).
2. Acceder a <https://share.streamlit.io/> y elegir **Create app**.
3. Seleccionar el repositorio, la rama `main` y el archivo de inicio `app.py`.
4. Publicar, comprobar filtros/datos y copiar la URL `*.streamlit.app` al `README.txt`.
5. Comprimir **el proyecto completo**, nombrando el ZIP con los nombres y apellidos exigidos por la profesora, y entregar por Blackboard antes de la fecha indicada.

## Límite del análisis

El aumento hipotético se aplica uniforme a máximas diarias; no modela humedad, adaptación, cambio en estacionalidad ni efectos urbanos. La calidad y resolución de las observaciones modeladas dependen de Open-Meteo. Los días sobre un umbral elegido no equivalen a una ola de calor oficialmente declarada. Los conteos no comparan directamente ciudades con coberturas temporales distintas.

## Licencias y atribución

Datos y API: [Open-Meteo](https://open-meteo.com/). Revisar condiciones actuales de uso no comercial. Este trabajo cita expresamente su fuente e incluye únicamente los datos que el servicio entregue.
