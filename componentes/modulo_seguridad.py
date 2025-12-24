# componentes/modulo_seguridad.py
import os
import json
import hashlib
import base64
from datetime import datetime
import random
import string
import uuid
import platform
import socket

from componentes.colores import Colors
from componentes.utilidades import input_con_mascara

# --- SISTEMA DE ALMA & AMISTAD (Stage 13) ---
MEMORIA_ALMA_PATH = "cronicas_director/memoria_alma.json"

def obtener_huella_digital():
    """Genera un hash único basado en el hardware del equipo."""
    try:
        identificador = f"{platform.node()}-{platform.processor()}-{uuid.getnode()}"
        return hashlib.sha256(identificador.encode()).hexdigest()
    except:
        return "huella_generica"

def inicializar_memoria_alma():
    """Asegura que exista la memoria del alma."""
    if not os.path.exists("cronicas_director"):
        os.makedirs("cronicas_director")
    if not os.path.exists(MEMORIA_ALMA_PATH):
        memoria = {
            "huellas_conocidas": {}, # huella: {trust_score, last_seen, name}
            "config_amistad": {
                "umbral_conocido": 5,  # Sesiones para Nivel 1
                "umbral_amigo": 15     # Sesiones para Nivel 2
            }
        }
        with open(MEMORIA_ALMA_PATH, 'w', encoding='utf-8') as f:
            json.dump(memoria, f, indent=4)

