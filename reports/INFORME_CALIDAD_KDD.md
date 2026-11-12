# Informe de calidad KDD

Se aceptaron 87 de 100 filas y se pusieron 13 en cuarentena. La completitud fue 95.0% antes y 100.0% después; la unicidad final fue 100.0% y la validez final 100.0%. Se validaron 2 archivos y se rechazaron 1.

Se descartaron filas con campos obligatorios vacíos o inválidos, fechas no válidas para el año actual, importes no positivos, unidades menores que uno, identificadores duplicados y valores de importe fuera de 1,5 veces el rango intercuartílico. Los campos categóricos secundarios vacíos se imputaron con la moda y los timestamps de salida se expresaron en ISO 8601. Las diferencias CRLF/LF se normalizaron antes de comparar SHA-256.

Importe en el conjunto limpio: media 70.99, mediana 73.44, desviación estándar 26.34, P25 53.8 y P75 85.34.

El CSV resultante queda preparado para análisis KDD conforme a las reglas aplicadas.
