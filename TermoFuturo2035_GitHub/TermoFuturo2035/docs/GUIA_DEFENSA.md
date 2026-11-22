# Guía para la defensa de TermoFuturo 2035

**Duración obligatoria:** 8 a 10 minutos en grupo. Las diapositivas apoyan la presentación y la demostración en vivo es adicional. Distribuir turnos de manera equilibrada. Este guion propone 9 minutos; ajustar tiempos con ensayo.

## Recorrido sugerido (9:00)

| Parte | Tiempo | Qué decir o mostrar |
|---|---:|---|
| 1. Problema | 0:50 | "En algunas ciudades las temperaturas altas afectan la planificación de actividades. Queremos comparar registros históricos en forma accesible". |
| 2. Propuesta | 0:55 | "TermoFuturo 2035 es un radar educativo que ayuda a analizar y debatir medidas de prevención; no predice el año 2035". |
| 3. Público y preguntas | 0:55 | Municipalidades, colegios y comunidades. ¿Qué ciudades tienen más días sobre el umbral? ¿Cómo cambia la cifra si probamos +1,5 °C? |
| 4. Fuente y limpieza | 1:00 | Mostrar `datos.py`: `requests.get`, respuesta JSON, pandas DataFrame, fechas, faltantes y duplicados. Explicar °C y mm. |
| 5. Diseño | 0:45 | Barra lateral, métricas, cuatro pestañas; por qué `st.sidebar`, `st.metric` y `st.tabs`. |
| 6. Demostración | 2:10 | Ejecutar con año 2025 y Santiago, Talca, Concepción. Mostrar la tabla, luego variar ciudades, umbral 30→32 °C, hipotético +1,5→+2 °C, y comparar gráficos. |
| 7. Hallazgos reales | 1:00 | Leer 2 valores directamente del dashboard abierto: ciudad con más días sobre el umbral y diferencia de días al simular. No inventar cifras. |
| 8. Limitaciones | 0:55 | Resolución espacial, datos modelados, no alerta oficial, aumento uniforme no predice 2035; API necesita conectividad. |
| 9. Cierre | 0:30 | Aplicación reproducible, datos reales exportables y decisiones informadas. |

**IMPORTANTE:** Antes de la exposición abrir la app con Internet, descargar el CSV real y subirlo también a GitHub. Hacer una prueba de entrada, dos filtros, dos indicadores y cuatro gráficos. La demo con respaldo se realiza cargando `data/respaldo_chile_2025.csv` en la barra lateral, no con números ficticios.

## Preguntas individuales probables y respuestas sencillas

