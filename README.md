# Laboratorio Hadoop 5075

Despliegue de un clúster Hadoop con Docker Compose para auditar HDFS, simular la caída de un DataNode y ejecutar WordCount en YARN.

## Arquitectura

Seis servicios en la red `hadoop-net`: un NameNode, tres DataNodes, un ResourceManager y un NodeManager. HDFS usa bloques de 64 MiB y replicación 2. Las interfaces web se publican en `localhost:9870` y `localhost:8088`.

## Uso

Desde `docker/`:

```powershell
docker compose up -d
docker compose ps
```

Abrir un shell en el NameNode:

```powershell
docker exec -it namenode bash
```

Al terminar, desde `docker/`, detener el clúster y eliminar sus volúmenes temporales:

```powershell
docker compose down -v
```

## Autoría

Leonardo Acchioni Mena
