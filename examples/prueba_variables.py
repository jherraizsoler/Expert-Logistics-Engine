import clips

env = clips.Environment()

# 1. LA BASE DE CONOCIMIENTO (Lo que el médico "sabe")
# Le enseñamos qué cosas consideramos graves.
# Fíjate que NO incluimos "cafe".
env.assert_string('(es-grave fiebre)')
env.assert_string('(es-grave cabeza)')
env.assert_string('(es-grave tos)')
env.assert_string('(es-grave rotura)')
env.assert_string('(es-grave insulina)')
env.assert_string('(es-grave ansiedad)')
env.assert_string('(es-grave receta)')


# 2. LA REGLA "FILTRO"
# Aquí está la magia del Capítulo 3 y 4 juntos.
# Usamos la misma variable ?x en dos líneas.
# CLIPS buscará algo que sea síntoma Y que ADEMÁS sea grave.
regla = """
(defrule detectar-urgencia
   (sintoma ?algo)          ; 1. El usuario tiene "algo"
   (es-grave ?algo)         ; 2. Y ese "algo" está en mi lista de graves
   =>
   (assert (resultado "¡URGENTE! Ve al hospital por" ?algo))
)
"""
env.build(regla)

# 3. PREGUNTAR AL USUARIO
print("--- MÉDICO AUTOMÁTICO V2 ---")
print("Cosas graves que conozco: fiebre, cabeza, tos, sangrado")
entrada = input("¿Qué tienes? (prueba con 'cafe' y luego con 'tos'): ")

# Insertamos el síntoma del usuario
env.assert_string(f'(sintoma {entrada})')

# 4. EJECUTAR
num_activaciones = env.run()

# 5. RESULTADO
# Si num_activaciones es 0, es que la regla no saltó (porque no era grave).
if num_activaciones == 0:
    print(f"\n>>> DIAGNÓSTICO: Nada de qué preocuparse. El '{entrada}' no es grave.")
else:
    # Buscamos el mensaje de urgencia
    for hecho in env.facts():
        if hecho.template.name == 'resultado':
            print(f"\n>>> {hecho[0]} {hecho[1]}")