1. **¿Qué es Streamlit?** Una biblioteca de Python que crea interfaces web interactivas sin desarrollar HTML o JavaScript manualmente.
2. **¿Qué es `st.selectbox`?** Lista desplegable para elegir una sola opción, como el año.
3. **¿Qué es `st.multiselect`?** Control que devuelve una lista de varias ciudades elegidas.
4. **¿Qué es `st.slider`?** Selector numérico que ajusta el umbral y el aumento hipotético.
5. **¿Qué es `st.checkbox`?** Retorna `True` o `False`; aquí activa el filtro de verano.
6. **¿Qué es `st.toggle`?** Interruptor booleano que permite mostrar u ocultar las ideas de prevención.
7. **¿Qué hace `st.file_uploader`?** Recibe un CSV de respaldo; `pd.read_csv()` lo transforma en DataFrame.
8. **¿Qué hace `st.download_button`?** Entrega los registros filtrados como archivo CSV compatible con Excel.
9. **¿Qué hace `st.dataframe`?** Muestra una tabla interactiva que se puede ordenar y explorar sin modificar el original.
10. **¿Qué hace `st.metric`?** Destaca un indicador calculado a partir del DataFrame filtrado.
11. **¿Qué diferencia hay entre `st.table` y `st.dataframe`?** `st.table` es estática; `st.dataframe` permite explorar y ordenar visualmente.
12. **¿Qué es pandas DataFrame?** Tabla de filas y columnas con tipos de datos para filtrar, agrupar y calcular.
13. **¿Qué hace `requests.get`?** Envía una petición HTTP GET a una dirección API con parámetros y recibe una respuesta.
14. **¿Por qué `raise_for_status()`?** Detecta respuestas HTTP fallidas para no procesar datos inválidos.
15. **¿Qué hace `.json()`?** Interpreta el cuerpo JSON devuelto por la API como estructuras Python.
16. **¿Dónde se limpian los datos?** En `preparar_datos` de `datos.py`, donde se convierten tipos, retiran faltantes críticos y duplicados.
17. **¿Para qué `groupby`?** Agrupa filas por ciudad para sumar días sobre el umbral y obtener el máximo.
18. **¿Cómo funciona el filtro de verano?** Selecciona registros de meses 12, 1 y 2 del año mostrado.
19. **¿Por qué gráfico de líneas?** Porque fecha es una variable temporal y la línea muestra evolución.
20. **¿Por qué barras?** Para comparar cantidades de días entre ciudades, antes y después del escenario.
21. **¿Por qué dispersión?** Para visualizar la relación entre máximas y precipitación, sin afirmar causalidad.
22. **¿Por qué histograma?** Para mostrar frecuencia de intervalos de temperatura.
23. **¿Qué muestra el simulador?** Suma un incremento elegido a cada máxima y vuelve a contar días ≥ umbral. Es sensibilidad hipotética, NO pronóstico.
24. **¿Qué ocurre si el aumento es cero?** Días del escenario = días observados, por definición.
25. **¿Qué pasa al elevar el umbral de 30 a 35 °C?** Ninguna temperatura cambia, pero el conteo de días que cumplen la condición puede bajar o mantenerse.
26. **¿Cómo evita duplicados?** Con `drop_duplicates(subset=["ciudad", "fecha"])`.
27. **¿Qué pasa si falla la API?** Se muestra aviso y puede cargarse un CSV real guardado previamente.
28. **¿Qué hace `st.cache_data`?** Almacena temporalmente respuestas para evitar repetir una consulta por cada cambio menor del usuario.
29. **¿Qué hace `st.tabs`?** Separa vistas dentro de una sola página, sin crear páginas Python independientes.
30. **¿Cuál es la diferencia entre `st.Page` y `st.navigation`?** Son API para crear páginas independientes; aquí no se usan porque las secciones están en `st.tabs`.
31. **¿Para qué sirve `requirements.txt`?** Indica las bibliotecas que la plataforma debe instalar.
32. **¿Qué se modifica para agregar una ciudad?** El diccionario `CIUDADES` de `datos.py` con nombre y coordenadas.

## Cómo responder una pregunta sobre el código

Describir siempre: **entrada → procesamiento → salida**. Ejemplo: "El slider devuelve `umbral`; `simular()` compara cada temperatura con ese valor; `resumen_por_ciudad()` agrupa resultados, y `st.bar_chart` los presenta."

## Checklist exacto de la rúbrica

| Bloque | Evidencia del proyecto | Estado |
|---|---|---|
| Carga API o CSV, 6 pt | `requests.get()` en `datos.py`, CSV opcional y fuente visible | Implementado; verificar Internet |
| Preparación pandas, 4 pt | Tipos, fechas, faltantes, duplicados, límites plausibles | Implementado |
| 3 gráficos y 2 métricas, 8 pt | Líneas, barras, dispersión, histograma; 4 KPI | Implementado |
| 12 instancias, 6 tipos, 3 entradas, 2 filtros, 6 pt | `selectbox` x2, `multiselect`, `slider` x2, `radio`, `number_input`, `toggle`, `checkbox` x2, `file_uploader`, `button`, `download_button`, `link_button` x2, `st.tabs`, `st.dataframe` x2, `st.metric` x4, etc. | Implementado |
| Diseño, 3 pt | Barra lateral + pestañas + títulos + unidades + advertencias | Implementado |
| Código y reproducción, 3 pt | Archivos Python, `requirements.txt`, README, URL por completar | Falta desplegar y agregar URL |
| Presentación, 20 pt | `Presentacion.pptx`, recorrido sugerido, resultados por registrar | Falta ensayar y registrar cifras reales |
| Individual, 50 pt | Preguntas de esta guía; practicar `app.py`, `datos.py`, `analisis.py` | Estudiar cada integrante |

## Detalles que deben completar ustedes

1. Nombres y apellidos en `README.txt`, portada e informe.
2. URL pública real en `README.txt` y presentación, después del despliegue.
3. A partir de la aplicación con datos reales, completar al menos dos hallazgos numéricos en el informe y presentación. No dejar placeholders en la versión entregada.
4. Generar el respaldo CSV con `python descargar_respaldo.py` y verificar que se puede cargar antes de la evaluación oral.
5. Cambiar el nombre del ZIP final por `Solemne3_NombreApellido_NombreApellido.zip` y enviarlo por Blackboard.
