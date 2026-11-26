import json
import time
from datetime import datetime, timedelta, timezone

from kafka import KafkaProducer

TOPIC = "telemetria-frio"
VEHICULOS = ("CAM-01", "CAM-02", "CAM-03", "CAM-04")
ANOMALIAS = {5, 10, 15, 20, 29, 34, 39, 56}

inicio = datetime.now(timezone.utc)
productor = KafkaProducer(
    bootstrap_servers="localhost:9092",
    acks="all",
    retries=5,
    max_in_flight_requests_per_connection=1,
    key_serializer=lambda clave: clave.encode("utf-8"),
    value_serializer=lambda evento: json.dumps(evento, separators=(",", ":")).encode("utf-8"),
)

emitidas = 0
for i in range(60):
    vehiculo = VEHICULOS[i % len(VEHICULOS)]
    anomalia = i in ANOMALIAS
    temperatura = round(-17.5 + (i % 4) * 0.5, 1) if anomalia else round(-20.5 + (i % 5) * 0.4, 1)
    evento = {
        "vehiculo": vehiculo,
        "temp_c": temperatura,
        "lat": round(37.3891 + (i % 10) * 0.0001, 4),
        "lon": round(-5.9845 - (i % 10) * 0.0001, 4),
        "timestamp_iso": (inicio + timedelta(seconds=i * 0.5)).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
    }
    resultado = productor.send(TOPIC, key=vehiculo, value=evento).get(timeout=10)
    emitidas += anomalia
    print(f"{vehiculo} temp={temperatura:.1f} C particion={resultado.partition} offset={resultado.offset}", flush=True)
    if i < 59:
        time.sleep(0.5)

productor.flush()
productor.close()
print(f"Anomalias emitidas: {emitidas}", flush=True)

