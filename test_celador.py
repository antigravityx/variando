
import os
import json
import hashlib
from unittest.mock import patch
from componentes.modulo_seguridad import celador_de_llaves

def test_celador():
    archivo_boveda = "boveda_celador.json"
    if os.path.exists(archivo_boveda):
        os.remove(archivo_boveda)
    
    # Simular inicialización
    print("\n--- TEST: INICIALIZACIÓN DEL CELADOR ---")
    inputs_init = [
        "richon",           # Nombre del Director
        "richon,admin,root", # Nombres Reservados
        "clave1",           # Clave Maestra 1
        "clave2",           # Clave Maestra 2 (distinta)
        "0"                 # Salir del panel
    ]
    
    with patch('builtins.input', side_effect=inputs_init), \
         patch('componentes.modulo_seguridad.input_con_mascara', side_effect=["clave1", "clave2"]):
        celador_de_llaves()
    
    if os.path.exists(archivo_boveda):
        print("[V] Bóveda creada correctamente.")
        with open(archivo_boveda, 'r') as f:
            data = json.load(f)
            if data["director"] == "richon":
                print("[V] Datos de inicialización correctos.")
    
    # Simular acceso y creación de llave
    print("\n--- TEST: ACCESO Y CREACIÓN DE LLAVE ---")
    inputs_login = [
        "richon", # Usuario
        "2",      # Forjar Nueva Llave
        "Gmail",  # Alias
        "0"       # Salir
    ]
    # input_con_mascara se usa para las claves de login y para el secreto de la llave
    mascaras_login = ["clave1", "clave2", "secreto123"]
    
    with patch('builtins.input', side_effect=inputs_login), \
         patch('componentes.modulo_seguridad.input_con_mascara', side_effect=mascaras_login):
        celador_de_llaves()
    
    with open(archivo_boveda, 'r') as f:
        data = json.load(f)
        if len(data["llaves"]) > 0:
            print(f"[V] Llave '{data['llaves'][0]['alias']}' guardada correctamente.")

    # Limpieza final
    if os.path.exists(archivo_boveda):
        os.remove(archivo_boveda)

if __name__ == "__main__":
    test_celador()