def actualizar_vínculo_amistad(nombre, huella):
    """Incrementa el nivel de amistad tras un login exitoso."""
    inicializar_memoria_alma()
    try:
        with open(MEMORIA_ALMA_PATH, 'r+', encoding='utf-8') as f:
            memoria = json.load(f)
            if huella not in memoria["huellas_conocidas"]:
                memoria["huellas_conocidas"][huella] = {
                    "nombre": nombre,
                    "trust_score": 1,
                    "last_seen": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            else:
                memoria["huellas_conocidas"][huella]["trust_score"] += 1
                memoria["huellas_conocidas"][huella]["last_seen"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            f.seek(0)
            json.dump(memoria, f, indent=4)
            f.truncate()
    except Exception as e:
        print(f"{Colors.RED}[!] Fallo en Memoria del Alma: {e}{Colors.ENDC}")

def obtener_nivel_amistad(huella):
    """Retorna el nivel de confianza (0, 1, 2)."""
    if not os.path.exists(MEMORIA_ALMA_PATH): return 0
    try:
        with open(MEMORIA_ALMA_PATH, 'r', encoding='utf-8') as f:
            memoria = json.load(f)
            data = memoria["huellas_conocidas"].get(huella)
            if not data: return 0
            
            score = data["trust_score"]
            umbral_amigo = memoria["config_amistad"]["umbral_amigo"]
            umbral_conocido = memoria["config_amistad"]["umbral_conocido"]
            
            if score >= umbral_amigo: return 2
            if score >= umbral_conocido: return 1
            return 0
    except: return 0

# Imagen base para las cápsulas (Un pequeño candado digital en Base64)
LOGO_CAPSULA_B64 = """
iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMA
AAsTAAALEwEAmpwYAAAAB3RJTUUH5QwUFB4z2i0qWwAAAB1pVFh0Q29tbWVudAAAAAAAQ3JlYXRlZCB3
aXRoIEdJTVBkLmUHAAABsklEQVRYw+2Wv0vDQBTHP29S61+g4qCi4iCCi4u4iIu04iIIdvEviIuL4CQI
LuIguImDi4uIi4uIi4uDi4uIi9g6VEO+5yV3V5cW2uQeD/fu7n3f997dveQB/1hF+81gK61XN6lW0j5N
6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0
j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6
Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3j
pF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F
+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zip
V9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+
TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupV
tI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+T
ehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt
46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46Re
Rfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4
qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfR
Pk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7q
VbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSP
k3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV
7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOk
XkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7
OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX
0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O
6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0
j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6
Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3j
pF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F
+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zip
V9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+
TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupV
tI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+T
ehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt
46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46Re
Rfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4
qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfR
Pk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7q
VbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSP
k3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV
7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOk
XkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7
OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX
0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O
6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0
j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6
Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3j
pF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F
+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zip
V9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+
TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupV
tI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+T
ehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt
46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46Re
Rfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4
qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfR
Pk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7q
VbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSP
k3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV
7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOk
XkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7
OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX
0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O
6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0
j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6
Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3j
pF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F
+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zip
V9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+
TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupV
tI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+T
ehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt
46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46Re
Rfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4
qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfR
Pk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7q
VbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSP
k3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV
7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOk
XkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7
OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX
0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O
6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0
j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6
Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3j
pF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F
+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zip
V9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+
TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupV
tI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+T
ehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt
46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46Re
Rfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4
qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfR
Pk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7q
VbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSP
k3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV
7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOk
XkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7
OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX
0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O
6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0
j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6
Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3j
pF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F
+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zip
V9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+
TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupV
tI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+T
ehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt
46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46Re
Rfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4
qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfR
Pk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7q
VbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSP
k3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV
7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOk
XkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7
OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX
0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O
6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0
j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6
Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3j
pF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F
+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zip
V9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+
TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupV
tI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+T
ehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt
46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46Re
Rfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4
qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfR
Pk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7q
VbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSP
k3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV
7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOk
XkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7
OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX
0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O
6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0
j5N6Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6
Fe3jpF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3j
pF5F+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F
+zipV9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zip
V9E+TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+
TupVtI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupV
tI+TehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+T
ehXt46ReRfs4qVfRPk7qVbSPk3oV7eOkXkX7OKlX0T5O6lW0j5N6Fe3jpF5F+zipV9E+TupVtI+T
"""

def _cifrar_verix(texto, clave):
    """Cifrado XOR + Base64 para transporte seguro."""
    try:
        cifrado = ''.join(chr(ord(c) ^ ord(k)) for c, k in zip(texto, clave * (len(texto) // len(clave) + 1)))
        return base64.b64encode(cifrado.encode('utf-8')).decode('utf-8')
    except Exception:
        return ""

def _descifrar_verix(texto_b64, clave):
    """Descifrado XOR + Base64."""
    try:
        cifrado = base64.b64decode(texto_b64).decode('utf-8')
        return ''.join(chr(ord(c) ^ ord(k)) for c, k in zip(cifrado, clave * (len(cifrado) // len(clave) + 1)))
    except Exception:
        return None

def desafio_captcha():
    """Genera un desafío visual (Sopa de Letras) para verificar humanidad."""
    chars = string.ascii_uppercase + string.digits
    token = ''.join(random.choices(chars, k=6))
    display = " ".join(list(token))
    print(f"\n{Colors.CYAN}--- FACTOR 3: PROTECCIÓN ANTI-BOT ---{Colors.ENDC}")
    print(f"Sopa de Letras: {Colors.BOLD}{Colors.RED}[ {display} ]{Colors.ENDC}")
    attempt = input(">> Transcribe los caracteres juntos: ").strip().upper()
    return attempt == token

def _generar_variantes_inteligentes(texto):
    """Genera variantes de estilo leet y combinaciones comunes."""
    variantes = set()
    base = texto.lower()
    variantes.add(base)
    variantes.add(base.upper())
    variantes.add(base.capitalize())
    leet1 = base.translate(str.maketrans("aeiost", "431057"))
    variantes.add(leet1)
    variantes.add(leet1.upper())
    variantes.add(f"xX_{base}_Xx")
    variantes.add(f"_{base}_")
    variantes.add(f"{base}123")
    variantes.add(f"admin_{base}")
    variantes.add(f"@{base}")
    variantes.add(f"#{base}")
    variantes.add(f".{base}")
    variantes.add(f"{base}!")
    variantes.add(f"{base}2025")
    variantes.add(f"root_{base}")
    return sorted(list(variantes))

def _inicializar_celador():
    """Realiza la ceremonia de iniciación del Celador (Configuración inicial)."""
    archivo_boveda = "boveda_celador.json"
    print(f"\n{Colors.YELLOW}[CEREMONIA DE INICIACIÓN - EL DESPERTAR DEL CELADOR]{Colors.ENDC}")
    print("El Celador requiere configurar la seguridad de la LISTA ROJA.")
    print("Esta configuración protegerá tu identidad bajo múltiples rostros.")
    
    director = input(">> Nombre Principal del Director: ").strip()
    if not director: 
        print(f"{Colors.RED}Cancelado.{Colors.ENDC}")
        return None
        
    print(">> Introduce tus Nombres Reservados (Lista Roja - separados por coma).")
    print("   Cualquiera de estos nombres te otorgará acceso de Director.")
    reserved_input = input("   (ej: richon, admin, orbe, maestro): ").strip()
    reserved_names = [n.strip() for n in reserved_input.split(',') if n.strip()]
    
    # Normalización: todos en minúsculas para comparaciones robustas
    reserved_names = list(set([n.lower() for n in reserved_names] + [director.lower()]))
        
    print(f"\n{Colors.CYAN}--- CONFIGURACIÓN DE LLAVES MAESTRAS ---{Colors.ENDC}")
    print("Establece las dos llaves de poder. Cualquiera servirá para entrar.")
    k1 = input_con_mascara(">> Introduce la PRIMERA Clave Maestra: ").strip()
    k2 = input_con_mascara(">> Introduce la SEGUNDA Clave Maestra: ").strip()
    
    if not k1 or not k2:
        print(f"{Colors.RED}Las llaves no pueden estar vacías.{Colors.ENDC}")
        return None
    if k1 == k2:
        print(f"{Colors.RED}¡ALERTA! Las llaves deben ser distintas para mayor seguridad.{Colors.ENDC}")
        return None
        
    boveda = {
        "director": director,
        "reserved_names": reserved_names,
        "hash_key1": hashlib.sha256(k1.encode()).hexdigest(),
        "hash_key2": hashlib.sha256(k2.encode()).hexdigest(),
        "factor3_users": [],
        "usuarios_adicionales": [] 
    }
    
    with open(archivo_boveda, 'w', encoding='utf-8') as f:
        json.dump(boveda, f, indent=4)
        
    print(f"{Colors.GREEN}[JURAMENTO] El Celador ha despertado. Tu identidad está protegida.{Colors.ENDC}")
    return boveda

def reset_boveda():
    """Elimina la bóveda actual para permitir una nueva inicialización."""
    archivo_boveda = "boveda_celador.json"
    if os.path.exists(archivo_boveda):
        # Crear backup antes de borrar por seguridad
        shutil = __import__('shutil')
        shutil.copy(archivo_boveda, archivo_boveda + ".bak")
        os.remove(archivo_boveda)
        print(f"{Colors.YELLOW}[SISTEMA] Bóveda antigua eliminada (Backup creado como .bak).{Colors.ENDC}")
    return True

def verificar_credenciales_director(nombre_previo=None):
    """Verifica las credenciales del Director para operaciones críticas (Override)."""
    archivo_boveda = "boveda_celador.json"
    boveda = {}
    
    if not os.path.exists(archivo_boveda):
        print(f"\n{Colors.YELLOW}[BOOTSTRAP] El Celador no ha sido inicializado.{Colors.ENDC}")
        print("Para autorizar cambios como Director, debes establecer tus llaves maestras.")
        if input(">> ¿Deseas inicializar el Celador ahora? (s/n): ").lower() == 's':
            boveda = _inicializar_celador()
            if not boveda: return None
            return {"nombre": boveda.get("director", "Richon"), "nivel": 0}
        return None

    try:
        with open(archivo_boveda, 'r', encoding='utf-8') as f:
            boveda = json.load(f)
    except Exception:
        print(f"{Colors.RED}[ERROR] La bóveda está corrupta.{Colors.ENDC}")
        return None

    if "hash_key1" not in boveda or "hash_key2" not in boveda:
        boveda = _inicializar_celador()
        if not boveda: return None
        return {"nombre": boveda.get("director", "Richon"), "nivel": 0}

    print(f"\n{Colors.CYAN}--- PROTOCOLO DE AUTORIZACIÓN: NIVEL DIRECTOR ---{Colors.ENDC}")
    
    # Si no viene de login_sistema, pedimos identidad para "despertar" el protocolo
    identidad_usada = nombre_previo
    if not identidad_usada:
        identidad_usada = input(">> Confirmar Identidad (Nombre de la Lista Roja): ").strip()
        
    nombres_legitimos = [n.lower() for n in boveda.get("reserved_names", [])]
    if boveda.get("director"): nombres_legitimos.append(boveda["director"].lower())
    
    if identidad_usada.lower() not in nombres_legitimos:
        print(f"{Colors.RED}[!] Identidad no reconocida en la Lista Roja.{Colors.ENDC}")
        return None

    if not nombre_previo:
        print(f"Identidad Detectada: {Colors.BOLD}{Colors.YELLOW}{identidad_usada}{Colors.ENDC}")
    else:
        print(f"Identidad Protegida: {Colors.BOLD}{Colors.YELLOW}{identidad_usada}{Colors.ENDC}")
    
    huella = obtener_huella_digital()
    nivel_amistad = obtener_nivel_amistad(huella)
    
    if nivel_amistad == 2:
        print(f"{Colors.GREEN}[VÍNCULO DE AMISTAD] El Cerebro reconoce tu esencia. No se requieren llaves.{Colors.ENDC}")
        actualizar_vínculo_amistad(identidad_usada, huella)
        registrar_remembranza(identidad_usada, huella, "ACCESO_DIRECTO_AMIGO")
        return {"nombre": identidad_usada, "nivel": 0}

    # Soporte para cualquiera de las llaves maestras (Simplificación a petición del Director)
    if nivel_amistad == 1:
        print(f"{Colors.YELLOW}[MEMORIA] Eres un usuario conocido. Se requiere validación simple.{Colors.ENDC}")
    
    p = input_con_mascara(">> Introduce una de tus Claves Maestras: ").strip()
    h = hashlib.sha256(p.encode()).hexdigest()
    
    if h == boveda.get("hash_key1") or h == boveda.get("hash_key2"):
        print(f"{Colors.GREEN}[V] Identidad y Llave confirmadas. Acceso concedido.{Colors.ENDC}")
        actualizar_vínculo_amistad(identidad_usada, huella)
        registrar_remembranza(identidad_usada, huella, "LOGUEO_EXITOSO")
    else:
        print(f"{Colors.RED}[!] Clave incorrecta. El protocolo se aborta.{Colors.ENDC}")
        # Registro de Remembranza (Intento fallido)
        registrar_remembranza(identidad_usada, huella, "FALLO_CLAVE")
        
        print(f"\n{Colors.YELLOW}[SISTEMA] Si has olvidado tus llaves, el Director puede forzarlas.")
        if input(">> ¿Deseas RESETEAR la bóveda e iniciar una nueva ceremonia? (s/n): ").lower() == 's':
            reset_boveda()
            print(f"{Colors.CYAN}Bóveda reseteada. Reinicia el programa para configurar nuevas llaves.{Colors.ENDC}")
        return None

    if identidad_usada.lower() in [n.lower() for n in boveda.get("factor3_users", [])]:
        print(f"{Colors.YELLOW}[FACTOR 3] Verificación anti-bot requerida.{Colors.ENDC}")
        if not desafio_captcha():
            print(f"{Colors.RED}Acceso Denegado: Fallo en desafío visual.{Colors.ENDC}")
            return None
            
    # Devolvemos el nombre usado para la sesión para mayor personalización
    return {"nombre": identidad_usada, "nivel": 0}

def registrar_remembranza(nombre, huella, evento):
    """Registra eventos de seguridad o intentos de acceso."""
    log_path = "cronicas_director/remembranzas.json"
    if not os.path.exists("cronicas_director"): os.makedirs("cronicas_director")
    
    entrada = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "identidad": nombre,
        "huella": huella,
        "evento": evento,
        "os": platform.system(),
        "ip_local": socket.gethostbyname(socket.gethostname()) if hasattr(socket, 'gethostbyname') else "unknown"
    }
    
    try:
        datos = []
        if os.path.exists(log_path):
            with open(log_path, 'r', encoding='utf-8') as f:
                datos = json.load(f)
        datos.append(entrada)
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump(datos, f, indent=4)
    except: pass

def login_sistema():
    """Punto de entrada de logueo. Identifica si es el Director o personal."""
    archivo_boveda = "boveda_celador.json"
    if not os.path.exists(archivo_boveda):
        # Si no existe, forzamos inicialización (Solo Director puede)
        print(f"\n{Colors.YELLOW}[BOOTSTRAP] El Celador no ha sido inicializado.{Colors.ENDC}")
        print("Para acceder, el Director debe establecer sus llaves maestras.")
        if input(">> ¿Deseas inicializar el Celador ahora? (s/n): ").lower() == 's':
            return verificar_credenciales_director() # Esto inicializa y devuelve el rol del director
        return None

    print(f"\n{Colors.CYAN}--- ACCESO AL SISTEMA ---{Colors.ENDC}")
    identidad = input(">> Identidad / Nombre: ").strip()
    
    with open(archivo_boveda, 'r', encoding='utf-8') as f:
        boveda = json.load(f)

    # Caso 1: Es el Director (Nombre principal o variantes reservadas)
    director_name = boveda.get("director", "").lower()
    nombres_reservados = [n.lower() for n in boveda.get("reserved_names", [])]
    
    if identidad.lower() == director_name or identidad.lower() in nombres_reservados:
        return verificar_credenciales_director(nombre_previo=identidad)

    # Caso 2: Es personal adicional
    usuarios = boveda.get("usuarios_adicionales", [])
    for user in usuarios:
        if user["nombre"].lower() == identidad.lower():
            pin = input_con_mascara(f">> Introduce PIN para {user['nombre']}: ").strip()
            if hashlib.sha256(pin.encode()).hexdigest() == user["pin_hash"]:
                print(f"{Colors.GREEN}[ACCESO CONCEDIDO] Bienvenido, {user['nombre']}.{Colors.ENDC}")
                return user
            else:
                print(f"{Colors.RED}[ERROR] PIN incorrecto.{Colors.ENDC}")
                return None

    print(f"{Colors.YELLOW}[AVISO] Identidad no reconocida. Acceso denegado.{Colors.ENDC}")
    return None

def celador_de_llaves():
    """Gestor de contraseñas y secretos (El Celador)."""
    log_output = "Acceso al Celador de Llaves."
    archivo_boveda = "boveda_celador.json"
    boveda = {}
    if os.path.exists(archivo_boveda):
        try:
            with open(archivo_boveda, 'r', encoding='utf-8') as f:
                boveda = json.load(f)
        except:
            print(f"{Colors.RED}[ALERTA] La bóveda está corrupta o vacía.{Colors.ENDC}")
            boveda = {}
    if "factor3_users" not in boveda:
        boveda["factor3_users"] = []
    master_key_session = ""
    if "hash_key1" not in boveda or "hash_key2" not in boveda:
        boveda = _inicializar_celador()
        if not boveda: return "Cancelado."
        # Extraer claves de sesión si es necesario, pero _inicializar_celador no las devuelve en plano.
        # En una inicialización, pedimos entrar de nuevo o simplemente fallamos por seguridad.
        return "Celador inicializado. Por favor, reingresa para operar."
    else:
        print(f"\n{Colors.CYAN}El Celador vigila la puerta. Identifícate.{Colors.ENDC}")
        user_input = input(">> Usuario: ").strip()
        if user_input not in boveda.get("reserved_names", []):
            print(f"{Colors.YELLOW}[ALERTA] Usuario '{user_input}' no está en la lista de nombres reservados.{Colors.ENDC}")
        p1_input = input_con_mascara(">> Introduce la PRIMERA Clave: ").strip()
        p2_input = input_con_mascara(">> Introduce la SEGUNDA Clave: ").strip()
        h1_input = hashlib.sha256(p1_input.encode()).hexdigest()
        h2_input = hashlib.sha256(p2_input.encode()).hexdigest()
        if h1_input == boveda["hash_key1"] and h2_input == boveda["hash_key2"]:
            if user_input in boveda.get("factor3_users", []):
                print(f"\n{Colors.YELLOW}[ALERTA DE SEGURIDAD] Este usuario requiere Verificación de Factor 3.{Colors.ENDC}")
                if not desafio_captcha():
                    print(f"\n{Colors.BOLD}{Colors.RED}¡FALLO DE VERIFICACIÓN HUMANA! ACCESO DENEGADO.{Colors.ENDC}")
                    return "ALERTA: Fallo en Factor 3 (Posible Bot)."
            print(f"\n{Colors.GREEN}Credenciales Verificadas. Bienvenido, {user_input}.{Colors.ENDC}")
            master_key_session = p1_input + p2_input
        else:
            print(f"\n{Colors.BOLD}{Colors.RED}¡ACCESO DENEGADO! Las llaves no coinciden.{Colors.ENDC}")
            print(f"{Colors.RED}El Celador ha bloqueado el acceso.{Colors.ENDC}")
            return "ALERTA DE SEGURIDAD: Intento de acceso fallido."
    while True:
        print(f"\n{Colors.MAGENTA}--- Panel de Control del Celador ---{Colors.ENDC}")
        print(f"  1. {Colors.BOLD}Pasar Revista{Colors.ENDC} (Listar Llaves Públicas)")
        print(f"  2. {Colors.BOLD}Forjar Nueva Llave{Colors.ENDC} (Guardar Secreto)")
        print(f"  3. {Colors.BOLD}Solicitar Acceso{Colors.ENDC} (Revelar Secreto Privado)")
        print(f"  4. {Colors.BOLD}Ejecutar Llave{Colors.ENDC} (Eliminar)")
        print(f"  5. {Colors.BOLD}Generador de Variantes{Colors.ENDC} (Protección Expandida)")
        print(f"  6. {Colors.BOLD}Gestionar Lista Roja{Colors.ENDC} (Administrar Reservados)")
        print(f"  7. {Colors.BOLD}Cápsulas Verix{Colors.ENDC} (Exportar/Importar Bóveda)")
        print(f"  {Colors.YELLOW}0. Cerrar Bóveda y Salir{Colors.ENDC}")
        choice = input("\n>> Orden del Amo: ").strip()
        if choice == '1':
            llaves = boveda.get("llaves", [])
            if not llaves:
                print(f"{Colors.YELLOW}La bóveda está vacía, Amo.{Colors.ENDC}")
            else:
                print(f"\n{Colors.CYAN}--- Inventario de Llaves ---{Colors.ENDC}")
                print(f"{'ID':<4}{'Alias / Nombre':<30}{'Firma (Integridad)'}")
                print("-" * 70)
                for i, k in enumerate(llaves):
                    firma_corta = k.get('firma', 'N/A')[:15] + "..."
                    print(f"{i+1:<4}{k['alias']:<30}{Colors.GREEN}{firma_corta}{Colors.ENDC}")
            input("\n--- Enter para continuar ---")
        elif choice == '2':
            print(f"\n{Colors.YELLOW}--- Forja de Llaves ---{Colors.ENDC}")
            alias = input(">> Nombre de la Llave (ej: Gmail, Banco, Wifi): ").strip()
            secreto = input_con_mascara(">> El Secreto (Contraseña/Token): ").strip()
            if alias and secreto:
                secreto_cifrado = _cifrar_verix(secreto, master_key_session)
                firma = hashlib.sha256((alias + secreto).encode()).hexdigest()
                nueva_llave = {"alias": alias, "secreto_cifrado": secreto_cifrado, "firma": firma, "fecha": datetime.now().strftime("%Y-%m-%d %H:%M")}
                boveda["llaves"].append(nueva_llave)
                with open(archivo_boveda, 'w', encoding='utf-8') as f:
                    json.dump(boveda, f, indent=4)
                print(f"{Colors.GREEN}[ÉXITO] La llave '{alias}' ha sido forjada y custodiada.{Colors.ENDC}")
            else:
                print(f"{Colors.RED}No se puede forjar la nada.{Colors.ENDC}")
        elif choice == '3':
            try:
                idx = int(input(">> ID de la llave a revelar: ").strip()) - 1
                if 0 <= idx < len(boveda.get("llaves", [])):
                    k = boveda["llaves"][idx]
                    secreto_revelado = _descifrar_verix(k['secreto_cifrado'], master_key_session)
                    if secreto_revelado is None:
                        print(f"{Colors.RED}[ERROR] La llave está corrupta o la clave de sesión es incorrecta.{Colors.ENDC}")
                        continue
                    firma_check = hashlib.sha256((k['alias'] + secreto_revelado).encode()).hexdigest()
                    estado_integridad = f"{Colors.GREEN}VERIFICADA{Colors.ENDC}" if firma_check == k['firma'] else f"{Colors.RED}CORRUPTA{Colors.ENDC}"
                    print(f"\n{Colors.BOLD}--- DETALLES DE LA LLAVE ---{Colors.ENDC}")
                    print(f"  Alias:      {k['alias']}")
                    print(f"  Integridad: {estado_integridad}")
                    print(f"  {Colors.YELLOW}SECRETO:{Colors.ENDC}    {Colors.BOLD}{Colors.CYAN}{secreto_revelado}{Colors.ENDC}")
                    input("\n--- Presiona Enter para ocultar el secreto ---")
                    os.system('cls' if os.name == 'nt' else 'clear')
                else:
                    print(f"{Colors.RED}Esa llave no existe.{Colors.ENDC}")
            except ValueError:
                print(f"{Colors.RED}Entrada inválida.{Colors.ENDC}")
        elif choice == '4':
            try:
                idx = int(input(">> ID de la llave a EJECUTAR (Borrar): ").strip()) - 1
                if 0 <= idx < len(boveda.get("llaves", [])):
                    target = boveda["llaves"][idx]
                    confirm = input(f"{Colors.RED}¿Ordenas la destrucción de la llave '{target['alias']}'? (s/n): {Colors.ENDC}").lower()
                    if confirm == 's':
                        boveda["llaves"].pop(idx)
                        with open(archivo_boveda, 'w', encoding='utf-8') as f:
                            json.dump(boveda, f, indent=4)
                        print(f"{Colors.YELLOW}La llave ha sido destruida.{Colors.ENDC}")
                else:
                    print(f"{Colors.RED}Llave no encontrada.{Colors.ENDC}")
            except ValueError:
                print(f"{Colors.RED}Entrada inválida.{Colors.ENDC}")
        elif choice == '5':
            print(f"\n{Colors.MAGENTA}--- Generador de Variantes de Protección ---{Colors.ENDC}")
            palabra = input(">> Introduce palabra o usuario a proteger: ").strip()
            if palabra:
                variantes = _generar_variantes_inteligentes(palabra)
                print(f"\n{Colors.CYAN}Variantes detectadas:{Colors.ENDC}")
                for v in variantes:
                    estado = " [ACTIVA]" if v in boveda.get("reserved_names", []) else ""
                    print(f"  - {v}{Colors.GREEN}{estado}{Colors.ENDC}")
                print(f"\n{Colors.BOLD}Opciones:{Colors.ENDC}")
                print("  1. Exportar lista a archivo (.txt)")
                print("  2. ACTIVAR protección (Agregar a Lista Roja)")
                print("  3. Archivar en Banco de Reservas (Inactivo)")
                print("  0. Volver")
                sub_choice = input(">> Acción: ").strip()
                if sub_choice == '1':
                    fname = f"variantes_{palabra}.txt"
                    with open(fname, 'w', encoding='utf-8') as f: f.write("\n".join(variantes))
                    print(f"{Colors.GREEN}[ÉXITO] Lista exportada a '{fname}'.{Colors.ENDC}")
                elif sub_choice == '2':
                    nuevos = sum(1 for v in variantes if v not in boveda["reserved_names"])
                    boveda["reserved_names"].extend([v for v in variantes if v not in boveda["reserved_names"]])
                    with open(archivo_boveda, 'w', encoding='utf-8') as f: json.dump(boveda, f, indent=4)
                    print(f"{Colors.GREEN}[ÉXITO] Se han blindado {nuevos} nuevas variantes en la Lista Roja.{Colors.ENDC}")
                elif sub_choice == '3':
                    if "banco_reservas" not in boveda: boveda["banco_reservas"] = []
                    count = sum(1 for v in variantes if v not in boveda["banco_reservas"] and v not in boveda["reserved_names"])
                    boveda["banco_reservas"].extend([v for v in variantes if v not in boveda["banco_reservas"] and v not in boveda["reserved_names"]])
                    with open(archivo_boveda, 'w', encoding='utf-8') as f: json.dump(boveda, f, indent=4)
                    print(f"{Colors.GREEN}[ÉXITO] {count} variantes archivadas en el Banco de Reservas.{Colors.ENDC}")
        elif choice == '6':
            print(f"\n{Colors.RED}--- GESTIÓN DE LISTA ROJA (NOMBRES RESERVADOS) ---{Colors.ENDC}")
            print(f"Nombres protegidos: {len(boveda.get('reserved_names', []))}")
            print("  1. Administrar Nombres por ID (Activar/Factor 3/Banco)")
            print("  2. Agregar nuevo nombre manualmente")
            print("  0. Volver")
            sub = input(">> Acción: ").strip()
            if sub == '1':
                sorted_reserved = sorted(boveda.get("reserved_names", []))
                print(f"\n{Colors.CYAN}--- Directorio de Usuarios Reservados ---{Colors.ENDC}")
                for i, n in enumerate(sorted_reserved):
                    tags = []
                    if n in boveda.get("factor3_users", []): tags.append(f"{Colors.RED}[F3-AntiBot]{Colors.ENDC}")
                    if n == boveda.get("director"): tags.append(f"{Colors.YELLOW}[DIRECTOR]{Colors.ENDC}")
                    print(f"  {Colors.BOLD}{i+1}.{Colors.ENDC} {n:<20} {' '.join(tags)}")
                try:
                    sel_idx = int(input("\n>> Selecciona ID para administrar (0 volver): ").strip()) - 1
                    if 0 <= sel_idx < len(sorted_reserved):
                        target_name = sorted_reserved[sel_idx]
                        print(f"\n{Colors.MAGENTA}Administrando: '{target_name}'{Colors.ENDC}")
                        print("  1. Activar/Desactivar Factor 3 (Sopa de Letras)")
                        print("  2. Mover al Banco de Reservas (Desactivar)")
                        act = input(">> Acción: ").strip()
                        if act == '1':
                            if target_name in boveda["factor3_users"]:
                                boveda["factor3_users"].remove(target_name)
                                print(f"{Colors.YELLOW}Factor 3 DESACTIVADO para '{target_name}'.{Colors.ENDC}")
                            else:
                                boveda["factor3_users"].append(target_name)
                                print(f"{Colors.GREEN}Factor 3 ACTIVADO para '{target_name}'.{Colors.ENDC}")
                        elif act == '2':
                            if target_name == boveda.get("director"):
                                print(f"{Colors.RED}El Director no puede ir al banco.{Colors.ENDC}")
                            else:
                                boveda["reserved_names"].remove(target_name)
                                if "banco_reservas" not in boveda: boveda["banco_reservas"] = []
                                boveda["banco_reservas"].append(target_name)
                                print(f"{Colors.YELLOW}'{target_name}' movido al Banco de Reservas.{Colors.ENDC}")
                        with open(archivo_boveda, 'w', encoding='utf-8') as f: json.dump(boveda, f, indent=4)
                except ValueError: pass
            elif sub == '2':
                nuevo = input(">> Nuevo nombre a proteger: ").strip()
                if nuevo:
                    print(f"\n{Colors.MAGENTA}¿Generar variantes automáticas para '{nuevo}'?{Colors.ENDC}")
                    print("  [s]í: Agregar variantes (leet, símbolos, etc.)")
                    print("  [n]o: Solo la palabra exacta")
                    op_var = input(">> Elección (s/n): ").lower().strip()
                    lista_a_agregar = [nuevo]
                    if op_var == 's':
                        posibles = _generar_variantes_inteligentes(nuevo)
                        nuevas = [p for p in posibles if p not in boveda.get("reserved_names", []) and p != nuevo]
                        if nuevas:
                            print(f"\n{Colors.CYAN}Variantes sugeridas ({len(nuevas)}):{Colors.ENDC}")
                            for v in nuevas: print(f"  - {v}")
                            if input("\n>> ¿Guardar estas variantes en la Lista Roja? (s/n): ").lower().strip() == 's':
                                lista_a_agregar.extend(nuevas)
                        else:
                            print(f"{Colors.YELLOW}[INFO] Las variantes ya estaban protegidas.{Colors.ENDC}")
                    agregados = sum(1 for n in lista_a_agregar if n not in boveda.get("reserved_names", []))
                    if agregados > 0:
                        boveda["reserved_names"].extend([n for n in lista_a_agregar if n not in boveda.get("reserved_names", [])])
                        with open(archivo_boveda, 'w', encoding='utf-8') as f: json.dump(boveda, f, indent=4)
                        print(f"{Colors.GREEN}[ÉXITO] Se han blindado {agregados} nombres en la Lista Roja.{Colors.ENDC}")
                    else:
                        print(f"{Colors.YELLOW}Los nombres ya estaban protegidos.{Colors.ENDC}")
        elif choice == '7':
            print(f"\n{Colors.CYAN}--- GESTOR DE CÁPSULAS VERIX ---{Colors.ENDC}")
            print("  1. Crear Cápsula (Exportar Bóveda a Imagen)")
            print("  2. Absorber Cápsula (Importar Bóveda desde Imagen)")
            op_capsula = input(">> Acción: ").strip()
            if op_capsula == '1':
                print(f"\n{Colors.YELLOW}--- SELLADO DE CÁPSULA ---{Colors.ENDC}")
                print("La cápsula contendrá una copia de seguridad de la bóveda actual.")
                id_nodo = input(">> Identidad del Nodo/Cliente (ej: Kiosco_Centro): ").strip()
                clave_sellado = input_con_mascara(">> Clave de Sellado (para esta cápsula): ").strip()
                if not clave_sellado or not id_nodo:
                    print(f"{Colors.RED}Se requiere ID y Clave de Sellado.{Colors.ENDC}")
                    continue
                boveda['id_nodo'] = id_nodo
                datos_json = json.dumps(boveda)
                datos_cifrados = _cifrar_verix(datos_json, clave_sellado)
                img_bytes = base64.b64decode(LOGO_CAPSULA_B64)
                nombre_capsula = f"Capsula_{id_nodo}_{datetime.now().strftime('%Y%m%d')}.png"
                with open(nombre_capsula, 'wb') as f:
                    f.write(img_bytes)
                    f.write(b'VERIX_CAPSULE_DATA')
                    f.write(datos_cifrados.encode('utf-8'))
                print(f"{Colors.GREEN}[ÉXITO] Cápsula '{nombre_capsula}' creada y sellada.{Colors.ENDC}")
            elif op_capsula == '2':
                print(f"\n{Colors.RED}--- ABSORCIÓN DE CÁPSULA ---{Colors.ENDC}")
                print("ADVERTENCIA: Esto SOBRESCRIBIRÁ la bóveda actual.")
                if input("¿Continuar? (s/n): ").lower() != 's': continue
                path_capsula = input(">> Ruta del archivo de la Cápsula (.png): ").strip().replace('"', '')
                clave_sellado = input_con_mascara(">> Clave de Sellado de la cápsula: ").strip()
                try:
                    with open(path_capsula, 'rb') as f:
                        contenido = f.read()
                    partes = contenido.split(b'VERIX_CAPSULE_DATA')
                    if len(partes) != 2: raise ValueError("Formato de cápsula inválido.")
                    datos_cifrados = partes[1].decode('utf-8')
                    datos_json = _descifrar_verix(datos_cifrados, clave_sellado)
                    if datos_json is None:
                        print(f"{Colors.RED}[ERROR] Clave de Sellado incorrecta o cápsula corrupta.{Colors.ENDC}")
                        continue
                    nueva_boveda = json.loads(datos_json)
                    with open(archivo_boveda, 'w', encoding='utf-8') as f:
                        json.dump(nueva_boveda, f, indent=4)
                    print(f"{Colors.GREEN}[ÉXITO] Bóveda absorbida desde la cápsula '{os.path.basename(path_capsula)}'.{Colors.ENDC}")
                    print("Es necesario reiniciar el Celador para aplicar los cambios.")
                    return log_output
                except Exception as e:
                    print(f"{Colors.RED}[ERROR] No se pudo absorber la cápsula: {e}{Colors.ENDC}")
        elif choice == '0':
            print(f"{Colors.CYAN}Cerrando la bóveda. El Celador permanece vigilante.{Colors.ENDC}")
            break
    return log_output