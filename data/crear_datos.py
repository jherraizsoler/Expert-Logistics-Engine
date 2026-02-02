import sqlite3
import os

# Esto detecta automáticamente la carpeta donde está este script (la carpeta 'data')
DIRECTORIO_ACTUAL = os.path.dirname(os.path.abspath(__file__))
# Une esa carpeta con el nombre del archivo
DB_FILE = os.path.join(DIRECTORIO_ACTUAL, 'logistica.db')

def crear_base_datos():
    # ==========================================
    # 1. COMPROBACIÓN DE EXISTENCIA
    # ==========================================
    mensaje_estado = ""
    
    if os.path.exists(DB_FILE):
        # Si existe, preparamos el mensaje de regeneración y la borramos
        mensaje_estado = f"⚠️  AVISO: La base de datos '{DB_FILE}' ya existía.\n    -> Se ha ELIMINADO y RECONSTRUIDO totalmente (datos reiniciados)."
        os.remove(DB_FILE)
    else:
        # Si no existe, preparamos el mensaje de creación inicial
        mensaje_estado = f"✅ ÉXITO: Base de datos '{DB_FILE}' CREADA satisfactoriamente por primera vez."

    # ==========================================
    # 2. CREACIÓN DE ESTRUCTURA Y DATOS
    # ==========================================
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Tabla Vehículos
    cursor.execute('''
        CREATE TABLE vehiculos (
            matricula TEXT PRIMARY KEY,
            tipo TEXT,
            carga_max_kg INTEGER
        )
    ''')

    # Tabla Pedidos (Con columnas para resultados)
    cursor.execute('''
        CREATE TABLE pedidos (
            id TEXT PRIMARY KEY,
            producto TEXT,
            peso_kg INTEGER,
            tipo_carga TEXT,
            prioridad TEXT,
            vehiculo_asignado TEXT DEFAULT NULL,
            estado_final TEXT DEFAULT 'PENDIENTE'
        )
    ''')

    # Insertar Flota
    lista_vehiculos = [
        ('CAMION-01', 'camion', 5000),
        ('FURGO-A', 'furgoneta', 800),
        ('MOTO-RX', 'moto', 15)
    ]
    cursor.executemany("INSERT INTO vehiculos VALUES (?,?,?)", lista_vehiculos)

    # Insertar Pedidos
    lista_pedidos = [
        ('P-100', 'Sofa Cama', 150, 'voluminoso', 'normal'),
        ('P-101', 'Cajas Libros', 50, 'normal', 'normal'),
        ('P-102', 'Cajas Ropa', 50, 'normal', 'normal'),
        ('P-103', 'Llaves', 1, 'normal', 'urgente'),
        ('P-104', 'Piano', 400, 'voluminoso', 'normal'),
        ('P-105', 'Elefante', 6000, 'voluminoso', 'normal')
    ]
    cursor.executemany("INSERT INTO pedidos (id, producto, peso_kg, tipo_carga, prioridad) VALUES (?,?,?,?,?)", lista_pedidos)

    conn.commit()
    conn.close()

    # ==========================================
    # 3. INFORME FINAL
    # ==========================================
    print("\n" + "="*60)
    print(mensaje_estado)
    print("="*60 + "\n")

if __name__ == "__main__":
    crear_base_datos()