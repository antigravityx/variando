# componentes/modulo_integridad.py
import os
import hashlib
import json
import glob
import socket
import threading
from datetime import datetime

from .colores import Colors

MANIFEST_FILE = "manifiesto_integridad.json"
HONEYPOT_LOG_FILE = "honeypot_log.txt"

def _calcular_hash(filepath):
    """Calcula el hash SHA256 de un archivo."""
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            # Leer y actualizar el hash en bloques para no consumir mucha memoria
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except (IOError, PermissionError):
        return None

def generar_manifiesto(autorizado_por=None):
    """Escanea los archivos .py y crea un manifiesto con sus hashes y el token de la cadena de confianza."""
    print(f"\n{Colors.YELLOW}Generando nuevo manifiesto de integridad (Cadena de Confianza)...{Colors.ENDC}")
    
    # Cargar manifiesto anterior para obtener la firma previa
    firma_previa = "GENESIS"
    if os.path.exists(MANIFEST_FILE):
        try:
            with open(MANIFEST_FILE, 'r', encoding='utf-8') as f:
                old_manifest = json.load(f)
                firma_previa = old_manifest.get("firma_version", "GENESIS")
        except: pass

    manifesto = {
        "files": {},
        "metadata": {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "autorizado_por": autorizado_por or "Iniciación",
            "firma_previa": firma_previa
        }
    }
    
    # Escaneo de archivos
    files_to_check = glob.glob("*.py") + glob.glob(os.path.join("componentes", "*.py"))
    
    for filepath in files_to_check:
        file_hash = _calcular_hash(filepath)
        if file_hash:
            manifesto["files"][filepath] = file_hash
            print(f"  -> Firmando: {filepath} ({Colors.GREEN}OK{Colors.ENDC})")
        else:
            print(f"  -> Error al leer: {filepath} ({Colors.RED}FALLO{Colors.ENDC})")

    # Forjar el nuevo Token de Versión (Blockchain-style)
    # Token = Hash(Hashes_Archivos + Firma_Previa + Autoridad)
    data_to_sign = json.dumps(manifesto["files"], sort_keys=True) + firma_previa + (autorizado_por or "Iniciación")
    manifesto["firma_version"] = hashlib.sha256(data_to_sign.encode()).hexdigest()

    with open(MANIFEST_FILE, 'w', encoding='utf-8') as f:
        json.dump(manifesto, f, indent=4)
    
    print(f"\n{Colors.GREEN}[SUCCESS] Manifiesto de integridad guardado con firma: {manifesto['firma_version'][:16]}...{Colors.ENDC}")
    return f"Manifiesto generado. Versión: {manifesto['firma_version'][:8]}"

def verificar_integridad():
    """Verifica la integridad de los archivos contra el manifiesto."""
    print(f"{Colors.CYAN}Iniciando protocolo de verificación de integridad...{Colors.ENDC}")
    if not os.path.exists(MANIFEST_FILE):
        print(f"\n{Colors.RED}[ALERTA DE SEGURIDAD] No existe un manifiesto de integridad.{Colors.ENDC}")
        print("  No se puede verificar la pureza del código.")
        if input("  ¿Deseas generar el manifiesto inicial ahora? (s/n): ").lower() == 's':
            generar_manifiesto()
            return True # Permitir la ejecución después de la creación inicial
        return False

    with open(MANIFEST_FILE, 'r', encoding='utf-8') as f:
        manifesto_data = json.load(f)

    # Soporte para formato antiguo y nuevo
    if "files" in manifesto_data:
        manifesto = manifesto_data["files"]
    else:
        manifesto = manifesto_data

    comprometido = False
    for filepath, original_hash in manifesto.items():
        if not os.path.exists(filepath):
            print(f"  - {Colors.BOLD}{Colors.RED}[VIOLACIÓN] Archivo desaparecido:{Colors.ENDC} {filepath}")
            comprometido = True
            continue
        
        current_hash = _calcular_hash(filepath)
        if current_hash != original_hash:
            print(f"  - {Colors.BOLD}{Colors.RED}[VIOLACIÓN] El código de '{filepath}' ha sido alterado.{Colors.ENDC}")
            comprometido = True
        else:
            print(f"  - {Colors.GREEN}[OK]{Colors.ENDC} Verificado: {filepath}")

    if comprometido:
        print(f"\n{Colors.BOLD}{Colors.RED}¡ALERTA MÁXIMA! Se ha detectado una brecha de integridad. El sistema está comprometido.{Colors.ENDC}")
        print("  Se recomienda no ejecutar el programa y restaurar desde una copia segura.")
        
        # --- RUTA SEGURA: OVERRIDE DEL DIRECTOR ---
        print(f"\n{Colors.MAGENTA}{Colors.BOLD}--- ZONA DE RECUPERACIÓN ---{Colors.ENDC}")
        print("  Si los cambios son legítimos, el Director puede autorizar la actualización.")
        opcion = input(">> ¿Deseas iniciar el protocolo de autorización? (s/n): ").lower().strip()
        
        if opcion == 's':
            # Importación local para evitar dependencia circular
            from . import modulo_seguridad
            session = modulo_seguridad.verificar_credenciales_director()
            if session:
                print(f"\n{Colors.GREEN}[V] INTEGRACIÓN AUTORIZADA POR {session['nombre']}.{Colors.ENDC}")
                generar_manifiesto(autorizado_por=session['nombre'])
                print(f"{Colors.CYAN}El escudo de integridad ha sido actualizado. Reiniciando secuencia...{Colors.ENDC}")
                # Usar el nuevo reinicio fluido
                from .utilidades import ejecutar_reinicio_fluido
                ejecutar_reinicio_fluido()
                return True
            else:
                print(f"{Colors.RED}[!] AUTORIZACIÓN FALLIDA. El acceso sigue bloqueado.{Colors.ENDC}")

        return False
    
    print(f"\n{Colors.GREEN}[SUCCESS] Verificación de integridad completada. Todos los módulos son puros.{Colors.ENDC}")
    return True

