<?php
function conectar() {
    $host = 'localhost';
    $db   = 'prueba1';
    $user = 'root';
    $pass = '';
    $charset = 'utf8mb4';

    $dsn = "mysql:host=$host;dbname=$db;charset=$charset";
    try {
        $pdo = new PDO($dsn, $user, $pass, [
            PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
        ]);
        return $pdo;
    } catch (PDOException $e) {
        die("Error de conexión: " . $e->getMessage());
    }
}

function insertar($tabla, $datos) {
    $pdo = conectar();

    $campos = [];
    $valores = [];
    $placeholders = [];

    foreach ($datos as $campo => $valor) {
        if ($campo !== 'tabla') {
            $campos[] = $campo;
            $valores[] = $valor;
            $placeholders[] = '?';
        }
    }

    $sql = "INSERT INTO `$tabla` (" . implode(',', $campos) . ") VALUES (" . implode(',', $placeholders) . ")";
    $stmt = $pdo->prepare($sql);
    $stmt->execute($valores);

    return $pdo->lastInsertId();
}

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['tabla'])) {
    $tabla = $_POST['tabla'];
    $datos = $_POST;
    $id = insertar($tabla, $datos);
    echo "Registro insertado correctamente en la tabla $tabla. ID: $id";
} else {
    echo "Datos inválidos.";
}
?>