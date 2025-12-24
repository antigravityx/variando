# componentes/modulo_tickets.py
import os
import json
import hashlib
from datetime import datetime
import uuid

from .colores import Colors

TICKETS_DIR = "cronicas_director/tickets"
TOKENS_FILE = "cronicas_director/tokens_usuarios.json"

def inicializar_sistema_tickets():
    """Crea las carpetas necesarias para el sistema de tickets."""
    if not os.path.exists(TICKETS_DIR):
        os.makedirs(TICKETS_DIR)
    if not os.path.exists(TOKENS_FILE):
        with open(TOKENS_FILE, 'w', encoding='utf-8') as f:
            json.dump({"tokens": [], "usuarios_autorizados": []}, f, indent=4)

def generar_firma_corta(data, longitud=8):
    """Genera una firma corta reconocible (primeros N caracteres del hash)."""
    hash_completo = hashlib.sha256(data.encode()).hexdigest()
    return hash_completo[:longitud].upper()

def generar_token_accion(usuario, accion, datos_extra=""):
    """
    Genera un token único para una acción específica de un usuario.
    Formato: USR-ACCION-FIRMA
    """
    timestamp = datetime.now().isoformat()
    data_token = f"{usuario}-{accion}-{timestamp}-{datos_extra}"
    firma = generar_firma_corta(data_token, 6)
    token_id = f"{usuario[:3].upper()}-{accion[:3].upper()}-{firma}"
    
    token = {
        "token_id": token_id,
        "usuario": usuario,
        "accion": accion,
        "datos_extra": datos_extra,
        "timestamp": timestamp,
        "firma_completa": hashlib.sha256(data_token.encode()).hexdigest()
    }
    
    # Guardar token
    with open(TOKENS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    data["tokens"].append(token)
    
    with open(TOKENS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
    
    return token_id

def ver_tickets_pendientes():
    """Muestra todos los tickets pendientes de revisión."""
    inicializar_sistema_tickets()
    
    print(f"\n{Colors.CYAN}--- TICKETS DE USUARIOS (Solicitudes Pendientes) ---{Colors.ENDC}")
    
    archivos_tickets = [f for f in os.listdir(TICKETS_DIR) if f.endswith('.json')]
    
    if not archivos_tickets:
        print(f"{Colors.YELLOW}[INFO] No hay tickets pendientes.{Colors.ENDC}")
        return
    
    tickets_pendientes = []
    for archivo in archivos_tickets:
        ruta = os.path.join(TICKETS_DIR, archivo)
        with open(ruta, 'r', encoding='utf-8') as f:
            ticket = json.load(f)
            if ticket.get("estado") == "pendiente":
                tickets_pendientes.append((archivo, ticket))
    
    if not tickets_pendientes:
        print(f"{Colors.YELLOW}[INFO] Todos los tickets han sido procesados.{Colors.ENDC}")
        return
    
    print(f"\n{Colors.BOLD}{'#':<4}{'Usuario':<20}{'Solicitud':<40}{'Fecha':<20}{Colors.ENDC}")
    print("-" * 90)
    
    for i, (archivo, ticket) in enumerate(tickets_pendientes, 1):
        print(f"{i:<4}{ticket['usuario']:<20}{ticket['solicitud'][:37]+'...':<40}{ticket['fecha']:<20}")
    
    print(f"\n{Colors.MAGENTA}Opciones:{Colors.ENDC}")
    print("  [número] - Ver detalles y procesar ticket")
    print("  0 - Volver")
    
    opcion = input("\n>> Selección: ").strip()
    
    if opcion == '0':
        return
    
    try:
        idx = int(opcion) - 1
        if 0 <= idx < len(tickets_pendientes):
            archivo, ticket = tickets_pendientes[idx]
            procesar_ticket(archivo, ticket)
    except ValueError:
        print(f"{Colors.RED}[ERROR] Opción no válida.{Colors.ENDC}")

def procesar_ticket(archivo, ticket):
    """Procesa un ticket específico: aprobar, denegar, o asignar permisos."""
    print(f"\n{Colors.CYAN}--- DETALLES DEL TICKET ---{Colors.ENDC}")
    print(f"Usuario: {ticket['usuario']}")
    print(f"Solicitud: {ticket['solicitud']}")
    print(f"Descripción: {ticket.get('descripcion', 'N/A')}")
    print(f"Fecha: {ticket['fecha']}")
    print(f"Dispositivo: {ticket.get('dispositivo_id', 'N/A')}")
    
    print(f"\n{Colors.MAGENTA}Acciones:{Colors.ENDC}")
    print("  1. Aprobar y Otorgar Permisos Personalizados")
    print("  2. Denegar Solicitud")
    print("  0. Volver")
    
    accion = input("\n>> Acción: ").strip()
    
    if accion == '1':
        otorgar_permisos_personalizados(ticket)
        ticket["estado"] = "aprobado"
        ticket["procesado_por"] = "richon"
        ticket["fecha_procesado"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Generar token de aprobación
        token_id = generar_token_accion(ticket['usuario'], "TICKET_APROBADO", ticket['solicitud'][:20])
        ticket["token_aprobacion"] = token_id
        
        print(f"{Colors.GREEN}[OK] Ticket aprobado. Token: {token_id}{Colors.ENDC}")
        
    elif accion == '2':
        ticket["estado"] = "denegado"
        ticket["procesado_por"] = "richon"
        ticket["fecha_procesado"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        motivo = input(">> Motivo de denegación: ").strip()
        ticket["motivo_denegacion"] = motivo
        print(f"{Colors.YELLOW}[INFO] Ticket denegado.{Colors.ENDC}")
    
    # Guardar cambios
    ruta = os.path.join(TICKETS_DIR, archivo)
    with open(ruta, 'w', encoding='utf-8') as f:
        json.dump(ticket, f, indent=4)

def otorgar_permisos_personalizados(ticket):
    """Permite al Director otorgar permisos específicos a un usuario."""
    print(f"\n{Colors.CYAN}--- OTORGAR PERMISOS PERSONALIZADOS ---{Colors.ENDC}")
    print(f"Usuario: {ticket['usuario']}")
    
    permisos_disponibles = {
        "1": "Gestión de Proyectos",
        "2": "Control de Stock",
        "3": "Visor de Presupuestos",
        "4": "Reportes de Sesión",
        "5": "Cerebro Numérico (Calculadora)",
        "6": "Herramientas de Red (Ping, IP)",
        "7": "Modo Espía (Ventanas)",
        "8": "Acceso a Panel Director (Limitado)"
    }
    
    print("\nPermisos Disponibles:")
    for key, valor in permisos_disponibles.items():
        print(f"  {key}. {valor}")
    
    print("\nIngresa los números separados por comas (ej: 1,2,5)")
    seleccion = input(">> Permisos: ").strip()
    
    permisos_otorgados = []
    for num in seleccion.split(','):
        num = num.strip()
        if num in permisos_disponibles:
            permisos_otorgados.append(permisos_disponibles[num])
    
    # Guardar en usuarios autorizados
    with open(TOKENS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    usuario_autorizado = {
        "nombre": ticket['usuario'],
        "permisos": permisos_otorgados,
        "fecha_autorizacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "autorizado_por": "richon",
        "dispositivo_id": ticket.get('dispositivo_id', 'N/A'),
        "firma_usuario": generar_firma_corta(ticket['usuario'], 6)
    }
    
    data["usuarios_autorizados"].append(usuario_autorizado)
    
    with open(TOKENS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
    
    print(f"{Colors.GREEN}[OK] Permisos otorgados a {ticket['usuario']}{Colors.ENDC}")
    print(f"Firma de Usuario: {usuario_autorizado['firma_usuario']}")

def crear_ticket_usuario(usuario, solicitud, descripcion=""):
    """Crea un nuevo ticket de solicitud (usado por usuarios comunes)."""
    inicializar_sistema_tickets()
    
    ticket_id = str(uuid.uuid4())[:8]
    ticket = {
        "ticket_id": ticket_id,
        "usuario": usuario,
        "solicitud": solicitud,
        "descripcion": descripcion,
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "estado": "pendiente",
        "dispositivo_id": str(uuid.getnode())  # MAC address como ID
    }
    
    archivo = f"ticket_{ticket_id}.json"
    ruta = os.path.join(TICKETS_DIR, archivo)
    
    with open(ruta, 'w', encoding='utf-8') as f:
        json.dump(ticket, f, indent=4)
    
    print(f"{Colors.GREEN}[OK] Ticket creado: {ticket_id}{Colors.ENDC}")
    print(f"{Colors.CYAN}Tu solicitud será revisada por el Director.{Colors.ENDC}")
    return ticket_id

def ver_mis_tokens(usuario):
    """Muestra los tokens generados para un usuario específico."""
    with open(TOKENS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    tokens_usuario = [t for t in data["tokens"] if t["usuario"] == usuario]
    
    if not tokens_usuario:
        print(f"{Colors.YELLOW}[INFO] No tienes tokens registrados.{Colors.ENDC}")
        return
    
    print(f"\n{Colors.CYAN}--- MIS TOKENS DE VALIDACIÓN ---{Colors.ENDC}")
    print(f"{Colors.BOLD}{'Token ID':<20}{'Acción':<30}{'Fecha':<20}{Colors.ENDC}")
    print("-" * 70)
    
    for token in tokens_usuario[-10:]:  # Últimos 10
        print(f"{token['token_id']:<20}{token['accion']:<30}{token['timestamp'][:19]:<20}")

def menu_gestion_tickets():
    """Menú principal para gestión de tickets (Panel Director)."""
    log_output = "Acceso a Gestión de Tickets."
    
    while True:
        print(f"\n{Colors.MAGENTA}--- GESTIÓN DE TICKETS Y PERMISOS ---{Colors.ENDC}")
        print("  1. Ver Tickets Pendientes")
        print("  2. Ver Todos los Usuarios Autorizados")
        print("  3. Revocar Permisos de Usuario")
        print("  4. Ver Historial de Tokens")
        print("  0. Volver")
        
        opcion = input("\n>> Orden: ").strip()
        
        if opcion == '1':
            ver_tickets_pendientes()
        elif opcion == '2':
            ver_usuarios_autorizados()
        elif opcion == '3':
            revocar_permisos()
        elif opcion == '4':
            ver_historial_tokens()
        elif opcion == '0':
            break
        else:
            print(f"{Colors.RED}[ERROR] Opción no válida.{Colors.ENDC}")
    
    return log_output

def ver_usuarios_autorizados():
    """Muestra todos los usuarios con permisos personalizados."""
    with open(TOKENS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    usuarios = data.get("usuarios_autorizados", [])
    
    if not usuarios:
        print(f"{Colors.YELLOW}[INFO] No hay usuarios autorizados.{Colors.ENDC}")
        return
    
    print(f"\n{Colors.CYAN}--- USUARIOS AUTORIZADOS ---{Colors.ENDC}")
    for i, user in enumerate(usuarios, 1):
        print(f"\n{i}. {Colors.BOLD}{user['nombre']}{Colors.ENDC} (Firma: {user['firma_usuario']})")
        print(f"   Permisos: {', '.join(user['permisos'])}")
        print(f"   Autorizado: {user['fecha_autorizacion']}")
    
    input("\n--- Presiona Enter para continuar ---")

def revocar_permisos():
    """Revoca permisos de un usuario específico."""
    with open(TOKENS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    usuarios = data.get("usuarios_autorizados", [])
    
    if not usuarios:
        print(f"{Colors.YELLOW}[INFO] No hay usuarios para revocar.{Colors.ENDC}")
        return
    
    print(f"\n{Colors.CYAN}--- REVOCAR PERMISOS ---{Colors.ENDC}")
    for i, user in enumerate(usuarios, 1):
        print(f"{i}. {user['nombre']} (Firma: {user['firma_usuario']})")
    
    try:
        idx = int(input("\n>> Usuario a revocar (0 para cancelar): ").strip()) - 1
        if idx >= 0 and idx < len(usuarios):
            usuario_revocado = usuarios.pop(idx)
            data["usuarios_autorizados"] = usuarios
            
            with open(TOKENS_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            
            print(f"{Colors.GREEN}[OK] Permisos revocados a {usuario_revocado['nombre']}{Colors.ENDC}")
    except ValueError:
        print(f"{Colors.RED}[ERROR] Entrada no válida.{Colors.ENDC}")

def ver_historial_tokens():
    """Muestra el historial completo de tokens generados."""
    with open(TOKENS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    tokens = data.get("tokens", [])
    
    if not tokens:
        print(f"{Colors.YELLOW}[INFO] No hay tokens registrados.{Colors.ENDC}")
        return
    
    print(f"\n{Colors.CYAN}--- HISTORIAL DE TOKENS (Últimos 20) ---{Colors.ENDC}")
    print(f"{Colors.BOLD}{'Token ID':<20}{'Usuario':<15}{'Acción':<25}{'Fecha':<20}{Colors.ENDC}")
    print("-" * 80)
    
    for token in tokens[-20:]:
        print(f"{token['token_id']:<20}{token['usuario']:<15}{token['accion']:<25}{token['timestamp'][:19]:<20}")
    
    input("\n--- Presiona Enter para continuar ---")
