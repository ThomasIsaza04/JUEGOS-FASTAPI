import sqlite3

DB_NAME = "juegos_db.sqlite3"


def obtener_conexion():
    """Abre conexión a SQLite y habilita las Claves Foráneas."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def inicializar_bd():
    """Crea las tablas e inserta datos predeterminados (usuarios, plataformas y juegos)."""
    # Importación local para evitar dependencia circular
    import seguridad

    conn = obtener_conexion()
    cursor = conn.cursor()

    # 1. Tabla Usuarios (GA4)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL,
            rol TEXT NOT NULL
        );
    """)

    # 2. Tabla Principal: Plataformas (GA2 / GA5)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS plataformas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            fabricante TEXT NOT NULL,
            anio_lanzamiento INTEGER NOT NULL
        );
    """)

    # 3. Tabla Dependiente: Juegos (GA2 / GA5)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS juegos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            genero TEXT NOT NULL,
            precio REAL NOT NULL,
            es_multijugador BOOLEAN NOT NULL DEFAULT 1,
            plataforma_id INTEGER NOT NULL,
            FOREIGN KEY (plataforma_id) REFERENCES plataformas (id) ON DELETE CASCADE
        );
    """)

    conn.commit()

    # --- SIEMBRA DE DATOS PREDETERMINADOS ---

    # A. Usuarios iniciales (si la tabla está vacía)
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    if cursor.fetchone()[0] == 0:
        admin_pass = seguridad.hashear_password("admin123")
        user_pass = seguridad.hashear_password("user123")

        cursor.execute(
            "INSERT INTO usuarios (username, hashed_password, rol) VALUES (?, ?, ?)",
            ("admin_master", admin_pass, "admin")
        )
        cursor.execute(
            "INSERT INTO usuarios (username, hashed_password, rol) VALUES (?, ?, ?)",
            ("jugador_standard", user_pass, "user")
        )
        conn.commit()

    # B. Plataformas predeterminadas (si la tabla está vacía)
    cursor.execute("SELECT COUNT(*) FROM plataformas")
    if cursor.fetchone()[0] == 0:
        plataformas_demo = [
            ("PlayStation 5", "Sony", 2020),
            ("Nintendo Switch", "Nintendo", 2017),
            ("PC - Steam", "Valve", 2003)
        ]
        cursor.executemany(
            "INSERT INTO plataformas (nombre, fabricante, anio_lanzamiento) VALUES (?, ?, ?)",
            plataformas_demo
        )
        conn.commit()

    # C. Juegos predeterminados (si la tabla está vacía)
    cursor.execute("SELECT COUNT(*) FROM juegos")
    if cursor.fetchone()[0] == 0:
        juegos_demo = [
            ("God of War Ragnarök", "Acción / Aventura", 69.99, False, 1),
            ("Spider-Man 2", "Acción", 69.99, False, 1),
            ("The Legend of Zelda: Tears of the Kingdom", "Aventura", 59.99, False, 2),
            ("Mario Kart 8 Deluxe", "Carreras", 59.99, True, 2),
            ("Counter-Strike 2", "Shooter / FPS", 0.00, True, 3)
        ]
        cursor.executemany(
            """INSERT INTO juegos (titulo, genero, precio, es_multijugador, plataforma_id) 
               VALUES (?, ?, ?, ?, ?)""",
            juegos_demo
        )
        conn.commit()

    conn.close()