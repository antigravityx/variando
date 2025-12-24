# componentes/modulo_admin.py
import os
import json
import shutil
import hashlib
from datetime import datetime
from .colores import Colors
from .utilidades import input_con_mascara

BASE_DIR = "cronicas_director"
BACKUP_DIR = os.path.join(BASE_DIR, "backups")
LOG_FILE = os.path.join(BASE_DIR, "historico.json")

def inicializar_entorno_admin():
    """Crea los directorios necesarios para la administración."""
    if not os.path.exists(BASE_DIR):
        os.makedirs(BASE_DIR)
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)

def _generar_firma_log(entrada):
    """Genera una firma de integridad para una entrada del historial."""
    data = f"{entrada['timestamp']}{entrada['accion']}{entrada['director']}"
    return hashlib.sha256(data.encode()).hexdigest()

def registrar_cronica(accion, director="Richon"):
    """Registra una acción en el historial firmado del Director."""
    inicializar_entorno_admin()
    entrada = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "accion": accion,
        "director": director
    }
    entrada["firma"] = _generar_firma_log(entrada)
    
    try:
        with open(LOG_FILE, 'r+', encoding='utf-8') as f:
            datos = json.load(f)
            datos.append(entrada)
            f.seek(0)
            json.dump(datos, f, indent=4)
            f.truncate()
    except Exception as e:
        print(f"{Colors.RED}[ERROR] No se pudo registrar la crónica: {e}{Colors.ENDC}")

def ver_cronicas():
    """Muestra el historial de acciones del Director."""
    if not os.path.exists(LOG_FILE):
        print(f"{Colors.YELLOW}No hay crónicas registradas aún.{Colors.ENDC}")
        return
    
    print(f"\n{Colors.CYAN}--- CRÓNICAS DEL DIRECTOR (Historial Firmado) ---{Colors.ENDC}")
    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        datos = json.load(f)
        for d in datos:
            firma_valida = _generar_firma_log(d) == d["firma"]
            status_firma = f"{Colors.GREEN}[V]{Colors.ENDC}" if firma_valida else f"{Colors.RED}[CORRUPTO]{Colors.ENDC}"
            print(f"[{d['timestamp']}] {status_firma} {Colors.BOLD}{d['director']}{Colors.ENDC}: {d['accion']}")
    input("\nPresiona Enter para continuar...")

def crear_punto_restauracion():
    """Crea un backup de los archivos .py actuales."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_backup = f"Snapshot_{timestamp}"
    ruta_backup = os.path.join(BACKUP_DIR, nombre_backup)
    
    os.makedirs(ruta_backup)
    
    # Copiar archivos raíz (.py)
    for f in os.listdir('.'):
        if f.endswith('.py'):
            shutil.copy(f, ruta_backup)
    
    # Copiar componentes
    comp_dest = os.path.join(ruta_backup, "componentes")
    os.makedirs(comp_dest)
    for f in os.listdir('componentes'):
        if f.endswith('.py'):
            shutil.copy(os.path.join('componentes', f), comp_dest)
            
    registrar_cronica(f"Punto de restauración creado: {nombre_backup}")
    print(f"{Colors.GREEN}[ÉXITO] Punto de restauración '{nombre_backup}' creado.{Colors.ENDC}")

def restaurar_sistema():
    """Permite volver a un punto de restauración anterior."""
    snapshots = sorted([d for d in os.listdir(BACKUP_DIR) if os.path.isdir(os.path.join(BACKUP_DIR, d))], reverse=True)
    
    if not snapshots:
        print(f"{Colors.YELLOW}No hay puntos de restauración disponibles.{Colors.ENDC}")
        return

    print(f"\n{Colors.MAGENTA}--- RESTAURACIÓN INTERNA ---{Colors.ENDC}")
    for i, s in enumerate(snapshots):
        print(f"  {i+1}. {s}")
    print(f"  0. Cancelar")
    
    try:
        idx = int(input("\n>> Selecciona el Snapshot a restaurar: ")) - 1
        if idx == -1: return
        if 0 <= idx < len(snapshots):
            target = snapshots[idx]
            confirm = input(f"{Colors.RED}¿Confirmas la restauración al punto '{target}'? Los cambios actuales se perderán. (s/n): {Colors.ENDC}").lower()
            if confirm == 's':
                source_path = os.path.join(BACKUP_DIR, target)
                
                # Restaurar archivos raíz
                for f in os.listdir(source_path):
                    if f.endswith('.py'):
                        shutil.copy(os.path.join(source_path, f), '.')
                
                # Restaurar componentes
                source_comp = os.path.join(source_path, "componentes")
                for f in os.listdir(source_comp):
                    if f.endswith('.py'):
                        shutil.copy(os.path.join(source_comp, f), 'componentes')
                
                registrar_cronica(f"SISTEMA RESTAURADO al punto: {target}")
                print(f"{Colors.GREEN}[ÉXITO] Sistema restaurado. Se recomienda reiniciar.{Colors.ENDC}")
        else:
            print(f"{Colors.RED}Opción inválida.{Colors.ENDC}")
    except ValueError:
        print(f"{Colors.RED}Entrada no válida.{Colors.ENDC}")

def menu_director():
    """Panel de mando exclusivo para el Director."""
    # Importación local para autorización
    from . import modulo_seguridad
    
    if not modulo_seguridad.verificar_credenciales_director():
        return "Fallo de autenticación en Panel del Director."

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(fr"""{Colors.BOLD}{Colors.MAGENTA}
          .-.
         (u.u)  PANEL DEL DIRECTOR
          |=|   Crónicas & Recuperación
         /   \{Colors.ENDC}""")
        
        print(f"\n  1. {Colors.BOLD}Ver Crónicas{Colors.ENDC} (Historial Firmado)")
        print(f"  2. {Colors.BOLD}Forjar Punto de Restauración{Colors.ENDC}")
        print(f"  3. {Colors.BOLD}Restaurar Sistema{Colors.ENDC} (Regresión)")
        print(f"  {Colors.YELLOW}0. Volver al Panel de Control{Colors.ENDC}")
        
        choice = input("\n>> Orden del Amo: ").strip()
        
        if choice == '1':
            ver_cronicas()
        elif choice == '2':
            crear_punto_restauracion()
            input("\n--- Enter para continuar ---")
        elif choice == '3':
            restaurar_sistema()
            input("\n--- Enter para continuar ---")
        elif choice == '0':
            break
        else:
            print(f"{Colors.RED}[ERROR] Orden no reconocida.{Colors.ENDC}")
    
    return "Salida de Panel del Director."
