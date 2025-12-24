# componentes/modulo_admin.py
import os
import json
import shutil
import hashlib
from datetime import datetime
from .colores import Colors
from .utilidades import input_con_mascara
from .modulo_seguridad import registrar_remembranza, obtener_huella_digital

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

def gestionar_personal():
    """Permite al Director dar de alta/baja a socios u operadores."""
    archivo_boveda = "boveda_celador.json"
    
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"\n{Colors.CYAN}--- GESTIÓN DE PERSONAL & ACCESOS ---{Colors.ENDC}")
        
        with open(archivo_boveda, 'r', encoding='utf-8') as f:
            boveda = json.load(f)
        
        usuarios = boveda.get("usuarios_adicionales", [])
        
        if not usuarios:
            print(f"  {Colors.YELLOW}No hay usuarios adicionales registrados.{Colors.ENDC}")
        else:
            for i, u in enumerate(usuarios):
                nivel_str = "SOCIO" if u['nivel'] == 1 else "OPERADOR"
                print(f"  {i+1}. [{nivel_str}] {u['nombre']}")
        
        print("\n  a. Dar de Alta Nuevo Usuario")
        print("  b. Dar de Baja Usuario")
        print("  0. Volver")
        
        op = input("\n>> Selección: ").lower().strip()
        
        if op == '0': break
        
        elif op == 'a':
            nombre = input(">> Nombre del Usuario: ").strip()
            if not nombre: continue
            print(">> Nivel de Acceso:")
            print("   1. SOCIO (Negocio + Red)")
            print("   2. OPERADOR (Cálculos + Sistema)")
            try:
                nivel = int(input("   Selección: "))
                if nivel not in [1, 2]: raise ValueError
                pin = input_con_mascara(">> Establecer PIN (4+ dígitos): ").strip()
                if len(pin) < 4:
                    print(f"{Colors.RED}El PIN es demasiado corto.{Colors.ENDC}")
                else:
                    nuevo_user = {
                        "nombre": nombre,
                        "nivel": nivel,
                        "pin_hash": hashlib.sha256(pin.encode()).hexdigest()
                    }
                    boveda.setdefault("usuarios_adicionales", []).append(nuevo_user)
                    with open(archivo_boveda, 'w', encoding='utf-8') as f:
                        json.dump(boveda, f, indent=4)
                    registrar_cronica(f"ALTA DE USUARIO: {nombre} (Nivel {nivel})")
                    print(f"{Colors.GREEN}[EXITO] Usuario '{nombre}' creado.{Colors.ENDC}")
            except:
                print(f"{Colors.RED}Entrada inválida.{Colors.ENDC}")
            input("Pulse Enter...")

        elif op == 'b':
            try:
                idx = int(input(">> Número de usuario a eliminar: ")) - 1
                if 0 <= idx < len(usuarios):
                    eliminado = boveda["usuarios_adicionales"].pop(idx)
                    with open(archivo_boveda, 'w', encoding='utf-8') as f:
                        json.dump(boveda, f, indent=4)
                    registrar_cronica(f"BAJA DE USUARIO: {eliminado['nombre']}")
                    print(f"{Colors.YELLOW}[AVISO] Usuario '{eliminado['nombre']}' eliminado.{Colors.ENDC}")
                else:
                    print(f"{Colors.RED}Índice fuera de rango.{Colors.ENDC}")
            except:
                print(f"{Colors.RED}Entrada inválida.{Colors.ENDC}")
            input("Pulse Enter...")

