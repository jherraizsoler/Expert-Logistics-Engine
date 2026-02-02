import clips
import sqlite3

# ==========================================
# 1. PREPARAR LA "BASE DE DATOS" (Simulada)
# ==========================================
def obtener_datos_usuario_bd(user_id):
    datos_mock = {
        "user_123": {"nombre": "Juan", "sueldo": 900, "deudas": 0},
        "user_456": {"nombre": "Maria", "sueldo": 2500, "deudas": 0},
        "user_789": {"nombre": "Pedro", "sueldo": 3000, "deudas": 50000}
    }
    return datos_mock.get(user_id, None)

# ==========================================
# 2. PREPARAR EL CEREBRO (CLIPS)
# ==========================================
env = clips.Environment()

# --- ¡CORRECCIÓN IMPORTANTE! ---
# Primero definimos la ESTRUCTURA (deftemplate) antes de usarla en las reglas.
# Esto le dice a CLIPS que un 'usuario' tiene campos con nombre.
env.build("(deftemplate usuario (slot id) (slot nombre) (slot sueldo) (slot deudas))")

# Ahora sí, las reglas entenderán qué es "sueldo" y "deudas"

# Regla: Si gana menos de 1000 -> Denegado
env.build("""
(defrule denegar-por-sueldo
   (solicitud prestamo)
   (usuario (sueldo ?s &:(< ?s 1000)))
   =>
   (assert (decision "DENEGADO" "Sueldo insuficiente"))
)
""")

# Regla: Si gana más de 1000 pero tiene muchas deudas -> Denegado
env.build("""
(defrule denegar-por-deudas
   (solicitud prestamo)
   (usuario (sueldo ?s &:(>= ?s 1000)) (deudas ?d &:(> ?d 10000)))
   =>
   (assert (decision "DENEGADO" "Nivel de endeudamiento alto"))
)
""")

# Regla: Si gana más de 1000 y pocas deudas -> Aprobado
env.build("""
(defrule aprobar
   (solicitud prestamo)
   (usuario (sueldo ?s &:(>= ?s 1000)) (deudas ?d &:(<= ?d 10000)))
   =>
   (assert (decision "APROBADO" "Disfruta tu dinero"))
)
""")

# ==========================================
# 3. EL FLUJO PRINCIPAL (El "Orquestador")
# ==========================================

def procesar_mensaje_chatbot(user_id, mensaje):
    print(f"\n--- Procesando mensaje de {user_id}: '{mensaje}' ---")
    
    env.reset() # Limpiamos la mente de CLIPS para la nueva consulta

    # PASO A: Entender el Chatbot
    if "prestamo" in mensaje.lower():
        print("1. [Chatbot] Intención detectada: Solicitud de Préstamo")
        env.assert_string('(solicitud prestamo)')
    else:
        return "No entiendo qué quieres."

    # PASO B: Consultar Base de Datos
    info_bd = obtener_datos_usuario_bd(user_id)
    if not info_bd:
        return "Error: Usuario no encontrado en BD."
    
    print(f"2. [Base de Datos] Recuperado: {info_bd['nombre']}, Sueldo: {info_bd['sueldo']}")

    # PASO C: Inyectar todo a CLIPS
    hecho_usuario = f'(usuario (id {user_id}) (nombre {info_bd["nombre"]}) (sueldo {info_bd["sueldo"]}) (deudas {info_bd["deudas"]}))'
    env.assert_string(hecho_usuario)

    # PASO D: Ejecutar y Leer Decisión
    env.run()
    
    respuesta_final = "No se pudo determinar."
    
    for hecho in env.facts():
        if hecho.template.name == 'decision':
            estado = hecho[0]
            razon = hecho[1]
            respuesta_final = f"Resultado: {estado}. Motivo: {razon}"

    return respuesta_final

# ==========================================
# 4. PROBAMOS EL SISTEMA
# ==========================================

# Caso 1: Juan (Gana poco)
print(procesar_mensaje_chatbot("user_123", "Quiero pedir un prestamo"))

# Caso 2: Maria (Gana bien y sin deudas)
print(procesar_mensaje_chatbot("user_456", "Necesito un prestamo urgente"))

# Caso 3: Pedro (Gana mucho pero debe mucho)
print(procesar_mensaje_chatbot("user_789", "Solicito prestamo"))