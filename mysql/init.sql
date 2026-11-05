CREATE DATABASE IF NOT EXISTS ventas_db;
USE ventas_db;

CREATE TABLE IF NOT EXISTS clientes (
    cliente_id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    ciudad VARCHAR(100) NOT NULL,
    fecha_registro DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS pedidos (
    pedido_id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NOT NULL,
    fecha_pedido DATE NOT NULL,
    total DECIMAL(10, 2) NOT NULL,
    estado VARCHAR(50) NOT NULL,
    INDEX (cliente_id)
);

-- Procedimiento para generar 1000 registros en clientes y pedidos
DELIMITER $$
CREATE PROCEDURE GenerarDatosPrueba()
BEGIN
    DECLARE i INT DEFAULT 1;
    DECLARE random_total DECIMAL(10,2);
    DECLARE random_dias INT;
    DECLARE random_estado VARCHAR(50);
    
    WHILE i <= 1000 DO
        INSERT INTO clientes (nombre, email, ciudad, fecha_registro)
        VALUES (
            CONCAT('Cliente_', i),
            CONCAT('cliente', i, '@ejemplo.com'),
            ELT(FLOOR(1 + RAND() * 5), 'Madrid', 'Sevilla', 'Barcelona', 'Valencia', 'Bilbao'),
            DATE_SUB(CURDATE(), INTERVAL FLOOR(RAND() * 365) DAY)
        );
        
        SET random_total = ROUND(10.0 + (RAND() * 990.0), 2);
        SET random_dias = FLOOR(RAND() * 180);
        SET random_estado = ELT(FLOOR(1 + RAND() * 4), 'ENTREGADO', 'ENVIADO', 'PENDIENTE', 'CANCELADO');
        
        INSERT INTO pedidos (cliente_id, fecha_pedido, total, estado)
        VALUES (
            i,
            DATE_SUB(CURDATE(), INTERVAL random_dias DAY),
            random_total,
            random_estado
        );
        
        SET i = i + 1;
    END WHILE;
END$$
DELIMITER ;

CALL GenerarDatosPrueba();
DROP PROCEDURE GenerarDatosPrueba;

-- Asegurar usuario sqoopuser y permisos
CREATE USER IF NOT EXISTS 'sqoopuser'@'%' IDENTIFIED WITH mysql_native_password BY 'sqooppassword';
ALTER USER 'sqoopuser'@'%' IDENTIFIED WITH mysql_native_password BY 'sqooppassword';
GRANT ALL PRIVILEGES ON ventas_db.* TO 'sqoopuser'@'%';
FLUSH PRIVILEGES;
