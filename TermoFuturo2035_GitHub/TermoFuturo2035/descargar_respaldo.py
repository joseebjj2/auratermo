"""Ejecutar online una vez para generar el respaldo REAL del año 2025.
Uso: python descargar_respaldo.py
No rellena datos faltantes con cifras inventadas.
"""
from pathlib import Path
from datos import CIUDADES, combinar_ciudades, exportar_csv


def main():
    datos, errores = combinar_ciudades(sorted(CIUDADES), 2025)
    for error in errores:
        print("Aviso:", error)
    if datos.empty:
        raise SystemExit("No se obtuvo ningún dato real. No se generó respaldo.")
    destino = Path(__file__).parent / "data" / "respaldo_chile_2025.csv"
    destino.parent.mkdir(exist_ok=True)
    destino.write_bytes(exportar_csv(datos))
    print(f"Respaldo real guardado: {destino} | filas: {len(datos)} | ciudades: {datos['ciudad'].nunique()}")


if __name__ == "__main__":
    main()
