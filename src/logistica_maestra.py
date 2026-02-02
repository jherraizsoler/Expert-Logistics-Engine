import clips

# Inicializamos el cerebro CLIPS
env = clips.Environment()

# ==================================================================================
# 1. DEFINICIÓN DE ESTRUCTURAS
# ==================================================================================

# Estructura del Vehículo
env.build("""
(deftemplate vehiculo
    (slot matricula)
    (slot tipo (allowed-values moto furgoneta camion camion-frigo))
    (slot carga-max-kg)
    (slot estado (default disponible))
)
""")

# Estructura del Pedido
env.build("""
(deftemplate pedido
    (slot id)
    (slot producto)
    (slot peso-kg)
    (slot tipo-carga (allowed-values normal fragil refrigerado voluminoso))
    (slot tiempo-espera-minutos (default 0))
    (slot prioridad (default normal))
)
""")

# Estructura de la Asignación (El resultado)
env.build("""
(deftemplate asignacion
    (slot id-pedido)
    (slot matricula-vehiculo)
    (slot motivo)
    (slot tiempo-estimado)
)
""")

# ==================================================================================
# 2. REGLAS DE NEGOCIO (LÓGICA ACTUALIZADA)
# ==================================================================================

# REGLA 1: Aumentar prioridad si lleva mucho esperando (+60 min)
env.build("""
(defrule detectar-retrasos
    ?p <- (pedido (tiempo-espera-minutos ?t &:(> ?t 60)) (prioridad normal))
    =>
    (modify ?p (prioridad urgente))
    (printout t ">>> [ALERTA] Pedido retrasado detectado. Subiendo prioridad!" crlf)
)
""")

# REGLA 2: Asignar REFRIGERADOS (Solo a Camiones Frigoríficos)
env.build("""
(defrule asignar-refrigerado
    (pedido (id ?pid) (tipo-carga refrigerado) (peso-kg ?peso))
    (vehiculo (matricula ?m) (tipo camion-frigo) (estado disponible) (carga-max-kg ?cap))
    (test (<= ?peso ?cap))
    =>
    (assert (asignacion (id-pedido ?pid) 
                        (matricula-vehiculo ?m) 
                        (motivo "Cadena de frio requerida")
                        (tiempo-estimado "4 horas")))
)
""")

# REGLA 3: Asignar URGENTES PEQUEÑOS (A Motos)
env.build("""
(defrule asignar-moto-rapida
    (pedido (id ?pid) (prioridad urgente) (peso-kg ?peso &:(< ?peso 10)) (tipo-carga normal))
    (vehiculo (matricula ?m) (tipo moto) (estado disponible))
    =>
    (assert (asignacion (id-pedido ?pid) 
                        (matricula-vehiculo ?m) 
                        (motivo "Envio Flash por Moto")
                        (tiempo-estimado "30 min")))
)
""")

# REGLA 4: Asignar VOLUMINOSOS O PESADOS (A Camiones)
env.build("""
(defrule asignar-carga-pesada
    (pedido (id ?pid) (peso-kg ?peso) (tipo-carga ?t))
    (vehiculo (matricula ?m) (tipo camion) (estado disponible) (carga-max-kg ?cap))
    (test (or (>= ?peso 500) (eq ?t voluminoso))) 
    (test (<= ?peso ?cap))
    =>
    (assert (asignacion (id-pedido ?pid) 
                        (matricula-vehiculo ?m) 
                        (motivo "Requiere transporte pesado")
                        (tiempo-estimado "24 horas")))
)
""")

# REGLA 5: Asignar ESTÁNDAR (Furgonetas)
env.build("""
(defrule asignar-estandar
    (pedido (id ?pid) (peso-kg ?peso) (tipo-carga ?t))
    (vehiculo (matricula ?m) (tipo furgoneta) (estado disponible) (carga-max-kg ?cap))
    (test (and (> ?peso 10) (< ?peso 500))) 
    (test (neq ?t refrigerado))
    (test (neq ?t voluminoso))  ; <--- LÍNEA NUEVA: Si es grande, NO lo quiero.
    (test (<= ?peso ?cap))
    =>
    (assert (asignacion (id-pedido ?pid) 
                        (matricula-vehiculo ?m) 
                        (motivo "Logistica estandar")
                        (tiempo-estimado "3 horas")))
)
""")

# ==================================================================================
# 3. CARGA DE DATOS
# ==================================================================================

print("--- INICIANDO SISTEMA DE GESTIÓN LOGÍSTICA (V3 - Logic Fixed) ---")

vehiculos_db = [
    "(vehiculo (matricula MOTO-01) (tipo moto) (carga-max-kg 15))",
    "(vehiculo (matricula FURGO-A) (tipo furgoneta) (carga-max-kg 800))",
    "(vehiculo (matricula CAMION-X) (tipo camion) (carga-max-kg 5000))",
    "(vehiculo (matricula FRIGO-Z) (tipo camion-frigo) (carga-max-kg 3000))"
]

pedidos_entrantes = [
    "(pedido (id 101) (producto Pescado) (peso-kg 200) (tipo-carga refrigerado))",
    "(pedido (id 102) (producto Documentos) (peso-kg 2) (prioridad urgente) (tipo-carga normal))",
    "(pedido (id 103) (producto Sofa) (peso-kg 150) (tipo-carga voluminoso))",
    "(pedido (id 104) (producto Cajas-Ropa) (peso-kg 50) (tiempo-espera-minutos 90) (tipo-carga normal))" 
]

print("Cargando flota y pedidos...")
for v in vehiculos_db:
    env.assert_string(v)

for p in pedidos_entrantes:
    env.assert_string(p)

# ==================================================================================
# 4. EJECUCIÓN Y RESULTADOS
# ==================================================================================

print("Calculando rutas óptimas...")
env.run()

print("\n--- INFORME DE ASIGNACIONES ---")
print(f"{'PEDIDO':<10} {'VEHÍCULO':<15} {'TIEMPO':<15} {'MOTIVO'}")
print("-" * 75)

asignaciones_encontradas = False

for hecho in env.facts():
    if hecho.template.name == 'asignacion':
        asignaciones_encontradas = True
        pid = hecho['id-pedido']
        veh = hecho['matricula-vehiculo']
        tiempo = hecho['tiempo-estimado']
        motivo = hecho['motivo']
        
        print(f"{pid:<10} {veh:<15} {tiempo:<15} {motivo}")

if not asignaciones_encontradas:
    print("No se pudieron asignar pedidos.")