def gestionar_lista_roja():
    """Permite al Director gestionar la lista de nombres reservados."""
    archivo_boveda = "boveda_celador.json"
    
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"\n{Colors.RED}{Colors.BOLD}--- GESTIÓN DE LA LISTA ROJA (IDENTIDADES) ---{Colors.ENDC}")
        
        with open(archivo_boveda, 'r', encoding='utf-8') as f:
            boveda = json.load(f)
        
        nombres = boveda.get("reserved_names", [])
        director_principal = boveda.get("director", "N/A")
        
        print(f"  Director Principal: {Colors.CYAN}{director_principal}{Colors.ENDC}")
        print(f"  Nombres Reservados Activos:")
        if not nombres:
            print(f"    {Colors.YELLOW}Ninguno adicional.{Colors.ENDC}")
        else:
            for i, n in enumerate(nombres):
                print(f"    {i+1}. {n}")
        
        print("\n  a. Añadir Identidad (Lista Roja)")
        print("  b. Eliminar Identidad")
        print("  0. Volver")
        
        op = input("\n>> Selección: ").lower().strip()
        
        if op == '0': break
        
        elif op == 'a':
            nuevo = input(">> Nuevo nombre reservado: ").strip().lower()
            if not nuevo: continue
            
            nuevos_nombres = [nuevo]
            print(f"\n{Colors.CYAN}¿Deseas generar variantes inteligentes para '{nuevo}'?{Colors.ENDC}")
            print("   (ej: UPPERCASE, Capitalized, admin_..., etc.)")
            if input("   (s/n): ").lower() == 's':
                variantes = [
                    nuevo.upper(),
                    nuevo.capitalize(),
                    f"_{nuevo}_",
                    f"admin_{nuevo}",
                    f"master_{nuevo}"
                ]
                nuevos_nombres.extend(variantes)
                print(f"  {Colors.YELLOW}[INFO] Se han preparado {len(variantes)} variantes para evaluar.{Colors.ENDC}")

            agregados = 0
            for n in nuevos_nombres:
                if n not in nombres:
                    nombres.append(n)
                    agregados += 1
            
            if agregados > 0:
                boveda["reserved_names"] = nombres
                with open(archivo_boveda, 'w', encoding='utf-8') as f:
                    json.dump(boveda, f, indent=4)
                registrar_cronica(f"IDENTIDADES AÑADIDAS (Red List): {nuevo} (+ {agregados-1} variantes)")
                print(f"{Colors.GREEN}[ÉXITO] Se han añadido {agregados} identificadores a la Lista Roja.{Colors.ENDC}")
            else:
                print(f"{Colors.YELLOW}[AVISO] Todos estos nombres ya estaban en la lista.{Colors.ENDC}")
            input("Pulse Enter...")

        elif op == 'b':
            try:
                idx = int(input(">> Número de identidad a eliminar: ")) - 1
                if 0 <= idx < len(nombres):
                    eliminado = nombres.pop(idx)
                    if eliminado.lower() == director_principal.lower():
                        print(f"{Colors.RED}[ERROR] No puedes eliminar el nombre del Director Principal.{Colors.ENDC}")
                    else:
                        boveda["reserved_names"] = nombres
                        with open(archivo_boveda, 'w', encoding='utf-8') as f:
                            json.dump(boveda, f, indent=4)
                        registrar_cronica(f"IDENTIDAD ELIMINADA DE LISTA ROJA: {eliminado}")
                        print(f"{Colors.YELLOW}[AVISO] Identidad '{eliminado}' eliminada.{Colors.ENDC}")
                else:
                    print(f"{Colors.RED}Índice fuera de rango.{Colors.ENDC}")
            except:
                print(f"{Colors.RED}Entrada inválida.{Colors.ENDC}")
            input("Pulse Enter...")

def ver_remembranzas():
    """Muestra el historial de intentos de acceso y dispositivos."""
    log_path = "cronicas_director/remembranzas.json"
    if not os.path.exists(log_path):
        print(f"{Colors.YELLOW}No hay recuerdos de acceso registrados aún.{Colors.ENDC}")
        return
    
    print(f"\n{Colors.CYAN}--- MEMORIA DE REMEMBRANZAS (AUDITORÍA DE ACCESOS) ---{Colors.ENDC}")
    try:
        # Al abrir, registramos que el Director está auditando el dispositivo actual
        h_actual = obtener_huella_digital()
        registrar_remembranza("DIRECTOR", h_actual, "AUDITORIA_ACTIVA")
        
        with open(log_path, 'r', encoding='utf-8') as f:
            datos = json.load(f)
            # Mostrar solo los últimos 20 para no saturar
            for d in datos[-20:]:
                evento = d.get('evento', 'UNKNOWN')
                color_evento = Colors.GREEN if "EXITOSO" in evento or "AMIGO" in evento else Colors.RED
                print(f"[{d['timestamp']}] {d['identidad']} - {color_evento}{evento}{Colors.ENDC}")
                print(f"    IP: {d.get('ip_local', '???')} | OS: {d.get('os', '???')} | Huella: {d.get('huella', '???')[:16]}...")
    except Exception as e:
        print(f"{Colors.RED}[ERROR] No se pudo leer la memoria: {e}{Colors.ENDC}")
    input("\nPresiona Enter para continuar...")

