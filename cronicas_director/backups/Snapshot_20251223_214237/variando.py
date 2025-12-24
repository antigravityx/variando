# ==============================================================================
#   EL CEREBRO - SISTEMA DE GESTIÓN Y MONITOREO (RichonOS)
#   Desarrollado por: Richon & Verix (Gemini AI)
#   Versión: 1.3 (Arquitectura Modular)
#   Descargo: El uso de estas herramientas es responsabilidad exclusiva del operador.
#   AVISO LEGAL: Software de uso personal. Uso corporativo requiere autorización explícita del autor.
# ==============================================================================

import os
from dotenv import load_dotenv
from datetime import datetime
import traceback
import sys

# --- IMPORTACIÓN DE COMPONENTES MODULARES ---
try:
    from componentes.colores import Colors
    from componentes import (
        modulo_sistema,
        modulo_admin,
        modulo_red,
        modulo_proyectos,
        modulo_gestion,
        modulo_seguridad,
        modulo_integridad
    )
except ImportError as e:
    print("\033[91m[ERROR CRÍTICO] No se encontraron los archivos de componentes.")
    print(f"Detalle: {e}")
    print("Asegúrate de que la carpeta 'componentes' con todos sus archivos .py esté junto a este ejecutable.\033[0m")
    input("\nPresiona ENTER para salir.")
    sys.exit()

# Carga las variables del archivo .env en el entorno
load_dotenv()

def mostrar_encabezado():
    """Imprime el encabezado principal del programa."""
    os.system('cls' if os.name == 'nt' else 'clear')
    print(fr"""{Colors.BOLD}{Colors.CYAN}
      .-.
     (o.o)  EL CEREBRO
      |=|   Panel de Control RichonOS v1.3 (Modular)
     /   \{Colors.ENDC}""")

def mostrar_menu():
    """Muestra el menú de opciones numerado y balanceado."""
    # Columna 1: ESTADO & SISTEMA (9 ítems)
    col_estado = [
        "1. Uso de CPU",
        "2. Uso de RAM",
        "3. Usuarios Activos",
        "4. Programas Instalados",
        "5. Analizar Procesos",
        "6. Analizador de Disco",
        "7. Limpieza de Sistema",
        "8. Actualizar Programa",
        "9. Reportes de Sesión"
    ]
    # Columna 2: RED & INTELIGENCIA (9 ítems)
    col_red = [
        "10. Mis Direcciones IP",
        "11. Herramienta Ping",
        "12. Puertos Abiertos",
        "13. Analizar WiFi",
        "14. Escáner Red Local",
        "15. Escáner Bluetooth",
        "16. Depredador (OSINT)",
        "17. Cazador Shodan",
        "18. Geo & Clima"
    ]
    # Columna 3: PODER & SEGURIDAD (11 ítems)
    col_poder = [
        "19. Celador de Llaves",
        "20. Guardián Integridad",
        "21. Gestión Proyectos",
        "22. Control de Stock",
        "23. Precios Referencia",
        "24. Visor Presupuestos",
        "25. Modo Espía",
        "26. Cerebro Numérico",
        "27. Ejecutar Programa",
        f"{Colors.MAGENTA}{Colors.BOLD}28. PANEL DIRECTOR{Colors.ENDC}",
        f"{Colors.RED}{Colors.BOLD}29. APOCALIPSIS{Colors.ENDC}"
    ]

    print(f"\n{Colors.BOLD}┌─ ESTADO & SISTEMA ──────┬─ RED & INTELIGENCIA ──────┬─ PODER & SEGURIDAD ───────┐{Colors.ENDC}")
    max_rows = max(len(col_estado), len(col_red), len(col_poder))
    import re
    ansi_escape = re.compile(r'\033\[[0-9;]*m')
    for i in range(max_rows):
        # Celda 1
        item1 = f"  {col_estado[i]:<24}" if i < len(col_estado) else ' ' * 26
        # Celda 2
        item2 = f"  {col_red[i]:<26}" if i < len(col_red) else ' ' * 28
        # Celda 3 (con colores ANSI)
        full3 = f"  {col_poder[i]}" if i < len(col_poder) else ""
        clean3 = ansi_escape.sub('', full3)
        padding3 = ' ' * (26 - len(clean3))
        
        print(f"{Colors.BOLD}│{Colors.ENDC}{item1}{Colors.BOLD}│{Colors.ENDC}{item2}{Colors.BOLD}│{Colors.ENDC}{full3}{padding3}{Colors.BOLD}│{Colors.ENDC}")
    print(f"{Colors.BOLD}└─────────────────────────┴───────────────────────────┴───────────────────────────┘{Colors.ENDC}")
    print(f"  {Colors.YELLOW}{Colors.BOLD}0. Salir{Colors.ENDC}")

def guardar_reporte(log_sesion):
    """Guarda las consultas de la sesión en un archivo de texto."""
    if not log_sesion:
        print(f"\n{Colors.YELLOW}[INFO] No hay consultas que guardar en esta sesión.{Colors.ENDC}")
        return

    now = datetime.now()
    filename = now.strftime("reporte_cerebro_%Y-%m-%d.txt")
    
    with open(filename, 'a', encoding='utf-8') as f:
        if f.tell() == 0:
            f.write("╔═════════════════════════════════════════╗\n")
            f.write("║   REPORTE CONSOLIDADO - EL CEREBRO      ║\n")
            f.write("╚═════════════════════════════════════════╝\n")
        
        f.write(f"\n\n═══════════ SESIÓN GUARDADA EL {now.strftime('%Y-%m-%d a las %H:%M:%S')} ═══════════\n")
        f.writelines(log + '\n' for log in log_sesion)
    print(f"\n{Colors.GREEN}[SUCCESS] Reporte guardado/actualizado en: {filename}{Colors.ENDC}")

