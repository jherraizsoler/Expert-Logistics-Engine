import clips
import string # Para limpiar puntos y comas

env = clips.Environment()

# =========================================================
# 1. BASE DE CONOCIMIENTO
# =========================================================

# GRAVE
env.assert_string('(es-grave infarto)')
env.assert_string('(es-grave rotura)')
env.assert_string('(es-grave apendicitis)')
env.assert_string('(es-grave ictus)')

# MODERADO
env.assert_string('(es-moderado fiebre)')
env.assert_string('(es-moderado gripe)')
env.assert_string('(es-moderado muelas)') # Ojo: palabra simple mejor
env.assert_string('(es-moderado ansiedad)')

# NORMAL
env.assert_string('(es-normal cansancio)')
env.assert_string('(es-normal rasguño)')
env.assert_string('(es-normal agujetas)')

# =========================================================
# 2. LAS REGLAS
# =========================================================

env.build("""
(defrule caso-urgente
   (sintoma ?x)
   (es-grave ?x)
   =>
   (assert (resultado "¡URGENCIA! Ve corriendo al HOSPITAL por" ?x))
)
""")

env.build("""
(defrule caso-moderado
   (sintoma ?x)
   (es-moderado ?x)
   =>
   (assert (resultado "Pide cita en tu centro de salud por" ?x))
)
""")

env.build("""
(defrule caso-leve
   (sintoma ?x)
   (es-normal ?x)
   =>
   (assert (resultado "No es nada. Descansa un poco por" ?x))
)
""")

# =========================================================
# 3. PROCESAMIENTO INTELIGENTE DE LA FRASE (Aquí está el cambio)
# =========================================================
print("--- MÉDICO CLIPS V4 (Detector de Palabras Clave) ---")
print("Puedes decir: 'Creo que tengo fiebre', 'Me da un infarto', etc.")

entrada_usuario = input("¿Qué te ocurre?: ").lower()

# LIMPIEZA: Quitamos comas y puntos para que "infarto." sea igual a "infarto"
# Esto convierte "hola, mundo." en "hola mundo"
tabla_limpieza = str.maketrans("", "", string.punctuation)
frase_limpia = entrada_usuario.translate(tabla_limpieza)

# TROCEADO: Convertimos la frase en una lista de palabras
# "tengo mucha fiebre" -> ["tengo", "mucha", "fiebre"]
palabras = frase_limpia.split()

# BUCLE: Insertamos CADA palabra como un posible síntoma
for palabra in palabras:
    # CLIPS recibirá: (sintoma tengo), (sintoma mucha), (sintoma fiebre)
    env.assert_string(f'(sintoma {palabra})')

# =========================================================
# 4. EJECUCIÓN
# =========================================================
num = env.run()

if num == 0:
    print(f"\n>>> No detecté ninguna palabra médica conocida en tu palabra, {palabra}")
else:
    # Usamos un conjunto (set) para evitar repetir mensajes si detecta dos veces lo mismo
    mensajes_unicos = set()
    
    for hecho in env.facts():
        if hecho.template.name == 'resultado':
            # Creamos el texto de respuesta
            texto_respuesta = f"{hecho[0]} ({hecho[1]})"
            mensajes_unicos.add(texto_respuesta)
            
    # Imprimimos los resultados sin repetir
    for msg in mensajes_unicos:
        print(f"\n>>> DIAGNÓSTICO: {msg}")