def gestionar_amistad_maestra():
    """Permite al Director otorgar confianza total a un hardware específico."""
    alma_path = "cronicas_director/memoria_alma.json"
    if not os.path.exists(alma_path):
        print(f"{Colors.YELLOW}No hay memoria del alma registrada.{Colors.ENDC}")
        return

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"\n{Colors.MAGENTA}{Colors.BOLD}--- ESTRELLAS DE CONFIANZA (ASCENSO DE HARDWARE) ---{Colors.ENDC}")
        
        with open(alma_path, 'r', encoding='utf-8') as f:
            alma = json.load(f)
        
        huellas = alma.get("huellas_conocidas", {})
        if not huellas:
            print(f"  {Colors.YELLOW}No hay dispositivos registrados en el alma.{Colors.ENDC}")
            input("Enter para volver...")
            break
            
        lista_huellas = list(huellas.items())
        for i, (h, data) in enumerate(lista_huellas):
            score = data.get("trust_score", 0)
            nivel = "AMIGO (Total)" if score >= 15 else "CONOCIDO" if score >= 5 else "NUEVO"
            estrellas = "★" * min(5, (score // 3) + 1)
            print(f"  {i+1}. {data.get('nombre', '???')} [{estrellas}] {nivel}")
            print(f"     Huella: {h[:20]}... | Visto: {data.get('last_seen')}")
        
        print("\n  p. Promocionar a CONFIANZA TOTAL (15+ Estrellas)")
        print("  0. Volver")
        
        op = input("\n>> Selección: ").lower().strip()
        if op == '0': break
        elif op == 'p':
            try:
                idx_input = input(">> Número de dispositivo a promocionar: ")
                idx = int(idx_input) - 1
                if 0 <= idx < len(lista_huellas):
                    target_h = lista_huellas[idx][0]
                    alma["huellas_conocidas"][target_h]["trust_score"] = 20 # Direct to Level 2
                    with open(alma_path, 'w', encoding='utf-8') as f:
                        json.dump(alma, f, indent=4)
                    print(f"{Colors.GREEN}[VÍNCULO SELLADO] Este dispositivo es ahora un AMIGO DEL ALMA.{Colors.ENDC}")
                    registrar_cronica(f"PROMOCIÓN DE HARDWARE A AMIGO: {target_h[:10]}")
                else:
                    print(f"{Colors.RED}Índice inválido.{Colors.ENDC}")
            except:
                print(f"{Colors.RED}Entrada no válida.{Colors.ENDC}")
            input("Pulse Enter...")

def menu_director():
    """Panel de mando exclusivo para el Director."""
    # Importación local para autorización
    from . import modulo_seguridad
    
    session = modulo_seguridad.verificar_credenciales_director()
    if not session:
        return "Fallo de autenticación en Panel del Director."

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(fr"""{Colors.BOLD}{Colors.MAGENTA}
          .-.
         (u.u)  PANEL DEL DIRECTOR
          |=|   Control de Mando F5
         /   \{Colors.ENDC}""")
        
        print(f"\n  1. {Colors.BOLD}Ver Crónicas{Colors.ENDC} (Historial Firmado)")
        print(f"  2. {Colors.BOLD}Forjar Punto de Restauración{Colors.ENDC}")
        print(f"  3. {Colors.BOLD}Restaurar Sistema{Colors.ENDC} (Regresión)")
        print(f"  4. {Colors.BOLD}Gestión de Personal{Colors.ENDC} (Roles & Accesos)")
        print(f"  5. {Colors.RED}{Colors.BOLD}Gestión de Lista Roja{Colors.ENDC} (Identidades Director)")
        print(f"  6. {Colors.BOLD}Ver Remembranzas{Colors.ENDC} (Auditoría de Acceso)")
        print(f"  7. {Colors.MAGENTA}{Colors.BOLD}Estrellas de Confianza{Colors.ENDC} (Vínculo Directo)")
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
        elif choice == '4':
            gestionar_personal()
        elif choice == '5':
            gestionar_lista_roja()
        elif choice == '6':
            ver_remembranzas()
        elif choice == '7':
            gestionar_amistad_maestra()
        elif choice == '0':
            break
        else:
            print(f"{Colors.RED}[ERROR] Orden no reconocida.{Colors.ENDC}")
    
    return "Salida de Panel del Director."
