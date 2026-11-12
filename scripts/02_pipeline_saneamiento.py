import json
import logging
from datetime import date
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
STAGING = ROOT / "staging" / "verified"
TAMPERED = ROOT / "quarantine" / "tampered"
BAD = ROOT / "quarantine" / "bad_records.csv"
PROCESSED = ROOT / "processed" / "dataset_kdd_listo.csv"
METRICS = ROOT / "output_samples" / "metricas_perfilado.json"
LOG = ROOT / "logs" / "ejecucion_pipeline.log"
REQUIRED = ["id_transaccion", "timestamp", "importe_eur", "unidades"]


def main():
    logging.basicConfig(filename=LOG, filemode="a", level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s")
    files = sorted(STAGING.glob("*.csv"))
    if not files:
        raise SystemExit("Ejecuta primero 01_verificar_integridad.py")
    data = pd.concat([pd.read_csv(p, dtype=str).assign(_origen=p.name) for p in files],
                     ignore_index=True).fillna("")
    for col in data.columns:
        if col != "_origen":
            data[col] = data[col].str.strip()

    reasons = pd.Series("", index=data.index)

    def mark(mask, text):
        reasons.loc[mask] += text + "; "

    missing = data[REQUIRED].eq("")
    mark(missing.any(axis=1), "campo obligatorio vacío")
    for col in ("importe_eur", "unidades"):
        data[col] = pd.to_numeric(data[col], errors="coerce")
        mark(data[col].isna() & ~missing[col], f"{col} inválido")
    dates = pd.to_datetime(data["timestamp"], errors="coerce")
    mark(dates.isna() & data["timestamp"].ne(""), "timestamp inválido")
    today = date.today()
    mark(dates.notna() & ((dates.dt.date > today) | (dates.dt.year < today.year)),
         "fecha fuera del año actual")
    mark(data["importe_eur"].le(0), "importe_eur debe ser > 0")
    mark(data["unidades"].lt(1), "unidades debe ser >= 1")
    mark(data["id_transaccion"].ne("") & data["id_transaccion"].duplicated(),
         "id_transaccion duplicado")

    valid = reasons.eq("")
    q1, q3 = data.loc[valid, "importe_eur"].quantile([.25, .75])
    low, high = q1 - 1.5 * (q3 - q1), q3 + 1.5 * (q3 - q1)
    outliers = valid & ~data["importe_eur"].between(low, high)
    mark(outliers, "importe_eur fuera del rango IQR 1,5")
    for i in data.index[outliers]:
        logging.warning("ANOMALÍA id=%s importe=%s", data.at[i, "id_transaccion"], data.at[i, "importe_eur"])

    bad = reasons.ne("")
    rejected = data.loc[bad].copy()
    rejected["motivo"] = reasons[bad].str.rstrip("; ")
    BAD.parent.mkdir(parents=True, exist_ok=True)
    rejected.to_csv(BAD, index=False)
    for _, row in rejected.iterrows():
        logging.warning("CUARENTENA id=%s motivo=%s", row["id_transaccion"], row["motivo"])

    clean = data.loc[~bad].copy()
    for col in ("categoria", "metodo_pago"):
        empty = clean[col].eq("")
        if empty.any():
            clean.loc[empty, col] = clean.loc[~empty, col].mode().iloc[0]
    clean["timestamp"] = dates.loc[~bad].dt.strftime("%Y-%m-%d %H:%M:%S")
    clean = clean.drop(columns="_origen")
    PROCESSED.parent.mkdir(parents=True, exist_ok=True)
    clean.to_csv(PROCESSED, index=False)

    amounts = clean["importe_eur"]
    rejected_files = len(list(TAMPERED.glob("*.csv")))
    metrics = {
        "registros_entrada": len(data), "registros_procesados": len(clean),
        "registros_cuarentena": int(bad.sum()),
        "completitud_entrada_pct": round(data.replace("", pd.NA).notna().all(axis=1).mean() * 100, 2),
        "completitud_salida_pct": round(clean.replace("", pd.NA).notna().all(axis=1).mean() * 100, 2),
        "unicidad_id_salida_pct": round(clean["id_transaccion"].nunique() / len(clean) * 100, 2),
        "validez_salida_pct": 100.0,
        "integridad_archivos": {"validados": len(files), "rechazados": rejected_files,
                                "tasa_validada_pct": round(len(files) / (len(files) + rejected_files) * 100, 2)},
        "importe_eur": {"media": round(amounts.mean(), 2), "mediana": round(amounts.median(), 2),
                        "desviacion_estandar": round(amounts.std(), 2), "percentil_25": round(amounts.quantile(.25), 2),
                        "percentil_75": round(amounts.quantile(.75), 2)},
    }
    METRICS.write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    logging.info("RESUMEN entrada=%s aceptados=%s cuarentena=%s", len(data), len(clean), int(bad.sum()))
    for path in (STAGING, TAMPERED, BAD, PROCESSED):
        logging.info("ESTRUCTURA %s", path.relative_to(ROOT))
    print(f"Entrada: {len(data)}; procesados: {len(clean)}; cuarentena: {int(bad.sum())}")


if __name__ == "__main__":
    main()
