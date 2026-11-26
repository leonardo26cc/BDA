import json
import os
from pathlib import Path

from kafka import KafkaConsumer

TOPIC = "telemetria-frio"
consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers="localhost:9092",
    group_id="grupo-alertas-frio",
    auto_offset_reset="earliest",
    enable_auto_commit=False,
    session_timeout_ms=6000,
    heartbeat_interval_ms=2000,
    client_id=os.getenv("KAFKA_CLIENT_ID", "consumidor-alertas"),
    key_deserializer=lambda clave: clave.decode("utf-8"),
    value_deserializer=lambda valor: json.loads(valor.decode("utf-8")),
)
log_path = Path(__file__).resolve().parents[1] / "evidencias" / "alertas_detectadas.log"

try:
    for mensaje in consumer:
        evento = mensaje.value
        print(
            f"particion={mensaje.partition} offset={mensaje.offset} "
            f"vehiculo={mensaje.key} temp={evento['temp_c']:.1f} °C",
            flush=True,
        )
        if evento["temp_c"] > -18.0:
            registro = {"particion": mensaje.partition, "offset": mensaje.offset, **evento}
            with log_path.open("a", encoding="utf-8") as log:
                log.write(json.dumps(registro, ensure_ascii=False, separators=(",", ":")) + "\n")
                log.flush()
            print(f"ALERTA cadena de frío: {mensaje.key} {evento['temp_c']:.1f} °C", flush=True)
        consumer.commit()
except KeyboardInterrupt:
    print("Consumidor detenido", flush=True)
finally:
    consumer.close()
