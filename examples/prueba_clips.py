import clips

# 1. Crear el entorno (El cerebro vacío)
env = clips.Environment()

# 2. Definir la lógica (La Regla)
# Le decimos: "Si el usuario tiene fiebre, entonces el diagnóstico es gripe".
# Fíjate que la acción es crear un nuevo hecho (diagnostico ...)
env.build("""
(defrule regla-gripe
   (sintoma fiebre)
   =>
   (assert (diagnostico "Posible Gripe"))
   (printout t ">>> CLIPS dice: ¡He encontrado un problema!" crlf)
)
""")

# 3. Meter el Input (El Hecho inicial)
print("Python: Insertando datos del paciente...")
env.assert_string('(sintoma fiebre)')

# 4. Ejecutar (El Run)
# Esto hace que CLIPS piense. Si las reglas coinciden, se disparan.
env.run()

# 5. OBTENER LA RESOLUCIÓN (Lo importante)
# CLIPS no hace "return". Tenemos que leer su memoria para ver qué ha deducido.

resolucion_encontrada = False

print("\n--- Buscando resultados en la memoria de CLIPS ---")
for hecho in env.facts():
    # 'hecho' es un objeto complejo.
    # hecho.template.name nos dice el nombre (ej: "diagnostico", "sintoma")
    
    if hecho.template.name == 'diagnostico':
        # ¡Bingo! Encontramos un hecho de tipo diagnóstico.
        # hecho[0] es el primer valor dentro del paréntesis.
        mensaje = hecho[0]
        print(f"RESULTADO FINAL: {mensaje}")
        resolucion_encontrada = True

if not resolucion_encontrada:
    print("CLIPS no llegó a ninguna conclusión.")