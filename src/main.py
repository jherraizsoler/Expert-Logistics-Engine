import clips
import sqlite3
import os

# ==========================================
# GESTIÓN DINÁMICA DE RUTAS
# ==========================================
# Detectamos dónde está 'main.py' (en /src)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# El .clp está en la misma carpeta que este script (/src)
CLIPS_FILE = os.path.join(BASE_DIR, 'logistica.clp')

# La base de datos está en la carpeta hermana /data (subimos un nivel y entramos en data)
DB_FILE = os.path.join(BASE_DIR, '..', 'data', 'logistica.db')

def cargar_datos_desde_sqlite(env):
    """Lee la BD y carga Hechos en CLIPS"""
    if not os.path.exists(DB_FILE):
        print(f"❌ ERROR: No se encuentra la BD en: {DB_FILE}")
        print("Asegúrate de ejecutar primero: python data/crear_datos.py")
        return False

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    print("\n--- 1. LEYENDO BASE DE DATOS ---")
    
    # Cargar Vehículos
    cursor.execute("SELECT matricula, tipo, carga_max_kg FROM vehiculos")
    for mat, tipo, carga in cursor.fetchall():
        env.assert_string(f'(vehiculo (matricula "{mat}") (tipo {tipo}) (carga-max-kg {carga}))')

    # Cargar Pedidos (Solo los que están PENDIENTES)
    cursor.execute("SELECT id, peso_kg, tipo_carga, prioridad FROM pedidos WHERE estado_final='PENDIENTE'")
    filas = cursor.fetchall()
    for pid, peso, tipo, prio in filas:
        env.assert_string(f'(pedido (id "{pid}") (peso-kg {peso}) (tipo-carga {tipo}) (prioridad {prio}))')
        print(f"📦 Cargado pedido pendiente: {pid}")

    conn.close()
    return True

def guardar_resultados_sql(lista_asignaciones):
    """Recibe una lista de tuplas (id_pedido, matricula, motivo) y actualiza SQL"""
    if not lista_asignaciones:
        print("⚠️ No hay asignaciones nuevas para guardar.")
        return

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    print(f"\n--- 4. GUARDANDO {len(lista_asignaciones)} ASIGNACIONES EN SQL ---")
    
    # La lista de entrada es (id, matricula, motivo)
    # Nuestra query espera: vehiculo, estado, id
    datos_para_sql = [ (veh, mot, pid) for (pid, veh, mot) in lista_asignaciones ]
    
    query = "UPDATE pedidos SET vehiculo_asignado = ?, estado_final = ? WHERE id = ?"
    cursor.executemany(query, datos_para_sql)
    conn.commit()
    
    print("✅ Base de datos actualizada con éxito.")
    conn.close()

def main():
    env = clips.Environment()
    
    # Cargar el archivo de reglas
    if not os.path.exists(CLIPS_FILE):
        print(f"❌ ERROR: No se encuentra el archivo de reglas en: {CLIPS_FILE}")
        return

    try:
        env.load(CLIPS_FILE)
    except Exception as e:
        print(f"❌ Error crítico cargando reglas CLIPS: {e}")
        return

    # 1. Cargar datos
    if not cargar_datos_desde_sqlite(env):
        return

    # 2. Ejecutar motor de inferencia
    print("\n--- 2. PENSANDO (MOTOR CLIPS) ---")
    env.run()

    # 3. Recolectar Resultados de la memoria de CLIPS
    print("\n--- 3. REPORTE EN MEMORIA ---")
    print(f"{'PEDIDO':<10} {'ASIGNADO A':<15} {'MOTIVO'}")
    print("-" * 50)

    asignaciones_para_guardar = []
    
    for hecho in env.facts():
        if hecho.template.name == 'asignacion':
            p_id = hecho['id-pedido']
            v_mat = hecho['matricula-vehiculo']
            motivo = hecho['motivo']
            
            print(f"{p_id:<10} {v_mat:<15} {motivo}")
            asignaciones_para_guardar.append((p_id, v_mat, motivo))

    # 4. Persistir
    guardar_resultados_sql(asignaciones_para_guardar)

    # 5. Verificación Final
    print("\n--- 🏁 VERIFICACIÓN FINAL EN SQL ---")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, vehiculo_asignado, estado_final FROM pedidos")
    for fila in cursor.fetchall():
        print(f"ID: {fila[0]} | Asignado a: {str(fila[1]):<10} | Estado: {fila[2]}")
    conn.close()

if __name__ == "__main__":
    main()