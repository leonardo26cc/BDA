import hashlib
import os
import pandas as pd

def calcular_sha256(ruta_fichero):
    sha = hashlib.sha256()
    with open(ruta_fichero, "rb") as f:
        for bloque in iter(lambda: f.read(4096), b""):
            sha.update(bloque)
    return sha.hexdigest()

def limpiar_datos(origen, destino):
    df = pd.read_csv(origen)
    # Deduplicación
    df = df.drop_duplicates()
    # Eliminación de nulos en variables clave
    df = df.dropna(subset=['destino', 'peso_kg', 'temp_celsius'])
    # Filtros lógicos
    df = df[df['peso_kg'] > 0]
    df = df[df['temp_celsius'] <= 50]
    df = df[df['estado_envio'] != 'DESCONOCIDO_ERROR']
    df.to_csv(destino, index=False)

if __name__ == "__main__":
    base = os.path.dirname(os.path.abspath(__file__))
    datos = os.path.join(base, "..", "datos")
    f_raw = os.path.join(datos, "telemetria_envios.csv")
    f_clean = os.path.join(datos, "telemetria_limpia.csv")

    h_raw = calcular_sha256(f_raw)
    print(f"SHA256 original: {h_raw}")

    limpiar_datos(f_raw, f_clean)

    h_clean = calcular_sha256(f_clean)
    print(f"SHA256 depurado: {h_clean}")
