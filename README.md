# Laboratorio Hadoop 5075

Despliegue de un clúster Hadoop con Docker Compose, auditoría de bloques HDFS, prueba de tolerancia a fallos y ejecución WordCount en YARN.

## Arquitectura

Seis servicios en la red aislada `hadoop-net`: un NameNode, tres DataNodes, un ResourceManager y un NodeManager. HDFS usa bloques de 64 MiB y replicación 2. Las interfaces web se publican en `localhost:9870` y `localhost:8088`.

## Uso

Desde `docker/`:

```powershell
docker compose -f compose.yml up -d
docker compose -f compose.yml ps
```

Abrir un shell en el NameNode:

```powershell
docker exec -it namenode bash
```

Al terminar, desde `docker/`, detener el clúster:

```powershell
docker compose -f compose.yml down -v
```

## Autoría

Leonardo Acchioni Mena