def gestionar_salida(log_sesion):
    """Muestra un submenú al salir y gestiona la opción."""
    print(f"\n{Colors.YELLOW}{Colors.BOLD}MENÚ DE SALIDA{Colors.ENDC}")
    print("  1. Guardar reporte y salir")
    print("  2. Salir directamente")
    print("  0. Volver al menú principal")
    
    opcion = input(">> Selecciona una opción de salida: ")
    if opcion == '1':
        guardar_reporte(log_sesion)
        return False
    elif opcion == '2':
        return False
    return True

def menu_post_accion(opcion_actual, log_sesion):
    """Muestra un menú de acciones después de ejecutar una opción."""
    print(f"\n{Colors.MAGENTA}{Colors.BOLD}¿QUÉ HACER AHORA?{Colors.ENDC}")
    print("  [s]iguiente: Ejecuta la siguiente opción del menú.")
    print("  [m]enú: Vuelve al menú principal.")
    print("  [g]uardar: Guarda el reporte de la sesión actual.")
    print("  [#]: Escribe el número de otra opción para ir directamente.")
    
    while True:
        eleccion = input(">> Elige una acción: ").lower().strip()
        if eleccion == 'm' or eleccion == 'menu':
            return None
        elif eleccion == 's' or eleccion == 'siguiente':
            try:
                return str((int(opcion_actual) % 28) + 1)
            except: return None
        elif eleccion == 'g':
            guardar_reporte(log_sesion)
        elif eleccion.isdigit() and 1 <= int(eleccion) <= 28:
            return eleccion
        else:
            print(f"{Colors.RED}[ERROR] Opción no reconocida.{Colors.ENDC}")

def iniciar_panel():
    """Función principal que muestra el menú y procesa las opciones."""
    if not modulo_integridad.verificar_integridad():
        input("\nPresiona Enter para salir.")
        return

    mostrar_encabezado()
    log_sesion = []
    proxima_opcion = None

    # Mapeo actualizado según la nueva numeración lógica
    opciones = {
        # --- ESTADO & SISTEMA ---
        '1': modulo_sistema.mostrar_uso_cpu,
        '2': modulo_sistema.mostrar_uso_memoria,
        '3': modulo_sistema.mostrar_usuarios,
        '4': modulo_sistema.mostrar_programas_instalados,
        '5': modulo_sistema.analizar_procesos,
        '6': modulo_sistema.analizador_disco,
        '7': modulo_sistema.limpieza_sistema,
        '8': modulo_gestion.actualizar_programa,
        '9': modulo_gestion.visualizar_reportes,
        
        # --- RED & INTELIGENCIA ---
        '10': modulo_red.ver_mis_ips,
        '11': modulo_red.herramienta_ping,
        '12': modulo_red.mostrar_puertos_abiertos,
        '13': modulo_red.analizar_redes_wifi,
        '14': modulo_red.escaner_red_local,
        '15': modulo_red.escaner_bluetooth,
        '16': modulo_red.depredador_silencioso,
        '17': modulo_red.cazador_shodan,
        '18': modulo_red.geolocalizacion_clima,
        
        # --- PODER & SEGURIDAD ---
        '19': modulo_seguridad.celador_de_llaves,
        '20': modulo_integridad.menu_guardian,
        '21': modulo_gestion.gestionar_avance_proyecto,
        '22': modulo_gestion.gestionar_stock,
        '23': modulo_proyectos.consultar_precios_referencia,
        '24': modulo_gestion.visor_presupuestos,
        '25': modulo_gestion.modo_espia,
        '26': modulo_proyectos.cerebro_numerico,
        '27': modulo_sistema.ejecutar_programa,
        '28': modulo_admin.menu_director,
        '29': modulo_sistema.ejecutar_apocalipsis
    }

    try:
        while True:
            if proxima_opcion is None:
                mostrar_menu()
                opcion = input(">> Selecciona una opción: ").strip()
            else:
                opcion = proxima_opcion
                proxima_opcion = None

            if opcion == '0':
                if not gestionar_salida(log_sesion):
                    print("\nCerrando El Cerebro. ¡Hasta la próxima, richon!")
                    break
            elif opcion in opciones:
                log = opciones[opcion]()
                if log:
                    log_sesion.append(f"[{datetime.now().strftime('%H:%M:%S')}] {log}")
                proxima_opcion = menu_post_accion(opcion, log_sesion)
            else:
                print(f"\n{Colors.RED}[ERROR] Opción '{opcion}' no válida. Inténtalo de nuevo.{Colors.ENDC}")
                input("\n--- Presiona Enter para continuar ---")

            if proxima_opcion is None:
                mostrar_encabezado()

    except KeyboardInterrupt:
        print("\n\nCierre forzado. ¡Adiós, richon!")

def main():
    iniciar_panel()

if __name__ == "__main__":
    try:
        main()
    except Exception:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        error_msg = f"[{timestamp}] ERROR FATAL:\n{traceback.format_exc()}\n"
        with open("debug_crash.txt", "a", encoding="utf-8") as f:
            f.write(error_msg)
        print(f"\n{Colors.RED}¡ALERTA DE SISTEMA! El Cerebro ha sufrido un error crítico.{Colors.ENDC}")
        print(f"Se ha generado un reporte en: 'debug_crash.txt'")
        print(f"\n{Colors.YELLOW}Detalle del error:{Colors.ENDC}\n{error_msg}")
        input(f"\n{Colors.BOLD}Presiona ENTER para cerrar la ventana...{Colors.ENDC}")
