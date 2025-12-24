
from componentes.modulo_seguridad import _cifrar_verix, _descifrar_verix, LOGO_CAPSULA_B64
import os
import json
import base64
from datetime import datetime

def test_security():
    texto = "Mensaje Secreto de Prueba"
    clave = "Verix2025!"
    
    print(f"Texto original: {texto}")
    cifrado = _cifrar_verix(texto, clave)
    print(f"Texto cifrado (B64): {cifrado}")
    
    descifrado = _descifrar_verix(cifrado, clave)
    print(f"Texto descifrado: {descifrado}")
    
    if texto == descifrado:
        print("\n[V] TEST DE CIFRADO: EXITOSO")
    else:
        print("\n[X] TEST DE CIFRADO: FALLIDO")
        return

    # --- TEST DE CÁPSULAS VERIX ---
    print("\n--- TEST DE CÁPSULAS VERIX ---")
    boveda_dummy = {
        "director": "richon",
        "llaves": [{"alias": "Prueba", "secreto_cifrado": cifrado}]
    }
    clave_sellado = "ClaveSello999"
    id_nodo = "Test_Nodo"
    
    datos_json = json.dumps(boveda_dummy)
    datos_cifrados = _cifrar_verix(datos_json, clave_sellado)
    img_bytes = base64.b64decode(LOGO_CAPSULA_B64)
    
    nombre_capsula = f"Test_Capsula.png"
    print(f"Creando cápsula: {nombre_capsula}")
    
    with open(nombre_capsula, 'wb') as f:
        f.write(img_bytes)
        f.write(b'VERIX_CAPSULE_DATA')
        f.write(datos_cifrados.encode('utf-8'))
    
    print(f"Cápsula creada. Tamaño: {os.path.getsize(nombre_capsula)} bytes.")
    
    # --- TEST DE ABSORCIÓN ---
    print("Probando absorción...")
    with open(nombre_capsula, 'rb') as f:
        contenido = f.read()
    
    partes = contenido.split(b'VERIX_CAPSULE_DATA')
    if len(partes) == 2:
        datos_extraidos_cifrados = partes[1].decode('utf-8')
        datos_extraidos_json = _descifrar_verix(datos_extraidos_cifrados, clave_sellado)
        
        if datos_extraidos_json:
            boveda_extraida = json.loads(datos_extraidos_json)
            if boveda_extraida["director"] == "richon":
                print("[V] TEST DE CÁPSULA: EXITOSO (Datos recuperados íntegros)")
            else:
                print("[X] TEST DE CÁPSULA: FALLIDO (Datos corruptos)")
        else:
            print("[X] TEST DE CÁPSULA: FALLIDO (Error de descifrado)")
    else:
        print("[X] TEST DE CÁPSULA: FALLIDO (Marcador no encontrado)")

    # Limpieza
    if os.path.exists(nombre_capsula):
        os.remove(nombre_capsula)

if __name__ == "__main__":
    test_security()
