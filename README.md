# 📦 Expert-Logistics-Engine: Sistema Experto de Optimización

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![CLIPS](https://img.shields.io/badge/Engine-CLIPS-green.svg)](http://www.clipsrules.net/)
[![SQLite](https://img.shields.io/badge/Database-SQLite-lightgrey.svg)](https://www.sqlite.org/)

**Expert-Logistics-Engine** es un sistema inteligente de toma de decisiones diseñado para optimizar la logística de transporte y la gestión de flotas. Utiliza un motor de reglas basado en **CLIPS** e integrado con **Python**, permitiendo automatizar asignaciones complejas que tradicionalmente requerirían supervisión humana.

---

## 🚀 Funcionalidades Clave

* **Motor de Reglas Avanzado**: Implementación de lógica de negocio (prioridades, tipos de carga, capacidades de vehículos) mediante el lenguaje de sistemas expertos CLIPS.
* **Gestión de Flota Híbrida**: Capacidad para asignar desde motos para entregas urgentes hasta camiones frigoríficos para cargas refrigeradas.
* **Persistencia en SQLite**: Integración completa con bases de datos para leer pedidos pendientes y persistir las decisiones tomadas por la IA.
* **Análisis Multicriterio**: El sistema evalúa peso, tipo de carga (frágil, voluminoso, refrigerado) y tiempo de espera para priorizar envíos.

---

## 🛠️ Arquitectura del Sistema

El proyecto sigue la arquitectura de un **Sistema Experto Moderno**:

1.  **Base de Conocimientos**: Definida mediante plantillas (`deftemplate`) y reglas (`defrule`) que modelan el conocimiento experto en logística.
2.  **Motor de Inferencia**: Gestionado por `clipspy`, que procesa los hechos (pedidos y vehículos) y dispara las reglas de asignación óptima.
3.  **Capa de Datos**: Python actúa como puente (middleware), extrayendo datos de `logistica.db` e inyectándolos en el entorno de CLIPS.

---

## 📂 Estructura del Proyecto

```text
Expert-Logistics-Engine/
├── src/
│   ├── main.py                # Orquestador: conecta SQL con CLIPS
│   └── logistica.clp          # Reglas de negocio (Sistemas Expertos)
├── data/
│   ├── crear_datos.py         # Script para inicializar la DB
│   └── logistica.db           # Base de datos SQLite (Generada)
├── scripts_adicionales/       # Módulos de apoyo y pruebas
│   ├── logistica_maestra.py
│   ├── chatbot_db_clips.py
│   └── prueba_variables.py
├── requirements.txt           # Dependencias (clipspy)
└── README.md                  # Documentación
```
---

## 🚦 Guía de Inicio Rápido

### 1. Requisitos previos
Es necesario instalar la librería que conecta Python con el motor CLIPS:
```bash
pip install -r requirements.txt
```

### 2. Inicializar el entorno (Datos)
El script de inicialización se encuentra en la carpeta `/data`. Este comando generará automáticamente el archivo `logistica.db` con la flota de vehículos y los pedidos pendientes necesarios para el motor de reglas.

```bash
# Ejecutar el script desde la raíz del proyecto
python data/crear_datos.py
```

```markdown
> [!WARNING]
> **Ubicación de la BD**: Ejecuta el script desde la raíz. El archivo `logistica.db` debe quedar en `data/logistica.db` para que las rutas de los scripts funcionen correctamente.
```

### 3. Ejecutar la optimización
Una vez generada la base de datos, lanza el orquestador principal. Este script leerá los pedidos pendientes de SQL, los procesará con el motor de inferencia CLIPS y guardará las decisiones de vuelta en la base de datos:

```bash
python src/main.py
```

---

## 🧠 Ejemplo de Lógica de Reglas (CLIPS)
El sistema utiliza razonamiento lógico para resolver conflictos de asignación mediante el motor de inferencia. Aquí puedes ver cómo se define una regla de negocio que prioriza envíos ligeros para vehículos rápidos:

```clips
(defrule asignar-urgente-moto
   (pedido (id ?id) (prioridad urgente) (peso-kg ?p&:(<= ?p 5)))
   (vehiculo (matricula ?mat) (tipo moto) (estado disponible))
   =>
   (assert (asignacion (id-pedido ?id) (matricula-vehiculo ?mat) (motivo "Envío ligero urgente")))
)
```

---

## 📄 Licencia y Autoría
Este proyecto ha sido desarrollado por **Jorge Herraiz Soler** como parte de la especialización en **IA y Big Data**.

> [!IMPORTANT]
> **Nota legal**: Queda prohibida la reproducción total o parcial para fines comerciales sin autorización expresa del autor.