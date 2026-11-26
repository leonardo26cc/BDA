# FríoSur Logística: telemetría con Kafka

Práctica individual del módulo 5074. Prototipo de ingestión de telemetría frigorífica con Kafka 4.0 en modo KRaft.

## Entorno

Un broker combinado (broker y controller) en KRaft, sin ZooKeeper, accesible desde el equipo anfitrión en `localhost:9092`. El topic `telemetria-frio` tiene tres particiones y factor de replicación 1.

## Arranque

Desde la raíz del proyecto:

```powershell
docker compose -f compose.yml up -d
docker logs kafka-lab04
```

Crear el topic y guardar la evidencia E1:

```powershell
docker exec kafka-lab04 /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --create --topic telemetria-frio --partitions 3 --replication-factor 1
docker exec kafka-lab04 /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --describe --topic telemetria-frio | Tee-Object evidencias/E1_topic_describe.txt
```

Instalar el cliente Python:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Antes de repetir la prueba, vaciar el registro anterior y reiniciar el broker para tener topic y offsets limpios:

```powershell
Clear-Content evidencias/alertas_detectadas.log -ErrorAction SilentlyContinue
docker compose -f compose.yml down -v
docker compose -f compose.yml up -d
```

Crear de nuevo el topic con los comandos anteriores. En dos terminales, iniciar los consumidores:

```powershell
$env:KAFKA_CLIENT_ID = "consumidor-A"
python src/consumidor_alertas.py
```

En la segunda terminal:

```powershell
$env:KAFKA_CLIENT_ID = "consumidor-B"
python src/consumidor_alertas.py
```

Antes de iniciar el productor, guardar la asignación inicial en E3-A:

```powershell
docker exec kafka-lab04 /opt/kafka/bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --describe --group grupo-alertas-frio | Tee-Object evidencias/E3A_group_antes_fallo.txt
```

En una tercera terminal, iniciar el productor y guardar su salida completa en E2:

```powershell
python src/productor_frio.py | Tee-Object evidencias/E2_productor_salida.txt
```

Cuando se hayan enviado entre 25 y 30 eventos, detener el consumidor A con Ctrl+C. Tras acabar el productor y esperar al reequilibrio, guardar la salida del grupo en E3-B. Debe quedar un solo consumidor con las tres particiones y `LAG` igual a 0:

```powershell
docker exec kafka-lab04 /opt/kafka/bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --describe --group grupo-alertas-frio | Tee-Object evidencias/E3B_group_despues_fallo.txt
```

Detener el consumidor B con Ctrl+C. El productor emite 60 eventos y 8 anomalías. E4 es `evidencias/alertas_detectadas.log`; debe contener 8 líneas. Los consumidores escriben y vacían el registro de alerta antes de confirmar el offset.

## Análisis arquitectónico

Kafka evita crear un fichero HDFS por cada vehículo y minuto. Cada partición mantiene un log append-only dividido en segmentos, reduciendo los pequeños ficheros y metadatos que el NameNode debe gestionar. Kafka conserva eventos durante el periodo de retención configurado; no sustituye HDFS para almacenamiento histórico de largo plazo [1], [5].

La clave `vehiculo` envía todos los eventos de un camión a una única partición, donde Kafka conserva el orden. Sin clave, los eventos pueden distribuirse entre particiones y se pierde ese orden por vehículo. Un grupo con cuatro consumidores y tres particiones dejaría una instancia sin asignación, ya que cada partición solo puede pertenecer a un consumidor del mismo grupo [1], [6].

Para que el anfitrión use `localhost:9092` y Spark use `kafka:9092`, se separarían los puertos internos: `KAFKA_LISTENERS=EXTERNAL://:9093,INTERNAL://:9092,CONTROLLER://:9094` y `KAFKA_ADVERTISED_LISTENERS=EXTERNAL://localhost:9092,INTERNAL://kafka:9092`. Compose publicaría `9092:9093`; además se definirían los tres protocolos en `KAFKA_LISTENER_SECURITY_PROTOCOL_MAP` y `INTERNAL` en `KAFKA_INTER_BROKER_LISTENER_NAME` [2], [7].

## Referencias

[1] Apache Software Foundation, “Basic Kafka Operations,” Apache Kafka 4.0 Documentation, [en línea]. Disponible en: https://kafka.apache.org/40/operations/basic-kafka-operations/.

[2] Apache Software Foundation, “Apache Kafka Docker Image,” Docker Hub, [en línea]. Disponible en: https://hub.docker.com/r/apache/kafka.

[3] Apache Software Foundation, “KRaft,” Apache Kafka 4.0 Documentation, [en línea]. Disponible en: https://kafka.apache.org/40/operations/kraft/.

[4] “kafka-python-ng 2.2.3,” Python Package Index, [en línea]. Disponible en: https://pypi.org/project/kafka-python-ng/2.2.3/.

[5] Apache Software Foundation, “HDFS Architecture,” Apache Hadoop Documentation, [en línea]. Disponible en: https://hadoop.apache.org/docs/stable/hadoop-project-dist/hadoop-hdfs/HdfsDesign.html.

[6] Apache Software Foundation, “Producer Configs,” Apache Kafka 4.0 Documentation, [en línea]. Disponible en: https://kafka.apache.org/40/configuration/producer-configs/.

[7] Apache Software Foundation, “Broker Configs: listeners and advertised.listeners,” Apache Kafka 4.0 Documentation, [en línea]. Disponible en: https://kafka.apache.org/40/configuration/broker-configs/.