def _honeypot_worker(port):
    """Función que corre en un hilo, escuchando en un puerto."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('0.0.0.0', port))
            s.listen()
            while True:
                conn, addr = s.accept()
                with conn:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    log_entry = f"[{timestamp}] Conexión sospechosa detectada al puerto {port} desde {addr[0]}"
                    print(f"\n{Colors.BOLD}{Colors.RED}¡ALERTA DE INTRUSIÓN!{Colors.ENDC} {log_entry}")
                    with open(HONEYPOT_LOG_FILE, "a", encoding="utf-8") as log_file:
                        log_file.write(log_entry + "\n")
    except Exception as e:
        error_msg = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] El Honeypot en el puerto {port} falló: {e}"
        print(f"\n{Colors.RED}{error_msg}{Colors.ENDC}")
        with open(HONEYPOT_LOG_FILE, "a", encoding="utf-8") as log_file:
            log_file.write(error_msg + "\n")

def iniciar_honeypot_simple():
    """Inicia un honeypot simple en un puerto especificado."""
    try:
        port = int(input(">> ¿En qué puerto quieres poner la carnada? (ej: 8081, 9000): ").strip())
        if not 1024 < port < 65535:
            print(f"{Colors.RED}[ERROR] Elige un puerto entre 1025 y 65534.{Colors.ENDC}")
            return "Honeypot no iniciado: puerto no válido."
        
        # Usamos un hilo para no bloquear el programa principal
        thread = threading.Thread(target=_honeypot_worker, args=(port,), daemon=True)
        thread.start()
        
        print(f"\n{Colors.GREEN}[VIGÍA ACTIVADO] El Honeypot está escuchando en el puerto {port}.{Colors.ENDC}")
        print(f"  Cualquier conexión será registrada en '{HONEYPOT_LOG_FILE}'.")
        return f"Honeypot activado en puerto {port}."
    except ValueError:
        print(f"{Colors.RED}[ERROR] Puerto no válido.{Colors.ENDC}")
        return "Honeypot no iniciado: entrada no válida."

def ver_log_honeypot():
    """Muestra el contenido del log del honeypot."""
    print(f"\n{Colors.CYAN}--- Registro de Intrusiones (Honeypot) ---{Colors.ENDC}")
    if not os.path.exists(HONEYPOT_LOG_FILE):
        print(f"{Colors.YELLOW}[INFO] El registro está limpio. Ninguna amenaza detectada.{Colors.ENDC}")
        return
    
    with open(HONEYPOT_LOG_FILE, 'r', encoding='utf-8') as f:
        print(f.read())

def menu_guardian():
    """Menú para las funciones de integridad y defensa."""
    log_output = "Acceso al Guardián del Orbe."
    while True:
        print(f"\n{Colors.RED}--- Guardián del Orbe (Defensa Activa) ---{Colors.ENDC}")
        print("  1. Generar / Actualizar Sello de Pureza (Manifiesto)")
        print("  2. Activar Vigía Silencioso (Honeypot)")
        print("  3. Ver Registro de Intrusiones")
        print("  0. Volver")
        
        choice = input(">> Orden: ").strip()

        if choice == '1':
            log_output += "\n  └─ " + generar_manifiesto()
        elif choice == '2':
            log_output += "\n  └─ " + iniciar_honeypot_simple()
        elif choice == '3':
            ver_log_honeypot()
        elif choice == '0':
            break
        else:
            print(f"{Colors.RED}[ERROR] Orden no reconocida.{Colors.ENDC}")
    return log_output