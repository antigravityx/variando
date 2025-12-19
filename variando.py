import os
from dotenv import load_dotenv
import psutil # ¡La librería para obtener datos del sistema!
import time
import json

import subprocess
import winreg
import glob
import pyautogui
import webbrowser
from datetime import datetime
import requests
import shodan
import ipaddress
import re
from bs4 import BeautifulSoup
from num2words import num2words
import locale
from urllib.parse import quote_plus
# Carga las variables del archivo .env en el entorno
load_dotenv()

class Colors:
    """Clase para almacenar los códigos de color ANSI."""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

PROCESOS_CONOCIDOS = {
    "svchost.exe": "Service Host - Proceso genérico de Windows que aloja múltiples servicios del sistema para ahorrar recursos. Es normal ver muchas instancias.",
    "lsass.exe": "Local Security Authority Subsystem Service - Proceso crítico de seguridad. Gestiona inicios de sesión y contraseñas. Si se detiene, el sistema se reinicia.",
    "csrss.exe": "Client Server Runtime Subsystem - Gestiona ventanas, la consola de comandos y otros elementos cruciales de la interfaz de usuario.",
    "wininit.exe": "Windows Initialization Process - Proceso esencial que se inicia con el sistema y lanza otros procesos críticos como services.exe y lsass.exe.",
    "explorer.exe": "Explorador de Windows - Es tu interfaz gráfica: el escritorio, la barra de tareas, el menú de inicio y el explorador de archivos.",
    "services.exe": "Service Control Manager - Gestiona el inicio, detención e interacción de todos los servicios del sistema.",
    "smss.exe": "Session Manager Subsystem - Crea nuevas sesiones de usuario. Es uno de los primeros procesos en arrancar.",
    "winlogon.exe": "Windows Logon Application - Gestiona el inicio y cierre de sesión de los usuarios.",
    "spoolsv.exe": "Spooler Subsystem App - Gestiona los trabajos de impresión y fax.",
    "msmpeng.exe": "Microsoft Malware Protection Engine - Es el motor principal de Microsoft Defender Antivirus.",
    "system": "NT Kernel & System - Representa el núcleo del sistema operativo. Un alto uso puede indicar problemas de drivers o hardware."
    
}

def get_color_for_usage(usage):
    """Devuelve un color basado en el porcentaje de uso."""
    if usage > 75:
        return Colors.RED
    elif usage > 40:
        return Colors.YELLOW
    else:
        return Colors.GREEN

def get_color_for_mem_mb(mem_mb):
    """Devuelve un color basado en el uso de memoria en MB."""
    if mem_mb > 500:
        return Colors.RED
    elif mem_mb > 100:
        return Colors.YELLOW
    else:
        return Colors.GREEN

def mostrar_uso_cpu():
    """Muestra el uso actual de la CPU y devuelve el dato para el log."""
    uso = psutil.cpu_percent(interval=1)
    color = get_color_for_usage(uso)
    output_colored = f"\n{Colors.BLUE}[INFO]{Colors.ENDC} Uso de CPU actual: {color}{uso}%{Colors.ENDC}"
    output_log = f"Uso de CPU actual: {uso}%"
    print(output_colored)
    return output_log

def mostrar_uso_memoria():
    """Muestra el uso actual de la memoria RAM y devuelve el dato para el log."""
    memoria = psutil.virtual_memory()
    uso = memoria.percent
    color = get_color_for_usage(uso)
    info_gb = f"({Colors.BOLD}{memoria.used / 1024**3:.2f}{Colors.ENDC} GB / {Colors.BOLD}{memoria.total / 1024**3:.2f}{Colors.ENDC} GB)"
    output_colored = f"\n{Colors.BLUE}[INFO]{Colors.ENDC} Uso de RAM actual: {color}{uso}%{Colors.ENDC} {info_gb}"
    output_log = f"Uso de RAM actual: {uso}% {info_gb}"
    print(output_colored)
    return output_log

def visualizar_reportes():
    """Busca, lista y muestra el contenido de los reportes guardados."""
    print(f"\n{Colors.MAGENTA}--- Visualizador de Reportes ---{Colors.ENDC}")
    report_files = sorted(glob.glob("reporte_cerebro_*.txt"), reverse=True)

    if not report_files:
        print(f"\n{Colors.YELLOW}[INFO] No se encontraron reportes guardados.{Colors.ENDC}")
        return "Intento de visualización de reportes: No se encontraron archivos."

    print("Reportes disponibles:")
    for i, filename in enumerate(report_files):
        print(f"  {i + 1}. {filename}")

    try:
        choice = int(input("\n>> Elige el número del reporte que quieres ver (0 para cancelar): "))
        if choice == 0:
            return "Visualización de reportes cancelada."
        
        selected_file = report_files[choice - 1]
        print(f"\n--- Mostrando contenido de: {Colors.CYAN}{selected_file}{Colors.ENDC} ---\n")
        with open(selected_file, 'r', encoding='utf-8') as f:
            print(f.read())
        print("--- Fin del reporte ---")
        return f"Visualizado el reporte: {selected_file}"
    except (ValueError, IndexError):
        print(f"\n{Colors.RED}[ERROR] Selección no válida.{Colors.ENDC}")
        return "Intento de visualización de reportes: Selección no válida."

def mostrar_usuarios():
    """Muestra los usuarios actualmente logueados en el sistema."""
    mostrar_encabezado()
    users = psutil.users()
    log_output = ["Consulta de usuarios conectados:"]

    if not users:
        no_users_msg = "[INFO] No hay usuarios actualmente conectados."
        print(f"{Colors.YELLOW}{no_users_msg}{Colors.ENDC}")
        return no_users_msg

    print(f"\n{Colors.MAGENTA}--- Usuarios Conectados ---{Colors.ENDC}")
    header = f"{Colors.BOLD}{'Usuario':<20}{'Terminal':<15}{'Inició Sesión':<25}{Colors.ENDC}"
    print(header)
    print("-" * 65)
    for user in users:
        login_time = datetime.fromtimestamp(user.started).strftime("%Y-%m-%d %H:%M:%S")
        line = f"{user.name:<20}{user.terminal or 'N/A':<15}{login_time:<25}"
        print(line)
        log_output.append(line)

    # Bucle para consultar procesos de usuarios
    while True:
        print(f"\n{Colors.MAGENTA}Consulta de actividad por usuario:{Colors.ENDC}")
        username_input = input(f"  >> Escribe un nombre de usuario para ver sus procesos (o 'volver'): ").strip()
        if username_input.lower() == 'volver':
            break
        
        print(f"\n{Colors.MAGENTA}--- Procesos para '{username_input}' (ordenado por memoria) ---{Colors.ENDC}")
        proc_header = f"{Colors.BOLD}{'PID':<10}{'CPU%':<10}{'MEM(MB)':<12}{'Nombre':<40}{Colors.ENDC}"
        print(proc_header)
        print("-" * 75)
        
        user_procs = []
        for p in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_info']):
            try:
                # Hacemos la comparación más robusta:
                # 1. Ignoramos el dominio/nombre de equipo (ej: 'DESKTOP\')
                # 2. Comparamos en minúsculas.
                proc_username = p.info['username'].split('\\')[-1] if p.info['username'] else ''
                if proc_username and username_input.lower() in proc_username.lower():
                    user_procs.append(p)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Ordenar por uso de memoria descendente
        sorted_procs = sorted(user_procs, key=lambda p: p.info['memory_info'].rss if p.info['memory_info'] else 0, reverse=True)

        if not sorted_procs:
            print(f"\n{Colors.YELLOW}[INFO] No se encontraron procesos para el usuario '{username_input}'.{Colors.ENDC}")
            continue # Vuelve a pedir un nombre de usuario
        else:
            for p in sorted_procs:
                info = p.info
                mem_mb = info['memory_info'].rss / (1024 * 1024) if info['memory_info'] else 0
                cpu_percent = p.cpu_percent(interval=None)
                cpu_color = get_color_for_usage(cpu_percent)
                mem_color = get_color_for_mem_mb(mem_mb)
                name_short = (info['name'][:37] + '...') if len(info['name']) > 40 else info['name']
                line = f"{Colors.YELLOW}{info['pid']:<10}{Colors.ENDC}{cpu_color}{cpu_percent:<10.2f}{Colors.ENDC}{mem_color}{mem_mb:<12.2f}{Colors.ENDC}{name_short:<40}"
                print(line)

        # Bucle interactivo para consultar detalles de un PID de la lista
        while True:
            try:
                print(f"\n{Colors.MAGENTA}Acción sobre la lista de procesos:{Colors.ENDC}")
                sub_choice = input(f"  >> Escribe un PID para gestionar el proceso (o 'volver'): ").lower().strip()
                if sub_choice == 'volver':
                    break
                pid_to_check = int(sub_choice)
                details_log = gestionar_proceso(pid_to_check)
                log_output.append(details_log)
                break 
            except ValueError:
                print(f"\n{Colors.RED}[ERROR] Por favor, introduce un número de PID válido o la palabra 'volver'.{Colors.ENDC}")
    return "\n".join(log_output)

def mostrar_programas_instalados():
    """Lista los programas instalados (solo para Windows)."""
    if os.name != 'nt':
        msg = "[ERROR] Esta función solo está disponible en Windows."
        print(f"\n{Colors.RED}{msg}{Colors.ENDC}")
        return msg

    mostrar_encabezado()
    print(f"\n{Colors.MAGENTA}--- Inventario de Programas Instalados (puede tardar un momento) ---{Colors.ENDC}")
    program_list = []
    uninstall_paths = [
        r"Software\Microsoft\Windows\CurrentVersion\Uninstall",
        r"Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
    ]
    hives = [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]

    for hive in hives:
        for path in uninstall_paths:
            try:
                with winreg.OpenKey(hive, path) as key:
                    for i in range(winreg.QueryInfoKey(key)[0]):
                        sub_key_name = winreg.EnumKey(key, i)
                        with winreg.OpenKey(key, sub_key_name) as sub_key:
                            try:
                                display_name = winreg.QueryValueEx(sub_key, "DisplayName")[0]
                                publisher = winreg.QueryValueEx(sub_key, "Publisher")[0] if "Publisher" in [winreg.EnumValue(sub_key, j)[0] for j in range(winreg.QueryInfoKey(sub_key)[1])] else "N/A"
                                install_date_str = winreg.QueryValueEx(sub_key, "InstallDate")[0] if "InstallDate" in [winreg.EnumValue(sub_key, j)[0] for j in range(winreg.QueryInfoKey(sub_key)[1])] else "N/A"
                                
                                install_date = "N/A"
                                if install_date_str != "N/A":
                                    try:
                                        install_date = datetime.strptime(install_date_str, '%Y%m%d').strftime('%Y-%m-%d')
                                    except ValueError:
                                        install_date = "Formato inválido"

                                if display_name:
                                    program_list.append({
                                        "name": display_name,
                                        "publisher": publisher,
                                        "install_date": install_date
                                    })
                            except OSError:
                                pass
            except FileNotFoundError:
                pass
    
    # Eliminar duplicados basados en el nombre
    unique_programs = {prog['name'].lower(): prog for prog in program_list}.values()

    while True:
        print(f"\n{Colors.MAGENTA}Opciones de ordenamiento:{Colors.ENDC}")
        print("  [n]ombre: Ordena la lista alfabéticamente.")
        print("  [f]echa: Muestra primero los programas instalados más recientemente.")
        print(f"  [{Colors.YELLOW}v{Colors.ENDC}]olver: Regresa al menú principal.")
        sort_choice = input(f"  >> Elige una opción ([n], [f], [v]): ").lower().strip()
        
        if sort_choice == 'v':
            break
        elif sort_choice == 'n':
            sorted_list = sorted(unique_programs, key=lambda x: x['name'].lower())
        elif sort_choice == 'f':
            # Pone los 'N/A' al final
            sorted_list = sorted(unique_programs, key=lambda x: (x['install_date'] == 'N/A', x['install_date']), reverse=True)
        else:
            print(f"{Colors.RED}[ERROR] Opción no válida.{Colors.ENDC}")
            continue

        header = f"{Colors.BOLD}{'Programa':<60}{'Editor':<40}{'Instalado el':<15}{Colors.ENDC}"
        print("\n" + header)
        print("-" * 115)
        for program in sorted_list:
            name_short = (program['name'][:57] + '...') if len(program['name']) > 60 else program['name']
            publisher_short = (program['publisher'][:37] + '...') if len(program['publisher']) > 40 else program['publisher']
            print(f"{name_short:<60}{publisher_short:<40}{program['install_date']:<15}")

    log_output = f"Se listaron {len(unique_programs)} programas instalados."
    return log_output

def analizar_procesos():
    """Muestra una lista de procesos y permite ordenarlos por consumo."""
    log_output = ["Análisis de procesos en ejecución:"]
    
    while True:
        print(f"\n{Colors.MAGENTA}Opciones de análisis:{Colors.ENDC}")
        print("  [c]pu: Muestra los procesos que más CPU consumen.")
        print("  [m]emoria: Muestra los procesos que más RAM consumen.")
        sort_choice = input(f"  >> Ordenar por: [c]pu, [m]emoria, [n]ombre, o [v]olver: ").lower().strip()
        
        if sort_choice == 'v':
            break

        print("\nAnalizando procesos...")
        process_data = []
        # Primera pasada para inicializar cpu_percent
        for p in psutil.process_iter(['pid']):
            try:
                p.cpu_percent(interval=0.01)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        time.sleep(0.5) # Pausa para una lectura de CPU más precisa

        for p in psutil.process_iter(['pid', 'name', 'memory_percent']):
            try:
                with p.oneshot():
                    proc_info = {
                        'pid': p.pid,
                        'name': p.name(),
                        'cpu': p.cpu_percent(),
                        'mem': p.memory_percent()
                    }
                    process_data.append(proc_info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                # Si el proceso desaparece mientras lo leemos, simplemente lo ignoramos
                continue

        if sort_choice == 'c':
            sorted_list = sorted(process_data, key=lambda p: p['cpu'], reverse=True)
        elif sort_choice == 'm':
            sorted_list = sorted(process_data, key=lambda p: p['mem'], reverse=True)
        elif sort_choice == 'n':
            sorted_list = sorted(process_data, key=lambda p: p['name'].lower())
        else:
            print(f"{Colors.RED}[ERROR] Opción no válida.{Colors.ENDC}")
            continue

        header = f"{Colors.BOLD}{'PID':<10}{'CPU%':<10}{'MEM%':<10}{'Nombre':<40}{Colors.ENDC}"
        print("\n" + header)
        print("-" * 70)
        for p in sorted_list[:20]:
            print(f"{p['pid']:<10}{p['cpu']:<10.2f}{p['mem']:<10.2f}{p['name']:<40}")

    return "\n".join(log_output)

def ejecutar_apocalipsis():
    """Aniquila todos los procesos que coincidan con un nombre de ejecutable."""
    log_output = "Intento de ejecución de Apocalipsis."
    try:
        print(f"\n{Colors.BOLD}{Colors.RED}--- APOCALIPSIS ---{Colors.ENDC}")
        print("Esta herramienta aniquila todos los procesos que coincidan con un nombre.")
        proc_name = input(f">> Escribe el nombre del ejecutable a aniquilar (ej: vivaldi.exe): ").strip()
        if not proc_name:
            print(f"{Colors.YELLOW}[INFO] Operación cancelada.{Colors.ENDC}")
            return "Apocalipsis cancelado: no se ingresó nombre."

        print(f"\n{Colors.BOLD}{Colors.RED}ADVERTENCIA: Vas a aniquilar TODOS los procesos llamados '{proc_name}'.")
        print(f"Esta acción es irreversible.{Colors.ENDC}")
        confirm = input(f"¿Estás absolutamente seguro? (s/n): ").lower().strip()

        if confirm == 's':
            print(f"{Colors.BOLD}{Colors.RED}[ACTION] ¡Iniciando Apocalipsis! Aniquilando todos los procesos llamados '{proc_name}'...{Colors.ENDC}")
            log_output = f"Apocalipsis ejecutado sobre el nombre de proceso '{proc_name}'."
            # Usamos taskkill con /IM para matar todos los procesos con ese nombre.
            subprocess.run(['taskkill', '/F', '/IM', proc_name], capture_output=True, text=True)
            time.sleep(1)
            
            # Verificación
            still_running = any(p.name().lower() == proc_name.lower() for p in psutil.process_iter(['name']))
            if not still_running:
                print(f"{Colors.GREEN}[SUCCESS] Apocalipsis completado. No quedan instancias de '{proc_name}'.{Colors.ENDC}")
            else:
                print(f"{Colors.YELLOW}[WARNING] Apocalipsis fallido. Algunos procesos de '{proc_name}' son extremadamente resistentes o están protegidos por el sistema.{Colors.ENDC}")
        else:
            print(f"{Colors.YELLOW}[INFO] Apocalipsis cancelado.{Colors.ENDC}")
            log_output = "Apocalipsis cancelado por el usuario."
    except Exception as e:
        log_output = f"Error durante Apocalipsis: {e}"
    return log_output

def ejecutar_programa():
    """Busca y ejecuta un programa instalado con opciones avanzadas."""
    if os.name != 'nt':
        msg = "[ERROR] Esta función solo está disponible en Windows."
        print(f"\n{Colors.RED}{msg}{Colors.ENDC}")
        return msg

    log_output = "Intento de ejecución de programa."
    print(f"\n{Colors.MAGENTA}--- Ejecutor de Programas ---{Colors.ENDC}")
    search_term = input(">> Escribe parte del nombre del programa a buscar: ").lower().strip()
    if not search_term:
        return "Ejecución cancelada: no se ingresó término de búsqueda."

    matches = []
    uninstall_paths = [
        r"Software\Microsoft\Windows\CurrentVersion\Uninstall",
        r"Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
    ]
    hives = [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]

    for hive in hives:
        for path in uninstall_paths:
            try:
                with winreg.OpenKey(hive, path) as key:
                    for i in range(winreg.QueryInfoKey(key)[0]):
                        try:
                            with winreg.OpenKey(key, winreg.EnumKey(key, i)) as sub_key:
                                display_name = winreg.QueryValueEx(sub_key, "DisplayName")[0]
                                if search_term in display_name.lower():
                                    # Intentar obtener la ruta del ejecutable
                                    icon_path = winreg.QueryValueEx(sub_key, "DisplayIcon")[0].split(',')[0].replace('"', '')
                                    matches.append({"name": display_name, "path": icon_path})
                        except (OSError, FileNotFoundError):
                            continue
            except FileNotFoundError:
                pass
    
    if not matches:
        print(f"\n{Colors.YELLOW}[INFO] No se encontró ningún programa que coincida con '{search_term}'.{Colors.ENDC}")
        return f"Búsqueda de '{search_term}' no arrojó resultados."

    print("\nProgramas encontrados:")
    for i, match in enumerate(matches):
        print(f"  {Colors.BOLD}{i + 1}.{Colors.ENDC} {match['name']}")

    try:
        choice = int(input("\n>> Elige el número del programa a ejecutar (0 para cancelar): "))
        if choice == 0: return "Ejecución cancelada por el usuario."
        
        selected_program = matches[choice - 1]
        exe_path = selected_program['path']

        print(f"\n{Colors.MAGENTA}Opciones de ejecución para '{selected_program['name']}':{Colors.ENDC}")
        print("  [n]ormal: Abre el programa con su interfaz gráfica.")
        print("  [s]egundo plano: Intenta ejecutar sin ventana (no siempre funciona).")
        exec_choice = input(">> Elige una opción: ").lower().strip()

        flags = 0
        if exec_choice == 's':
            # DETACHED_PROCESS flag para Windows
            flags = 0x00000008
        
        subprocess.Popen([exe_path], creationflags=flags)
        log_output = f"Ejecutado '{selected_program['name']}' desde '{exe_path}'."
        print(f"\n{Colors.GREEN}[SUCCESS] Se ha enviado la orden de ejecución.{Colors.ENDC}")

    except (ValueError, IndexError):
        print(f"\n{Colors.RED}[ERROR] Selección no válida.{Colors.ENDC}")
        log_output = "Selección de programa para ejecutar no válida."
    except Exception as e:
        print(f"\n{Colors.RED}[ERROR] No se pudo ejecutar el programa: {e}{Colors.ENDC}")
        log_output = f"Fallo al ejecutar programa: {e}"
    
    return log_output

def modo_espia():
    """Permite encontrar y obtener información de ventanas abiertas."""
    log_output = "Iniciado Modo Espía."
    
    while True:
        mostrar_encabezado()
        print(f"\n{Colors.MAGENTA}--- Modo Espía / Explorador de Ventanas ---{Colors.ENDC}")
        
        # Obtener y filtrar ventanas para que sean relevantes
        all_windows = [w for w in pyautogui.getAllWindows() if w.title and w.visible]
        
        print("Ventanas abiertas actualmente:")
        for i, window in enumerate(all_windows):
            print(f"  {Colors.BOLD}{i + 1:2}.{Colors.ENDC} {window.title}")

        print(f"\n{Colors.MAGENTA}Acciones del Modo Espía:{Colors.ENDC}")
        print("  Escribe el número de una ventana para ver sus detalles.")
        choice = input("  >> Elige una ventana (o 'volver'): ").lower().strip()

        if choice == 'volver':
            break
        
        try:
            choice_index = int(choice) - 1
            if 0 <= choice_index < len(all_windows):
                target_window = all_windows[choice_index]
                
                print(f"\n{Colors.GREEN}[SUCCESS] Espiando ventana: '{target_window.title}'{Colors.ENDC}")
                
                print(f"\n{Colors.MAGENTA}--- Ficha Técnica de la Ventana ---{Colors.ENDC}")
                print(f"  {Colors.BOLD}Título completo:{Colors.ENDC} {target_window.title}")
                print(f"  {Colors.BOLD}Tamaño:{Colors.ENDC} {target_window.width}x{target_window.height} píxeles")
                print(f"  {Colors.BOLD}Posición (esquina sup-izq):{Colors.ENDC} X={target_window.left}, Y={target_window.top}")
                print(f"  {Colors.BOLD}¿Está activa?:{Colors.ENDC} {'Sí' if target_window.isActive else 'No'}")
                print(f"  {Colors.BOLD}¿Está minimizada?:{Colors.ENDC} {'Sí' if target_window.isMinimized else 'No'}")

                log_output += f"\n  └─ Espiada la ventana '{target_window.title}'."
                input("\n--- Presiona Enter para volver al explorador de ventanas ---")
            else:
                print(f"\n{Colors.RED}[ERROR] Número fuera de rango.{Colors.ENDC}")
                time.sleep(2)

        except ValueError:
            print(f"\n{Colors.RED}[ERROR] Por favor, introduce un número válido.{Colors.ENDC}")
            time.sleep(2)

    return log_output

def gestionar_proceso(pid):
    """Muestra información detallada de un proceso por su PID y devuelve un log."""
    try:
        p = psutil.Process(pid)
        # Usar 'with p.oneshot()' es más eficiente para obtener múltiples datos del mismo proceso
        with p.oneshot():
            print(f"\n{Colors.MAGENTA}--- Detalles del Proceso (PID: {pid}) ---{Colors.ENDC}")
            
            proc_name = p.name()
            if proc_name.lower() in PROCESOS_CONOCIDOS:
                print(f"{Colors.CYAN}  [i] Descripción de '{proc_name}': {PROCESOS_CONOCIDOS[proc_name.lower()]}{Colors.ENDC}")

            # Información básica
            print(f"{Colors.BOLD}Nombre:{Colors.ENDC} {p.name()}")
            print(f"{Colors.BOLD}Ruta:{Colors.ENDC} {p.exe()}")
            print(f"{Colors.BOLD}Usuario:{Colors.ENDC} {p.username()}")
            
            # Uso de recursos
            cpu_usage = p.cpu_percent(interval=0.1)
            mem_usage_mb = p.memory_info().rss / (1024 * 1024)
            print(f"{Colors.BOLD}Uso de CPU:{Colors.ENDC} {get_color_for_usage(cpu_usage)}{cpu_usage:.2f}%{Colors.ENDC}")
            print(f"{Colors.BOLD}Uso de Memoria (RSS):{Colors.ENDC} {mem_usage_mb:.2f} MB")

            # Información adicional
            create_time = datetime.fromtimestamp(p.create_time()).strftime("%Y-%m-%d %H:%M:%S")
            print(f"{Colors.BOLD}Iniciado el:{Colors.ENDC} {create_time}")
            print(f"{Colors.BOLD}Estado:{Colors.ENDC} {p.status()}")
            
            log_output = [f"Consulta de detalles para PID {pid}: Nombre={p.name()}, Usuario={p.username()}, CPU={cpu_usage:.2f}%, Mem={mem_usage_mb:.2f}MB"]

        # Bucle de acciones para el proceso actual
        while True:
            status = p.status()
            print(f"\n{Colors.MAGENTA}--- Acciones para PID {pid} ({p.name()}) ---{Colors.ENDC}")
            
            # Menú de acciones dinámico
            if status == psutil.STATUS_RUNNING:
                print(f"  [{Colors.YELLOW}p{Colors.ENDC}]ausar: Congela el proceso temporalmente.")
            elif status == psutil.STATUS_STOPPED:
                print(f"  [{Colors.GREEN}r{Colors.ENDC}]eanudar: Vuelve a activar un proceso pausado.")
            
            print(f"  [{Colors.RED}t{Colors.ENDC}]erminar: Pide amablemente al proceso que se cierre.")
            print(f"  [{Colors.BOLD}{Colors.RED}k{Colors.ENDC}]ill: Fuerza el cierre inmediato de este proceso.")
            print(f"  [{Colors.BOLD}{Colors.RED}kt{Colors.ENDC}]illTrueno: Mata este proceso y todos los que haya creado.")
            print(f"  [{Colors.GREEN}a{Colors.ENDC}]brir de nuevo: Intenta reiniciar el programa desde su ruta.")
            print(f"  [{Colors.CYAN}v{Colors.ENDC}]olver: Regresa a la pantalla anterior.")

            accion = input(">> Elige una acción: ").lower().strip()

            if accion == 'v':
                return "\n".join(log_output)
            
            elif accion == 'p' and status == psutil.STATUS_RUNNING:
                p.suspend()
                print(f"{Colors.YELLOW}[ACTION] Proceso {pid} pausado.{Colors.ENDC}")
                log_output.append(f"  └─ ACCIÓN: Proceso {pid} pausado.")
            
            elif accion == 'r' and status == psutil.STATUS_STOPPED:
                p.resume()
                print(f"{Colors.GREEN}[ACTION] Proceso {pid} reanudado.{Colors.ENDC}")
                log_output.append(f"  └─ ACCIÓN: Proceso {pid} reanudado.")
            
            elif accion == 't':
                p.terminate()
                print(f"{Colors.RED}[ACTION] Señal de terminación enviada a {pid}.{Colors.ENDC}")
                log_output.append(f"  └─ ACCIÓN: Señal de terminación enviada a {pid}.")
                time.sleep(1) # Dar tiempo al proceso para cerrarse
                if not p.is_running():
                    print(f"{Colors.GREEN}[SUCCESS] El proceso se ha cerrado.{Colors.ENDC}")
                    return "\n".join(log_output) # Salir del menú de acciones
            
            elif accion == 'k':
                p.kill()
                print(f"{Colors.BOLD}{Colors.RED}[ACTION] Proceso {pid} forzado a terminar (kill).{Colors.ENDC}")
                log_output.append(f"  └─ ACCIÓN: Proceso {pid} forzado a terminar (kill).")
                time.sleep(1)
                if not p.is_running():
                    print(f"{Colors.GREEN}[SUCCESS] El proceso ha sido eliminado.{Colors.ENDC}")
                    return "\n".join(log_output) # Salir del menú de acciones
            
            elif accion == 'kt':
                print(f"{Colors.BOLD}{Colors.RED}[ACTION] ¡Desatando KillTrueno sobre PID {pid} y su árbol de procesos!{Colors.ENDC}")
                log_output.append(f"  └─ ACCIÓN: KillTrueno ejecutado sobre {pid} ({p.name()}).")
                # Usamos taskkill con /T para matar el árbol de procesos y /F para forzarlo.
                subprocess.run(['taskkill', '/PID', str(pid), '/T', '/F'], capture_output=True, text=True)
                time.sleep(1)
                if not psutil.pid_exists(pid):
                    print(f"{Colors.GREEN}[SUCCESS] El árbol de procesos ha sido fulminado.{Colors.ENDC}")
                    return "\n".join(log_output)

            
            elif accion == 'a':
                exe_path = p.exe()
                subprocess.Popen(exe_path)
                print(f"{Colors.GREEN}[ACTION] Intentando reiniciar el proceso desde: {exe_path}{Colors.ENDC}")
                log_output.append(f"  └─ ACCIÓN: Intento de reinicio para {p.name()}.")
            
            else:
                print(f"{Colors.RED}[ERROR] Acción no válida o no aplicable al estado actual.{Colors.ENDC}")

    except psutil.NoSuchProcess:
        print(f"\n{Colors.RED}[ERROR] El proceso con PID {pid} ya no existe.{Colors.ENDC}")
        return f"Intento de gestión para PID {pid}: Proceso no encontrado."
    except psutil.AccessDenied:
        print(f"\n{Colors.RED}[ERROR] Acceso denegado. 'El Cerebro' necesita permisos de administrador para gestionar este proceso.{Colors.ENDC}")
        return f"Intento de gestión para PID {pid}: Acceso denegado."
    except ValueError:
        print(f"\n{Colors.RED}[ERROR] PID no válido.{Colors.ENDC}")
        return f"Intento de gestión para PID {pid}: PID no válido."

def mostrar_puertos_abiertos():
    """Muestra los puertos de red en estado de 'escucha'."""
    listening_conns = []
    connections = psutil.net_connections(kind='inet')
    for conn in connections:
        if conn.status == 'LISTEN':
            try:
                proc = psutil.Process(conn.pid)
                proc_name = proc.name()
                listening_conns.append({
                    'pid': conn.pid,
                    'name': proc_name,
                    'addr': f"{conn.laddr.ip}:{conn.laddr.port}"
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

    # Ordenar la lista por nombre de programa
    listening_conns.sort(key=lambda x: x['name'].lower())

    print(f"\n{Colors.MAGENTA}--- Puertos Abiertos (Escuchando) ---{Colors.ENDC}")
    header = f"{Colors.BOLD}{'PID':<10}{'Programa':<28}{'Dirección Local':<25}{Colors.ENDC}"
    print(header)
    print("-" * 65) # Longitud fija para que la línea no cambie por los colores
    log_output = "Consulta de puertos abiertos:\n"

    for conn in listening_conns:
        # Acortar nombres de programa largos para mantener la alineación
        proc_name_short = (conn['name'][:25] + '...') if len(conn['name']) > 28 else conn['name']
        line_colored = f"{Colors.YELLOW}{conn['pid']:<10}{Colors.ENDC}{proc_name_short:<28}{Colors.GREEN}{conn['addr']:<25}{Colors.ENDC}"
        line_log = f"{conn['pid']:<10}{conn['name']:<28}{conn['addr']}"
        print(line_colored)
        log_output += line_log + "\n"

    # Bucle interactivo para consultar detalles
    while True:
        try:
            print(f"\n{Colors.MAGENTA}Acción sobre la lista de puertos:{Colors.ENDC}")
            print("  Escribe el PID de un proceso para ver sus detalles y gestionarlo.")
            sub_choice = input(f"  >> Elige un PID (o 'volver'): ").lower().strip()
            if sub_choice == 'volver':
                break
            pid_to_check = int(sub_choice)
            details_log = gestionar_proceso(pid_to_check)
            log_output += "\n" + details_log
        except ValueError:
            print(f"\n{Colors.RED}[ERROR] Por favor, introduce un número de PID válido o la palabra 'volver'.{Colors.ENDC}")
    return log_output

def herramienta_ping():
    """Realiza un ping a un host especificado por el usuario."""
    log_output = "Iniciada herramienta de Ping."
    print(f"\n{Colors.MAGENTA}--- Herramienta de Ping ---{Colors.ENDC}")
    host = input(">> Introduce la IP o el dominio para hacer ping (ej: google.com o 8.8.8.8): ").strip()
    if not host:
        return "Ping cancelado: no se ingresó host."
    
    print(f"\n{Colors.MAGENTA}Elige el tamaño del paquete de datos:{Colors.ENDC}")
    print("  1. 32 bytes (Rápido): Comprobación estándar de latencia y conectividad.")
    print("  2. 64 bytes (Común): Prueba de conectividad general, un poco más exigente.")
    print("  3. 1024 bytes (1KB - Mediano): Ayuda a detectar problemas con paquetes más grandes.")
    print("  4. 4096 bytes (4KB - Grande): Simula más carga y puede revelar problemas de MTU (fragmentación).")
    
    size_choice = input(">> Elige una opción (o presiona Enter para 32 bytes por defecto): ").strip()
    
    packet_size = 32 # Valor por defecto
    if size_choice == '2':
        packet_size = 64
    elif size_choice == '3':
        packet_size = 1024
    elif size_choice == '4':
        packet_size = 4096

    print(f"\n{Colors.YELLOW}Haciendo ping a {host} con {packet_size} bytes...{Colors.ENDC}\n")
    log_output += f"\nPing a {host} con {packet_size} bytes:\n"
    
    # El comando -n 4 es para Windows. En Linux/macOS sería -c 4.
    # El flag -l establece el tamaño del buffer (paquete).
    command = ['ping', '-n', '4', '-l', str(packet_size), host]
    result = subprocess.run(command, capture_output=True, text=True, encoding='latin-1')
    
    print(result.stdout)
    log_output += result.stdout
    return log_output

def analizar_redes_wifi():
    """Escanea y muestra información detallada de las redes WiFi disponibles (solo Windows)."""
    if os.name != 'nt':
        msg = "[ERROR] Esta función solo está disponible en Windows."
        print(f"\n{Colors.RED}{msg}{Colors.ENDC}")
        return msg

    log_output = "Iniciada herramienta de análisis WiFi."
    print(f"\n{Colors.MAGENTA}--- Analizador de Redes WiFi ---{Colors.ENDC}")
    print(f"{Colors.YELLOW}Escaneando redes a tu alrededor... (esto puede tardar unos segundos){Colors.ENDC}")

    try:
        # Ejecutamos el comando de netsh para obtener un informe detallado de las redes
        result = subprocess.run(
            ['netsh', 'wlan', 'show', 'networks', 'mode=Bssid'],
            capture_output=True, text=True, encoding='latin-1', check=True
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        msg = "[ERROR] No se pudo ejecutar 'netsh'. Asegúrate de que el servicio WLAN está activo."
        print(f"\n{Colors.RED}{msg}{Colors.ENDC}")
        return msg

    networks = []
    current_network = {}
    
    # Analizamos la salida del comando línea por línea
    for line in result.stdout.splitlines():
        if "SSID" in line and ":" in line:
            if current_network.get("SSID"):
                networks.append(current_network)
            ssid = line.split(":", 1)[1].strip()
            current_network = {"SSID": ssid}
        elif "Autenticaci" in line:
            current_network["Autenticación"] = line.split(":", 1)[1].strip()
        elif "Cifrado" in line:
            current_network["Cifrado"] = line.split(":", 1)[1].strip()
        elif "Se¤al" in line or "Señal" in line: # Maneja problemas de codificación
            signal_percent = re.search(r'(\d+)%', line)
            if signal_percent:
                current_network["Señal"] = int(signal_percent.group(1))
        elif "Canal" in line:
            current_network["Canal"] = line.split(":", 1)[1].strip()

    if current_network.get("SSID"):
        networks.append(current_network)

    # Ordenar por la señal más fuerte
    sorted_networks = sorted(networks, key=lambda x: x.get("Señal", 0), reverse=True)

    print(f"\n{Colors.BOLD}{'SSID':<30}{'Señal':<10}{'Canal':<8}{'Autenticación':<20}{'Cifrado':<15}{Colors.ENDC}")
    print("-" * 85)
    for net in sorted_networks:
        signal = net.get("Señal", 0)
        color = get_color_for_usage(signal)
        print(f"{net.get('SSID', 'N/A'):<30}{color}{str(signal)+'%':<10}{Colors.ENDC}{net.get('Canal', 'N/A'):<8}{net.get('Autenticación', 'N/A'):<20}{net.get('Cifrado', 'N/A'):<15}")

    return f"Análisis WiFi completado. Se encontraron {len(sorted_networks)} redes."

def depredador_silencioso():
    """Busca cámaras públicas de forma sigilosa y permite búsquedas geográficas."""
    log_output = "Iniciada herramienta de búsqueda de cámaras."
    print(f"\n{Colors.MAGENTA}--- Depredador Silencioso (Buscador OSINT) ---{Colors.ENDC}")
    print("Esta herramienta realiza búsquedas sigilosas para encontrar cámaras públicas.")

    dorks = {
        "1": {"dork": 'inurl:"view/index.shtml"', "desc": "Cámaras Axis antiguas"},
        "2": {"dork": 'intitle:"Live View / - AXIS"', "desc": "Cámaras de red Axis"},
        "3": {"dork": 'inurl:viewerframe?mode=motion', "desc": "Cámaras Panasonic"},
        "4": {"dork": 'intitle:"webcam 7" inurl:8080', "desc": "Software 'Webcam 7'"},
        "5": {"dork": 'intitle:"Live Stream" inurl:LvAppl', "desc": "Cámaras con 'Live Stream'"},
        "6": {"dork": 'inurl:/cgi-bin/guest/Video.cgi', "desc": "Cámaras D-Link"},
        "7": {"dork": 'intitle:"SONY IPELA" inurl:camera', "desc": "Cámaras SONY IPELA"},
    }

    while True:
        print(f"\n{Colors.MAGENTA}Elige un tipo de 'Dork' para la búsqueda:{Colors.ENDC}")
        for key, value in dorks.items():
            print(f"  {Colors.BOLD}{key}.{Colors.ENDC} {value['desc']:<25} ({value['dork']})")
        print(f"  {Colors.YELLOW}{Colors.BOLD}0.{Colors.ENDC} Volver al menú")

        choice = input("\n>> Elige una opción: ").strip()
        if choice == '0':
            break
        
        if choice in dorks:
            dork = dorks[choice]['dork']
            location = input(">> (Opcional) Escribe una ubicación para refinar la búsqueda (ej: mar del plata): ").strip()
            query = f'{dork} "{location}"' if location else dork

            print(f"\n{Colors.YELLOW}Depredador en modo caza... Buscando en Brave: {query}{Colors.ENDC}")
            
            try:
                # Usamos Brave Search, que es menos propenso a bloquear y tiene buenos resultados.
                search_url = f"https://search.brave.com/search?q={quote_plus(query)}"
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'}
                
                response = requests.get(search_url, headers=headers)
                response.raise_for_status()

                soup = BeautifulSoup(response.text, 'html.parser')
                # La estructura de resultados de Brave
                results = soup.select("div.snippet[data-pos]")
                
                if not results:
                    print(f"\n{Colors.YELLOW}[INFO] No se encontraron resultados directos. La caza fue limpia o el motor de búsqueda nos bloqueó.{Colors.ENDC}")
                    continue

                print(f"\n{Colors.GREEN}[SUCCESS] ¡Objetivos encontrados!{Colors.ENDC}")
                found_links = []
                for i, res in enumerate(results):
                    link_tag = res.find("a")
                    if link_tag and link_tag.has_attr('href'):
                        title = res.find("span", class_="snippet-title").get_text(strip=True)
                        link = link_tag['href']
                        found_links.append(link)
                        print(f"  {Colors.BOLD}{i+1}.{Colors.ENDC} {title} - {Colors.CYAN}{link}{Colors.ENDC}")
                
                link_choice = input("\n>> Elige un número para abrir en el navegador (0 para volver): ").strip()
                if link_choice.isdigit() and 0 < int(link_choice) <= len(found_links):
                    webbrowser.open(found_links[int(link_choice) - 1])

            except requests.exceptions.RequestException as e:
                print(f"\n{Colors.RED}[ERROR] Fallo en la conexión: {e}{Colors.ENDC}")
                if "429" in str(e):
                    print(f"{Colors.YELLOW}[INFO] El motor de búsqueda nos ha bloqueado temporalmente. Esperando 10 segundos...{Colors.ENDC}")
                    time.sleep(10)

        else:
            print(f"\n{Colors.RED}[ERROR] Opción no válida.{Colors.ENDC}")

    return log_output

def cazador_shodan():
    """Busca dispositivos en Shodan usando su API."""
    log_output = "Iniciada herramienta de caza Shodan."
    print(f"\n{Colors.MAGENTA}--- Cazador Shodan ---{Colors.ENDC}")
    
    SHODAN_API_KEY = os.getenv("SHODAN_API_KEY")
    if not SHODAN_API_KEY or SHODAN_API_KEY == "AQUÍ_PEGAS_LA_CLAVE_QUE_COPIASTE_DE_SHODAN":
        print(f"\n{Colors.RED}[ERROR] No se encontró una API Key de Shodan en el archivo .env.{Colors.ENDC}")
        print("  1. Regístrate gratis en https://account.shodan.io/register")
        print("  2. Copia tu API Key y pégala en la variable SHODAN_API_KEY dentro de tu archivo .env")
        return "Caza cancelada: Falta API Key de Shodan."

    api = shodan.Shodan(SHODAN_API_KEY)

    try:
        print("\nInformación de la cuenta:")
        info = api.info()
        query_credits = info.get('query_credits', 0)
        scan_credits = info.get('scan_credits', 0)
        print(f"  Créditos de Búsqueda (API): {Colors.RED if query_credits == 0 else Colors.GREEN}{query_credits}{Colors.ENDC} (Necesitas créditos para búsquedas generales)")
        print(f"  Créditos de Escaneo (API): {Colors.GREEN}{scan_credits}{Colors.ENDC}")

        while True:
            target_input = input("\n>> Escribe la IP del objetivo a investigar en Shodan (o 'volver'): ").strip()
            if target_input.lower() == 'volver':
                break
            if not target_input:
                continue

            # ¡NUEVA LÓGICA INTELIGENTE!
            # Limpiamos la entrada para obtener solo la IP, descartando el puerto si existe.
            target_ip = target_input.split(':')[0]

            print(f"\n{Colors.YELLOW}Obteniendo ficha de inteligencia para {target_ip}...{Colors.ENDC}")
            host_details = api.host(target_ip)
            
            print(f"\n{Colors.BOLD}--- Ficha de Inteligencia Shodan: {target_ip} ---{Colors.ENDC}")
            print(f"  - {Colors.BOLD}País/Ciudad:{Colors.ENDC} {host_details.get('country_name', 'N/A')}, {host_details.get('city', 'N/A')}")
            print(f"  - {Colors.BOLD}Hostnames:{Colors.ENDC} {', '.join(host_details.get('hostnames', ['N/A']))}")
            print(f"  - {Colors.BOLD}Puertos Abiertos:{Colors.ENDC} {Colors.GREEN}{', '.join(map(str, host_details.get('ports', ['N/A'])))}{Colors.ENDC}")
            
            if host_details.get('vulns'):
                print(f"  - {Colors.BOLD}Vulnerabilidades Conocidas (CVEs):{Colors.ENDC} {Colors.RED}{', '.join(host_details.get('vulns'))}{Colors.ENDC}")

    except shodan.APIError as e:
        print(f"\n{Colors.RED}[ERROR] Fallo en la API de Shodan: {e}{Colors.ENDC}")

    return "Caza en Shodan finalizada."

def gestionar_stock():
    """Permite al usuario ver, añadir y gestionar un inventario de materiales."""
    log_output = "Iniciada gestión de Stock."
    stock_file = "stock.json"
    
    # Cargar stock existente o crear uno nuevo
    if os.path.exists(stock_file):
        with open(stock_file, 'r', encoding='utf-8') as f:
            stock = json.load(f)
    else:
        stock = []

    while True:
        mostrar_encabezado()
        print(f"\n{Colors.MAGENTA}--- Gestión de Stock de Materiales ---{Colors.ENDC}")
        print("1. Ver inventario actual")
        print("2. Añadir nuevo material al inventario")
        print(f"{Colors.YELLOW}0. Volver al menú principal{Colors.ENDC}")
        
        choice = input("\n>> Elige una opción: ").strip()

        if choice == '1':
            print(f"\n{Colors.BOLD}--- Inventario Actual ---{Colors.ENDC}")
            if not stock:
                print(f"{Colors.YELLOW}[INFO] El inventario está vacío.{Colors.ENDC}")
            else:
                print(f"{'#':<4}{'Nombre':<30}{'Precio Costo':<20}{'Precio Venta':<20}")
                print("-" * 75)
                for i, item in enumerate(stock):
                    costo_f, _ = format_and_describe_number(item['precio_costo'])
                    venta_f, _ = format_and_describe_number(item['precio_venta'])
                    print(f"{i+1:<4}{item['nombre']:<30}{f'$ {costo_f}':<20}{f'$ {venta_f}':<20}")
            input("\n--- Presiona Enter para continuar ---")

        elif choice == '2':
            try:
                print(f"\n{Colors.CYAN}--- Añadir Nuevo Material ---{Colors.ENDC}")
                nombre = input(">> Nombre del material: ").strip()
                if not nombre or nombre.isdigit():
                    print(f"{Colors.RED}[ERROR] El nombre no puede estar vacío o ser solo números.{Colors.ENDC}")
                    continue
                
                precio_costo = float(input(f">> Precio de COSTO para '{nombre}': $ "))
                precio_venta = float(input(f">> Precio de VENTA para '{nombre}': $ "))
                
                stock.append({'nombre': nombre, 'precio_costo': precio_costo, 'precio_venta': precio_venta})
                with open(stock_file, 'w', encoding='utf-8') as f:
                    json.dump(stock, f, indent=4)
                print(f"\n{Colors.GREEN}[SUCCESS] '{nombre}' añadido al inventario.{Colors.ENDC}")
            except ValueError:
                print(f"\n{Colors.RED}[ERROR] Valor no válido. Introduce solo números para los precios.{Colors.ENDC}")
            time.sleep(2)

        elif choice == '0':
            break
    return log_output

def editar_presupuesto(file_path):
    """Carga un presupuesto desde un archivo, permite editarlo y lo vuelve a guardar."""
    data_dir = os.path.join("presupuestos", ".data")
    filename = os.path.basename(file_path)
    json_path = os.path.join(data_dir, filename.replace('.txt', '.json'))

    if not os.path.exists(json_path):
        print(f"\n{Colors.RED}[ERROR] No se encontró el archivo de datos para editar este presupuesto.{Colors.ENDC}")
        time.sleep(2)
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Extraemos los datos existentes
    project_title = data['project_title']
    items_costo = data['items_costo']
    margen_ganancia_pct = data['margen_ganancia_pct']
    base = data.get('base', 0) # Usamos .get para compatibilidad con presupuestos antiguos
    altura = data.get('altura', 0)
    costo_instalacion = data['costo_instalacion']

    while True:
        mostrar_encabezado()
        print(f"\n{Colors.MAGENTA}--- Editando Presupuesto: {project_title} ---{Colors.ENDC}")
        print("1. Ver/Editar items de fabricación")
        print("2. Editar margen de ganancia")
        print("3. Editar superficie (m²)")
        print("4. Editar costo de instalación")
        print(f"{Colors.GREEN}5. Guardar cambios y salir{Colors.ENDC}")
        print(f"{Colors.YELLOW}0. Cancelar y descartar cambios{Colors.ENDC}")

        choice = input("\n>> ¿Qué deseas modificar?: ").strip()

        if choice == '1': # Editar items
            while True:
                print("\n--- Items Actuales ---")
                if not items_costo: print("No hay items.")
                for i, item in enumerate(items_costo):
                    print(f"  {i+1}. {item['nombre']}: $ {item['costo']:.2f}")
                
                print("\nOpciones: [a]ñadir, [e]liminar #, [v]olver")
                item_choice = input(">> ").strip().lower()

                if item_choice == 'v': break
                elif item_choice == 'a':
                    nombre = input("   - Nombre del nuevo item: ").strip()
                    costo = float(input(f"   - Costo para '{nombre}': $ ").strip())
                    items_costo.append({'nombre': nombre, 'costo': costo})
                elif item_choice.startswith('e'):
                    try:
                        idx_to_del = int(item_choice.split()[-1]) - 1
                        if 0 <= idx_to_del < len(items_costo):
                            removed = items_costo.pop(idx_to_del)
                            print(f"{Colors.YELLOW}[INFO] Item '{removed['nombre']}' eliminado.{Colors.ENDC}")
                        else: print(f"{Colors.RED}[ERROR] Número de item no válido.{Colors.ENDC}")
                    except (ValueError, IndexError):
                        print(f"{Colors.RED}[ERROR] Comando no válido. Usa 'e' seguido de un número (ej: e 2).{Colors.ENDC}")

        elif choice == '2': # Editar margen
            print(f"Margen de ganancia actual: {margen_ganancia_pct}%")
            try:
                nuevo_margen = input(">> Introduce el nuevo porcentaje de ganancia: ").strip()
                margen_ganancia_pct = float(nuevo_margen)
                print(f"{Colors.GREEN}[SUCCESS] Margen actualizado a {margen_ganancia_pct}%.{Colors.ENDC}")
            except ValueError:
                print(f"{Colors.RED}[ERROR] Valor no válido.{Colors.ENDC}")
            time.sleep(1.5)

        elif choice == '3': # Editar superficie
            print(f"Superficie actual: {base} x {altura} = {base*altura:.2f} m²")
            try:
                nueva_base = input(f">> Introduce la nueva BASE (actual: {base}): ").strip()
                nueva_altura = input(f">> Introduce la nueva ALTURA (actual: {altura}): ").strip()
                base = float(nueva_base)
                altura = float(nueva_altura)
                print(f"{Colors.GREEN}[SUCCESS] Superficie actualizada a {base} x {altura} = {base*altura:.2f} m².{Colors.ENDC}")
            except ValueError:
                print(f"{Colors.RED}[ERROR] Valores no válidos.{Colors.ENDC}")
            time.sleep(1.5)

        elif choice == '4': # Editar instalación
            print(f"Costo de instalación actual: $ {costo_instalacion:.2f}")
            try:
                nuevo_costo = input(">> Introduce el nuevo costo de instalación: $ ").strip()
                costo_instalacion = float(nuevo_costo)
                print(f"{Colors.GREEN}[SUCCESS] Costo de instalación actualizado a $ {costo_instalacion:.2f}.{Colors.ENDC}")
            except ValueError:
                print(f"{Colors.RED}[ERROR] Valor no válido.{Colors.ENDC}")
            time.sleep(1.5)

        elif choice == '5': # Guardar
            # Volvemos a ejecutar la lógica de cálculo y guardado con los datos actualizados
            costo_fabricacion_total = sum(item['costo'] for item in items_costo)
            ganancia_fabricacion = costo_fabricacion_total * (margen_ganancia_pct / 100)
            subtotal_producto = costo_fabricacion_total + ganancia_fabricacion
            presupuesto_final = subtotal_producto + costo_instalacion
            
            # Generar el texto del reporte
            budget_output = generar_texto_presupuesto(project_title, items_costo, costo_fabricacion_total, margen_ganancia_pct, ganancia_fabricacion, costo_instalacion, presupuesto_final, ganancia_fabricacion)
            
            # Guardar el .txt
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("\n".join(budget_output))
            
            # Guardar el .json actualizado
            new_data = {
                'project_title': project_title, 'items_costo': items_costo,
                'margen_ganancia_pct': margen_ganancia_pct, 'costo_instalacion': costo_instalacion,
                'base': base, 'altura': altura
            }
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(new_data, f, indent=4)

            print(f"\n{Colors.GREEN}[SUCCESS] Presupuesto '{project_title}' actualizado y guardado.{Colors.ENDC}")
            time.sleep(2)
            return # Salimos de la función de edición

        elif choice == '0': # Cancelar
            if input("¿Descartar todos los cambios? (s/n): ").lower() == 's':
                print(f"{Colors.YELLOW}[INFO] Edición cancelada. No se guardaron los cambios.{Colors.ENDC}")
                time.sleep(2)
                return

def visor_presupuestos():
    """Busca y muestra presupuestos guardados en la carpeta 'presupuestos'."""
    log_output = "Iniciado Visor de Presupuestos (Ojo de Halcón)."
    budget_dir = "presupuestos"
    if not os.path.exists(budget_dir):
        print(f"\n{Colors.YELLOW}[INFO] La carpeta '{budget_dir}' no existe. Aún no se han guardado presupuestos.{Colors.ENDC}")
        return "Intento de visualización de presupuestos: No se encontraron."

    while True:
        mostrar_encabezado()
        print(f"\n{Colors.MAGENTA}--- Ojo de Halcón (Visor de Presupuestos) ---{Colors.ENDC}")
        
        search_term = input(">> Busca por palabra clave en el título del presupuesto (o 'todos'/'volver'): ").lower().strip()

        if search_term == 'volver':
            break
        
        all_files = [f for f in os.listdir(budget_dir) if f.endswith('.txt')]
        
        if search_term == 'todos':
            found_files = all_files
        else:
            found_files = [f for f in all_files if search_term in f.lower()]

        if not found_files:
            print(f"\n{Colors.YELLOW}[INFO] No se encontraron presupuestos que coincidan con '{search_term}'.{Colors.ENDC}")
            time.sleep(2)
            continue

        print("\nPresupuestos encontrados:")
        for i, filename in enumerate(found_files):
            print(f"  {Colors.BOLD}{i + 1}.{Colors.ENDC} {filename.replace('.txt', '')}")

        try:
            choice_input = input("\n>> Elige un # para ver, o usa 'e #' para editar, 'b #' para borrar (0 para buscar): ").strip().lower()
            if choice_input == '0': continue

            parts = choice_input.split()
            action = 'ver'
            if len(parts) > 1:
                if parts[0] == 'e': action = 'editar'
                elif parts[0] == 'b': action = 'borrar'
            
            file_idx = int(parts[-1]) - 1
            selected_filename = found_files[file_idx]
            full_path = os.path.join(budget_dir, selected_filename)

            if action == 'ver':
                print(f"\n--- Mostrando contenido de: {Colors.CYAN}{selected_filename}{Colors.ENDC} ---\n")
                # Leemos el contenido y le aplicamos colores para que se vea bien
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Re-aplicamos colores para la visualización
                    content = content.replace("--- PRESUPUESTO:", f"{Colors.BOLD}{Colors.GREEN}--- PRESUPUESTO:")
                    content = content.replace("A) Desglose de Fabricación:", f"{Colors.BOLD}A) Desglose de Fabricación:{Colors.ENDC}")
                    content = content.replace("B) Resumen Financiero:", f"{Colors.BOLD}B) Resumen Financiero:{Colors.ENDC}")
                    content = content.replace("Costo de Fabricación:", f"Costo de Fabricación:{Colors.YELLOW}")
                    content = content.replace("PRECIO VENTA AL CLIENTE:", f"{Colors.BOLD}PRECIO VENTA AL CLIENTE:{Colors.ENDC}{Colors.GREEN}{Colors.BOLD}")
                    content = content.replace("GANANCIA NETA DEL PROYECTO:", f"{Colors.BOLD}GANANCIA NETA DEL PROYECTO:{Colors.ENDC}{Colors.CYAN}{Colors.BOLD}")
                    # Añadimos el ENDC al final de las líneas con color
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if Colors.YELLOW in line or Colors.GREEN in line or Colors.CYAN in line:
                            lines[i] += Colors.ENDC
                    print("\n".join(lines))
                input("\n--- Presiona Enter para continuar ---")
            
            elif action == 'editar':
                editar_presupuesto(full_path)

            elif action == 'borrar':
                if input(f"{Colors.RED}¿Seguro que quieres borrar permanentemente '{selected_filename}'? (s/n): {Colors.ENDC}").lower() == 's':
                    os.remove(full_path)
                    # Borrar también el archivo de datos .json
                    json_path = os.path.join(budget_dir, ".data", selected_filename.replace('.txt', '.json'))
                    if os.path.exists(json_path): os.remove(json_path)
                    print(f"{Colors.GREEN}[SUCCESS] Presupuesto borrado.{Colors.ENDC}")
                    time.sleep(2)

        except (ValueError, IndexError):
            print(f"\n{Colors.RED}[ERROR] Selección no válida.{Colors.ENDC}")
            time.sleep(2)

    return log_output

def buscar_item_stock():
    """Muestra el stock y permite al usuario seleccionar un item."""
    stock_file = "stock.json"
    if not os.path.exists(stock_file):
        print(f"{Colors.YELLOW}[INFO] No hay archivo de stock. Debes añadir items desde la opción 18.{Colors.ENDC}")
        return None

    with open(stock_file, 'r', encoding='utf-8') as f:
        stock = json.load(f)

    if not stock:
        print(f"{Colors.YELLOW}[INFO] El stock está vacío.{Colors.ENDC}")
        return None

    print(f"\n{Colors.CYAN}--- Seleccionar Item del Stock ---{Colors.ENDC}")
    print(f"{'#':<4}{'Nombre':<30}{'Precio Costo':<20}{'Precio Venta':<20}")
    print("-" * 75)
    for i, item in enumerate(stock):
        costo_f, _ = format_and_describe_number(item['precio_costo'])
        venta_f, _ = format_and_describe_number(item['precio_venta'])
        print(f"{i+1:<4}{item['nombre']:<30}{f'$ {costo_f}':<20}{f'$ {venta_f}':<20}")

    try:
        choice = int(input("\n>> Elige el número del item (0 para cancelar): ").strip())
        if choice == 0 or choice > len(stock):
            return None
        
        selected_item = stock[choice - 1]
        
        tipo_precio = input(f">> ¿Usar precio de COSTO o de VENTA para '{selected_item['nombre']}'? (c/v): ").lower().strip()
        if tipo_precio == 'c':
            return {'nombre': selected_item['nombre'], 'costo': selected_item['precio_costo']}
        elif tipo_precio == 'v':
            return {'nombre': selected_item['nombre'], 'costo': selected_item['precio_venta']}
        else:
            print(f"{Colors.RED}[ERROR] Opción no válida. Se cancela la selección.{Colors.ENDC}")
            return None
    except (ValueError, IndexError):
        print(f"{Colors.RED}[ERROR] Selección no válida.{Colors.ENDC}")
        return None

def calculadora_proyectos_detallada():
    """Calcula un presupuesto detallado desglosando costos de fabricación, ganancia e instalación."""
    log_output = "Iniciada Calculadora de Proyectos Detallada."
    print(f"\n{Colors.CYAN}--- Calculadora de Proyectos (Detallada) ---{Colors.ENDC}")
    print("Ideal para presupuestos complejos con desglose de costos.")

    while True:
        try:
            # --- 0. Título del Proyecto ---
            print(f"\n{Colors.MAGENTA}PASO 0: Identificación del Proyecto.{Colors.ENDC}")
            project_title = input(">> Introduce un título o alias para este presupuesto (ej: Cartel Luminoso Calle 123): ").strip()
            if not project_title:
                print(f"{Colors.RED}[ERROR] El título es obligatorio para guardar el presupuesto.{Colors.ENDC}")
                continue
            
            # Pedimos dimensiones aquí
            base = float(input(">> Introduce la medida de la BASE del proyecto (ej: 4.5): ").strip() or "0")
            altura = float(input(">> Introduce la medida de la ALTURA del proyecto (ej: 2.3): ").strip() or "0")
            
            budget_output = [] # Aquí guardaremos el texto del presupuesto

            # --- 1. Desglose de Costos de Fabricación ---
            print(f"\n{Colors.MAGENTA}PASO 1: Desglose de costos de fabricación del producto.{Colors.ENDC}")
            items_costo = []
            while True:
                modo_item = input(">> Añadir item: [m]anual, desde [s]tock, o [f]in para continuar: ").lower().strip()
                if modo_item == 'f': break

                if modo_item == 'm':
                    nombre_item = input("   - Nombre del item: ").strip()
                    if not nombre_item or nombre_item.isdigit():
                        print(f"{Colors.RED}[ERROR] El nombre del item no puede estar vacío o ser solo números.{Colors.ENDC}")
                        continue
                    costo_item = float(input(f"   - Costo para '{nombre_item}': $ ").strip())
                    items_costo.append({'nombre': nombre_item, 'costo': costo_item})
                
                elif modo_item == 's':
                    item_seleccionado = buscar_item_stock()
                    if item_seleccionado:
                        items_costo.append(item_seleccionado)
                        print(f"{Colors.GREEN}[SUCCESS] Item '{item_seleccionado['nombre']}' añadido al presupuesto.{Colors.ENDC}")
                
                else:
                    print(f"{Colors.RED}[ERROR] Opción no válida.{Colors.ENDC}")
            
            costo_fabricacion_total = sum(item['costo'] for item in items_costo)

            # --- 2. Margen de Ganancia ---
            print(f"\n{Colors.MAGENTA}PASO 2: Margen de ganancia.{Colors.ENDC}")
            margen_ganancia_pct = float(input(">> ¿Qué porcentaje de ganancia quieres añadir sobre la fabricación? (ej: 30): ").strip() or "0")
            
            # --- 3. Costo de Instalación ---
            print(f"\n{Colors.MAGENTA}PASO 3: Costo de instalación.{Colors.ENDC}")
            costo_instalacion = 0
            if input(">> ¿La instalación tiene un costo aparte? (s/n): ").lower() == 's':
                costo_instalacion = float(input(">> Introduce el costo total de la instalación: $ ").strip())

            # --- 4. Cálculos Finales ---
            ganancia_fabricacion = costo_fabricacion_total * (margen_ganancia_pct / 100)
            subtotal_producto = costo_fabricacion_total + ganancia_fabricacion
            precio_venta_cliente = subtotal_producto + costo_instalacion
            ganancia_total = precio_venta_cliente - (costo_fabricacion_total + costo_instalacion)

            # --- 5. Generar y Mostrar Presupuesto Detallado ---
            budget_output = generar_texto_presupuesto(
                project_title, items_costo, costo_fabricacion_total, margen_ganancia_pct, 
                ganancia_fabricacion, costo_instalacion, precio_venta_cliente, ganancia_total
            )
            # Imprimimos el resultado con colores
            colored_output = "\n".join(budget_output)
            total_f_str = format_and_describe_number(precio_venta_cliente)[0]
            colored_output = colored_output.replace(f"$ {total_f_str}", f"{Colors.GREEN}{Colors.BOLD}$ {total_f_str}{Colors.ENDC}")
            print(colored_output)

            # --- 6. Guardar Presupuesto en Archivo ---
            budget_dir = "presupuestos"
            os.makedirs(budget_dir, exist_ok=True)
            safe_title = re.sub(r'[^\w\s-]', '', project_title).strip().replace(' ', '_')
            filename = os.path.join(budget_dir, f"{safe_title}.txt")
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("\n".join(budget_output))
            
            # --- 7. Guardar datos para edición en .json ---
            data_dir = os.path.join(budget_dir, ".data")
            os.makedirs(data_dir, exist_ok=True)
            json_filename = os.path.join(data_dir, f"{safe_title}.json")
            project_data = {
                "project_title": project_title,
                "items_costo": items_costo,
                "margen_ganancia_pct": margen_ganancia_pct, 
                "base": base, "altura": altura,
                "costo_instalacion": costo_instalacion
            }
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, indent=4)

            print(f"\n{Colors.GREEN}[SUCCESS] Presupuesto guardado como: {filename}{Colors.ENDC}")
            
            total_f_for_log, _ = format_and_describe_number(precio_venta_cliente)
            log_output += f"\n  └─ Presupuesto Detallado: ${total_f_for_log}"

            # --- 8. (NUEVO) Calcular costo por m² a partir del total ---
            if base > 0 and altura > 0:
                calc_m2_output = []
                area = base * altura
                costo_por_m2 = precio_venta_cliente / area
                costo_m2_f, _ = format_and_describe_number(costo_por_m2)
                
                calc_m2_output.append("\n\n" + "="*50)
                calc_m2_output.append("CÁLCULO ADICIONAL: COSTO POR METRO CUADRADO")
                calc_m2_output.append("="*50)
                calc_m2_output.append(f"  - {'Precio Venta Cliente:':<25} $ {format_and_describe_number(precio_venta_cliente)[0]}")
                calc_m2_output.append(f"  - {'Superficie Total:':<25} {area:.2f} m² ({base} x {altura})")
                calc_m2_output.append("-" * 50)
                calc_m2_output.append(f"  - {'COSTO RESULTANTE POR m²:':<25} $ {costo_m2_f}")
                print("\n".join(calc_m2_output).replace(f"$ {costo_m2_f}", f"{Colors.YELLOW}$ {costo_m2_f}{Colors.ENDC}"))
                with open(filename, 'a', encoding='utf-8') as f:
                    f.write("\n".join(calc_m2_output))

        except ValueError:
            print(f"{Colors.RED}[ERROR] Entrada no válida. Por favor, introduce solo números donde se pida.{Colors.ENDC}")
        
        if input("\n>> ¿Hacer otro presupuesto detallado? (s/n): ").lower() != 's':
            break
    return log_output

def generar_texto_presupuesto(project_title, items_costo, costo_fabricacion_total, margen_ganancia_pct, ganancia_sobre_costo, costo_instalacion, precio_venta_cliente, ganancia_neta):
    """Toma todos los datos de un presupuesto y devuelve una lista de strings para el reporte .txt."""
    output = []
    
    output.append(f"--- PRESUPUESTO: {project_title.upper()} ---")
    output.append(f"\nA) Desglose de Fabricación:")
    
    if items_costo:
        for item in items_costo:
            costo_f, _ = format_and_describe_number(item['costo'])
            output.append(f"  - {item['nombre']:<30} $ {costo_f}")
    
    costo_fab_f, _ = format_and_describe_number(costo_fabricacion_total)
    output.append(f"  {'-'*45}\n  {'Costo Total de Fabricación:':<32} $ {costo_fab_f}")

    output.append(f"\nB) Resumen Financiero:")
    
    ganancia_f, _ = format_and_describe_number(ganancia_sobre_costo)
    instalacion_f, _ = format_and_describe_number(costo_instalacion)
    total_f, total_palabras = format_and_describe_number(precio_venta_cliente)
    ganancia_neta_f, _ = format_and_describe_number(ganancia_neta)

    output.extend([
        f"  - {'Costo de Fabricación:':<45} $ {costo_fab_f}",
        f"  - {'Ganancia sobre Costo ({margen_ganancia_pct}%):':<45} $ {ganancia_f}",
        f"  - {'Costo de Instalación:':<45} $ {instalacion_f}",
        "-" * 60,
        f"  PRECIO VENTA AL CLIENTE:                    $ {total_f}",
        f"  GANANCIA NETA DEL PROYECTO:                 $ {ganancia_neta_f}",
        f"                                                {total_palabras}"
    ])
    
    # Quitamos los códigos de color para el archivo de texto
    clean_output = [re.sub(r'\033\[[0-9;]*m', '', line) for line in output]
    
    return clean_output

def format_and_describe_number(number):
    """Formatea un número a un string con separadores y lo convierte a palabras en español."""
    # --- Formateo del número ---
    try:
        # Intentar usar una configuración regional en español para el formato
        locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')
    except locale.Error:
        try:
            locale.setlocale(locale.LC_ALL, 'Spanish_Spain.1252') # Para Windows
        except locale.Error:
            # Si falla, usamos un formateo manual simple
            formatted_number = f"{number:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            
    # locale.format_string usa las reglas de la región para formatear
    formatted_number = locale.format_string('%.2f', number, grouping=True)

    # --- Conversión a palabras ---
    parte_entera = int(number)
    parte_decimal = int(round((number - parte_entera) * 100))

    palabras_enteras = num2words(parte_entera, lang='es')
    palabras_decimales = num2words(parte_decimal, lang='es') if parte_decimal > 0 else "cero"
    
    descripcion = f"({palabras_enteras} con {palabras_decimales} centavos)"
    return formatted_number, descripcion

def calculadora_presupuestos():
    """Calcula el área y el costo de un proyecto basado en dimensiones y precios."""
    log_output = "Iniciada Calculadora de Presupuestos."
    print(f"\n{Colors.CYAN}--- Calculadora de Costos por Superficie ---{Colors.ENDC}")
    print("Calcula el costo total para un área (materiales o mano de obra).")

    while True:
        costo_base = 0
        area = 0
        try:
            # 1. Pedir medidas
            base = float(input("\n>> Introduce la medida de la BASE (ej: 4.5): "))
            altura = float(input(">> Introduce la medida de la ALTURA (ej: 2.3): "))
            area = base * altura

            # 2. Pedir costo
            costo_base = float(input(f"{Colors.YELLOW}>> Introduce el COSTO BASE por m² (Material o Mano de Obra): {Colors.ENDC}"))

            # 3. Pedir margen de ganancia
            margen_pct = float(input(f"{Colors.YELLOW}>> Introduce el margen de ganancia a añadir (%) (ej: 30): {Colors.ENDC}") or "0")

            # 4. Calcular
            costo_total_fabricacion = area * costo_base
            ganancia = costo_total_fabricacion * (margen_pct / 100)
            precio_venta_final = costo_total_fabricacion + ganancia

            # Formateamos los números importantes para la visualización
            costo_base_f, _ = format_and_describe_number(costo_base)
            costo_total_f, _ = format_and_describe_number(costo_total_fabricacion)
            precio_venta_f, precio_venta_palabras = format_and_describe_number(precio_venta_final)
            ganancia_f, _ = format_and_describe_number(ganancia)

            # 4. Mostrar resultado
            print(f"\n{Colors.BOLD}{Colors.GREEN}--- RESULTADO DEL CÁLCULO ---{Colors.ENDC}")
            print(f"  - {'Superficie a cubrir:':<25} {Colors.CYAN}{area:.2f} m²{Colors.ENDC} ({base} x {altura})")
            print(f"  - {'Costo base por m²:':<25} $ {costo_base_f}")
            print(f"  - {'Costo Total de Fabricación:':<25} $ {costo_total_f}")
            print(f"  - {'Ganancia ({margen_pct}%):':<25} $ {ganancia_f}")
            print("-" * 50)
            print(f"  {Colors.BOLD}{'PRECIO DE VENTA FINAL:':<25}{Colors.ENDC} {Colors.GREEN}{Colors.BOLD}$ {precio_venta_f}{Colors.ENDC}")
            print(f"  {'':<25} {Colors.CYAN}{precio_venta_palabras}{Colors.ENDC}")
            
            log_output += f"\n  └─ Cálculo de costo: {area:.2f}m² -> ${precio_venta_f}"

        except ValueError as e:
            print(f"{Colors.RED}[ERROR] Entrada no válida. Por favor, introduce solo números.{Colors.ENDC}")
        
        continuar = input("\n>> ¿Hacer otro presupuesto? (s/n): ").lower().strip()
        if continuar != 's':
            break
    return log_output

def cerebro_numerico():
    """Módulo con herramientas de cálculo matemático."""
    log_output = "Iniciado Cerebro Numérico."
    
    while True:
        mostrar_encabezado()
        print(f"\n{Colors.MAGENTA}--- Cerebro Numérico ---{Colors.ENDC}")
        print("  1. Calculadora Estándar")
        print("  2. Calculadora de Porcentajes")
        print(f"  3. Calculadora de Costos por Superficie")
        print(f"  {Colors.GREEN}4. Calculadora de Proyectos (Detallada){Colors.ENDC}")
        print(f"  {Colors.YELLOW}0. Volver al menú principal{Colors.ENDC}")
        
        choice = input("\n>> Elige una herramienta: ").strip()

        if choice == '1':
            print(f"\n{Colors.CYAN}--- Calculadora Estándar ---{Colors.ENDC}")
            print("Escribe una operación (ej: 5 * (10 + 2) / 3).")
            print(f"Escribe {Colors.YELLOW}0{Colors.ENDC} para volver al menú anterior.")
            while True:
                expression = input(">> Cálculo: ").strip()
                if expression == '0' or expression.lower() == 'volver':
                    break
                try:
                    # Usamos eval() de forma segura, solo permitiendo caracteres numéricos y operadores.
                    if not re.match(r'^[\d\s\+\-\*\/\(\)\.\%]+$', expression):
                        raise ValueError("Caracteres no permitidos.")
                    
                    result = eval(expression)
                    print(f"{Colors.GREEN}Resultado: {result}{Colors.ENDC}")
                    log_output += f"\n  └─ Cálculo: {expression} = {result}"
                except (SyntaxError, NameError, ZeroDivisionError, ValueError) as e:
                    print(f"{Colors.RED}[ERROR] Expresión no válida: {e}{Colors.ENDC}")

        elif choice == '2':
            print(f"\n{Colors.CYAN}--- Calculadora de Porcentajes ---{Colors.ENDC}")
            print("  a. ¿Qué es el X% de Y?")
            print("  b. ¿Qué porcentaje es X de Y?")
            
            while True:
                sub_choice = input(">> Elige una opción (o 'volver'): ").strip().lower()
                if sub_choice == 'volver':
                    break
                try:
                    if sub_choice == 'a':
                        percent = float(input("   - Introduce el porcentaje (X): "))
                        total = float(input("   - Introduce el número total (Y): "))
                        result = (percent / 100) * total
                        print(f"{Colors.GREEN}Resultado: El {percent}% de {total} es {result}{Colors.ENDC}")
                        log_output += f"\n  └─ Porcentaje: El {percent}% de {total} es {result}"
                    elif sub_choice == 'b':
                        part = float(input("   - Introduce la parte (X): "))
                        total = float(input("   - Introduce el número total (Y): "))
                        result = (part / total) * 100
                        print(f"{Colors.GREEN}Resultado: {part} es el {result:.2f}% de {total}{Colors.ENDC}")
                        log_output += f"\n  └─ Porcentaje: {part} es el {result:.2f}% de {total}"
                    else:
                        print(f"{Colors.RED}[ERROR] Opción no válida.{Colors.ENDC}")
                except ValueError:
                    print(f"{Colors.RED}[ERROR] Por favor, introduce solo números.{Colors.ENDC}")
                except ZeroDivisionError:
                    print(f"{Colors.RED}[ERROR] El número total no puede ser cero.{Colors.ENDC}")

        elif choice == '3':
            log = calculadora_presupuestos()
            log_output += f"\n  └─ {log}"

        elif choice == '4':
            log = calculadora_proyectos_detallada()
            log_output += f"\n  └─ {log}"

        elif choice == '0':
            break
        else:
            print(f"\n{Colors.RED}[ERROR] Opción no válida.{Colors.ENDC}")
            time.sleep(1)
            
    return log_output

def analizador_disco():
    """Encuentra los archivos más grandes en una ruta específica."""
    log_output = "Iniciada herramienta de análisis de disco."
    print(f"\n{Colors.MAGENTA}--- Analizador de Disco ---{Colors.ENDC}")
    print("Esta herramienta busca los archivos más grandes en una carpeta y sus subcarpetas.")

    while True:
        current_path = os.path.abspath(os.sep) # Empezar en la raíz del sistema

        # Navegación de carpetas
        while True:
            try:
                items = os.listdir(current_path)
                dirs = sorted([d for d in items if os.path.isdir(os.path.join(current_path, d))])
            except PermissionError:
                print(f"\n{Colors.RED}[ERROR] Permiso denegado para acceder a '{current_path}'. Subiendo un nivel.{Colors.ENDC}")
                current_path = os.path.dirname(current_path)
                continue

            print(f"\n{Colors.MAGENTA}--- Explorador de Disco ---{Colors.ENDC}")
            print(f"Ubicación actual: {Colors.CYAN}{current_path}{Colors.ENDC}")
            
            for i, dirname in enumerate(dirs):
                print(f"  {Colors.BOLD}{i + 1}.{Colors.ENDC} {dirname}")

            print(f"\n{Colors.MAGENTA}Opciones:{Colors.ENDC}")
            print("  [#] - Elige un número para entrar a una carpeta.")
            print(f"  [{Colors.GREEN}a{Colors.ENDC}] - {Colors.GREEN}Analizar esta carpeta en busca de archivos grandes.{Colors.ENDC}")
            print(f"  [{Colors.YELLOW}u{Colors.ENDC}] - Subir un nivel.")
            print(f"  [{Colors.RED}v{Colors.ENDC}] - Volver al menú principal.")

            choice = input("\n>> Elige una opción: ").strip().lower()

            if choice == 'v':
                return "Análisis de disco finalizado."
            elif choice == 'u':
                parent_path = os.path.dirname(current_path)
                if parent_path != current_path:
                    current_path = parent_path
                else:
                    print(f"\n{Colors.YELLOW}[INFO] Ya estás en la raíz. No se puede subir más.{Colors.ENDC}")
                    time.sleep(2)
            elif choice == 'a':
                # Iniciar el análisis en la carpeta actual
                try:
                    print(f"\n{Colors.MAGENTA}¿Qué tamaño mínimo de archivos te interesa buscar?{Colors.ENDC}")
                    print(f"  1. Pequeños {Colors.CYAN}(10 MB){Colors.ENDC}")
                    print(f"  2. Medianos {Colors.CYAN}(100 MB){Colors.ENDC}")
                    print(f"  3. Grandes {Colors.CYAN}(500 MB){Colors.ENDC}")
                    print(f"  4. Gigantes {Colors.CYAN}(1 GB){Colors.ENDC}")
                    
                    size_choice = input(">> Elige una opción (por defecto '2'): ").strip() or '2'
                    size_map = {'1': 10, '2': 100, '3': 500, '4': 1024}
                    min_size_mb = size_map.get(size_choice, 100)

                    num_files_to_show_str = input(">> ¿Cuántos archivos quieres mostrar en el top? (por defecto '10'): ").strip() or '10'
                    num_files_to_show = int(num_files_to_show_str)

                    print(f"\n{Colors.YELLOW}Analizando '{current_path}'... (Presiona Ctrl+C para cancelar){Colors.ENDC}")
                    
                    large_files = []
                    for foldername, subfolders, filenames in os.walk(current_path):
                        print(f"\r{Colors.YELLOW}Escaneando: {foldername[:70]:<70}{Colors.ENDC}", end="", flush=True)
                        for filename in filenames:
                            try:
                                file_path = os.path.join(foldername, filename)
                                size_bytes = os.path.getsize(file_path)
                                if size_bytes >= min_size_mb * 1024 * 1024:
                                    large_files.append((size_bytes, file_path))
                            except (FileNotFoundError, OSError):
                                continue
                    print("\r" + " " * 80 + "\r", end="")

                    while True: # Bucle para mostrar la lista y permitir borrar
                        large_files.sort(key=lambda x: x[0], reverse=True)

                        print(f"\n{Colors.BOLD}--- Top {num_files_to_show} de Archivos Más Grandes (mayores a {min_size_mb} MB) ---{Colors.ENDC}")
                        print(f"{'#':<4}{'Tamaño (MB)':<15}{'Ruta del Archivo'}{Colors.ENDC}")
                        print("-" * 90)
                        for i, (size, path) in enumerate(large_files[:num_files_to_show]):
                            size_mb = size / 1024 / 1024
                            print(f"{Colors.BOLD}{i+1:<4}{Colors.ENDC}{Colors.GREEN}{size_mb:<15.2f}{Colors.ENDC}{path}")

                        if not large_files:
                            print(f"{Colors.YELLOW}[INFO] No se encontraron archivos que cumplan los criterios.{Colors.ENDC}")
                            break

                        try:
                            action_choice = input("\n>> Elige un # para BORRAR el archivo (o 'volver'): ").strip()
                            if action_choice.lower() == 'volver':
                                break
                            
                            file_idx = int(action_choice) - 1
                            if 0 <= file_idx < len(large_files):
                                size_to_delete, path_to_delete = large_files[file_idx]
                                confirm = input(f"{Colors.BOLD}{Colors.RED}ADVERTENCIA: ¿Seguro que quieres borrar '{os.path.basename(path_to_delete)}' ({size_to_delete/1024/1024:.2f} MB)? (s/n): {Colors.ENDC}").lower()
                                if confirm == 's':
                                    os.remove(path_to_delete)
                                    print(f"{Colors.GREEN}[SUCCESS] Archivo borrado.{Colors.ENDC}")
                                    del large_files[file_idx]
                            else:
                                print(f"{Colors.RED}[ERROR] Número fuera de rango.{Colors.ENDC}")
                        except (ValueError, OSError) as e:
                            print(f"\n{Colors.RED}[ERROR] No se pudo realizar la acción: {e}{Colors.ENDC}")

                except KeyboardInterrupt:
                    print(f"\n{Colors.RED}Análisis cancelado por el usuario.{Colors.ENDC}")
                except ValueError:
                    print(f"\n{Colors.RED}[ERROR] Entrada no válida.{Colors.ENDC}")
            
            elif choice.isdigit():
                try:
                    dir_index = int(choice) - 1
                    if 0 <= dir_index < len(dirs):
                        current_path = os.path.join(current_path, dirs[dir_index])
                    else:
                        print(f"\n{Colors.RED}[ERROR] Número fuera de rango.{Colors.ENDC}")
                except ValueError:
                    print(f"\n{Colors.RED}[ERROR] Selección no válida.{Colors.ENDC}")
            else:
                print(f"\n{Colors.RED}[ERROR] Opción no reconocida.{Colors.ENDC}")
                time.sleep(2)

    return "Análisis de disco finalizado."

def actualizar_programa():
    """Ejecuta el script externo para actualizar el programa desde GitHub."""
    if not os.path.exists("ACTUALIZAR.bat"):
        print(f"\n{Colors.RED}[ERROR] No se encontró el archivo 'ACTUALIZAR.bat'.{Colors.ENDC}")
        return "Fallo de actualización: falta script."

    print(f"\n{Colors.MAGENTA}--- Actualización del Sistema ---{Colors.ENDC}")
    print("El programa se cerrará, descargará la nueva versión y se reiniciará.")
    confirm = input("¿Estás seguro? (s/n): ").lower().strip()
    if confirm == 's':
        print(f"{Colors.GREEN}Iniciando secuencia de actualización...{Colors.ENDC}")
        subprocess.Popen(["ACTUALIZAR.bat"], shell=True)
        os._exit(0) # Cerramos Python forzosamente para permitir que el bat sobrescriba el exe
    return "Actualización cancelada."

def mostrar_menu():
    """Muestra el menú de opciones numerado."""
    # --- Menú rediseñado en columnas para ser más compacto ---
    # Definimos las opciones por categoría
    monitoreo = [
        "1. Ver uso de CPU",
        "2. Ver uso de RAM",
        "3. Ver reportes"
    ]
    sistema = [
        "4. Puertos abiertos",
        "5. Info de usuarios",
        "6. Programas instalados",
        "7. Analizar procesos"
    ]
    accion = [
        f"{Colors.RED}8. Apocalipsis{Colors.ENDC}",
        f"{Colors.GREEN}9. Ejecutor{Colors.ENDC}",
        f"{Colors.MAGENTA}10. Modo Espía{Colors.ENDC}",
        f"{Colors.BLUE}11. Ping{Colors.ENDC}",
        f"{Colors.BLUE}12. Analizador Disco{Colors.ENDC}",
        f"{Colors.MAGENTA}13. Analizar WiFi{Colors.ENDC}",
        f"{Colors.MAGENTA}14. Depredador (OSINT){Colors.ENDC}",
        f"{Colors.RED}15. Cazador Shodan{Colors.ENDC}",
        f"{Colors.GREEN}16. Cerebro Numérico{Colors.ENDC}",
        f"{Colors.CYAN}17. Ojo de Halcón{Colors.ENDC}",
        f"{Colors.BLUE}18. Gestionar Stock{Colors.ENDC}",
        f"{Colors.YELLOW}19. Actualizar Programa{Colors.ENDC}"
    ]

    # Imprimimos en formato de tabla
    print(f"\n{Colors.BOLD}┌─ MONITOREO ─────────────┬─ SISTEMA ──────────────────┬─ ACCIÓN ──────────────────┐{Colors.ENDC}")
    max_rows = max(len(monitoreo), len(sistema), len(accion))
    for i in range(max_rows):
        col1 = f"  {monitoreo[i]:<24}" if i < len(monitoreo) else ' ' * 26
        col2 = f"  {sistema[i]:<25}" if i < len(sistema) else ' ' * 27
        col3 = f"  {accion[i]:<25}" if i < len(accion) else ' ' * 27
        # Usamos expresiones regulares para no contar los códigos de color en el padding
        col3_clean_len = len(re.sub(r'\033\[[0-9;]*m', '', col3))
        padding = ' ' * (27 - col3_clean_len)
        print(f"{Colors.BOLD}│{Colors.ENDC}{col1}{Colors.BOLD}│{Colors.ENDC}{col2}{Colors.BOLD}│{Colors.ENDC}{col3}{padding}{Colors.BOLD}│{Colors.ENDC}")
    print(f"{Colors.BOLD}└─────────────────────────┴──────────────────────────┴───────────────────────────┘{Colors.ENDC}")
    print(f"  {Colors.YELLOW}{Colors.BOLD}0. Salir{Colors.ENDC}")

def gestionar_salida(log_sesion):
    """Muestra un submenú al salir y gestiona la opción."""
    print(f"\n{Colors.YELLOW}{Colors.BOLD}MENÚ DE SALIDA{Colors.ENDC}")
    print("  1. Guardar reporte y salir")
    print("  2. Salir directamente")
    print("  0. Volver al menú principal")
    
    opcion = input(">> Selecciona una opción de salida: ")
    if opcion == '1':
        guardar_reporte(log_sesion)
        return False # Indica que se debe salir
    elif opcion == '2':
        return False # Indica que se debe salir
    return True # Indica que se debe continuar en el menú principal

def mostrar_encabezado():
    """Imprime el encabezado principal del programa."""
    os.system('cls' if os.name == 'nt' else 'clear')
    # Encabezado rediseñado para ser más compacto
    print(fr"""{Colors.BOLD}{Colors.CYAN}
      .-.
     (o.o)  EL CEREBRO
      |=|   Panel de Control RichonOS v1.1
     /   \{Colors.ENDC}""")

def guardar_reporte(log_sesion):
    """Guarda las consultas de la sesión en un archivo de texto."""
    if not log_sesion:
        print(f"\n{Colors.YELLOW}[INFO] No hay consultas que guardar en esta sesión.{Colors.ENDC}")
        return

    now = datetime.now()
    # Usamos un nombre de archivo por día para consolidar los reportes.
    filename = now.strftime("reporte_cerebro_%Y-%m-%d.txt")
    
    # 'a' para añadir al final del archivo si existe, 'w' (implícito con 'a' si no existe) para crearlo.
    with open(filename, 'a', encoding='utf-8') as f:
        # Si el archivo está vacío, escribimos un encabezado general.
        if f.tell() == 0:
            f.write("╔═════════════════════════════════════════╗\n")
            f.write("║   REPORTE CONSOLIDADO - EL CEREBRO      ║\n")
            f.write("╚═════════════════════════════════════════╝\n")
        
        # Añadimos un separador y la hora para cada nueva sesión guardada.
        f.write(f"\n\n═══════════ SESIÓN GUARDADA EL {now.strftime('%Y-%m-%d a las %H:%M:%S')} ═══════════\n")
        f.writelines(log + '\n' for log in log_sesion)
    print(f"\n{Colors.GREEN}[SUCCESS] Reporte guardado/actualizado en: {filename}{Colors.ENDC}")

def menu_post_accion(opcion_actual, log_sesion):
    """Muestra un menú de acciones después de ejecutar una opción."""
    print(f"\n{Colors.MAGENTA}{Colors.BOLD}¿QUÉ HACER AHORA?{Colors.ENDC}")
    print("  [s]iguiente: Ejecuta la siguiente opción del menú.")
    print("  [m]enú: Vuelve al menú principal.")
    print("  [g]uardar: Guarda el reporte de la sesión actual.")
    print("  [#]: Escribe el número de otra opción para ir directamente.")
    prompt = f">> Elige una acción: "
    
    while True:
        eleccion = input(prompt).lower().strip()
        if eleccion == 'm' or eleccion == 'menu':
            return None # Indica volver al menú principal
        elif eleccion == 's' or eleccion == 'siguiente':
            # Lógica para ir a la siguiente opción (si es 1 va a 2, si es 2 va a 1)
            return str((int(opcion_actual) % 18) + 1) # Cicla a través de las opciones
        elif eleccion == 'g':
            guardar_reporte(log_sesion)
        elif eleccion in [str(i) for i in range(1, 20)]: # Ampliar si hay más opciones
            return eleccion # Devuelve el número de la nueva opción a ejecutar
        else:
            print(f"{Colors.RED}[ERROR] Opción no reconocida.{Colors.ENDC}")

def iniciar_panel():
    """Función principal que muestra el menú y procesa las opciones."""
    mostrar_encabezado()
    log_sesion = []
    proxima_opcion = None

    try:
        while True:
            if proxima_opcion is None:
                mostrar_menu()
                opcion = input(">> Selecciona una opción: ")
            else:
                opcion = proxima_opcion
                proxima_opcion = None # Resetea para el siguiente ciclo

            if opcion == '1':
                log = mostrar_uso_cpu()
                log_sesion.append(f"[{datetime.now().strftime('%H:%M:%S')}] {log}")
                proxima_opcion = menu_post_accion(opcion, log_sesion)
            elif opcion == '2':
                log = mostrar_uso_memoria()
                log_sesion.append(f"[{datetime.now().strftime('%H:%M:%S')}] {log}")
                proxima_opcion = menu_post_accion(opcion, log_sesion)
            elif opcion == '3':
                log = visualizar_reportes()
                log_sesion.append(f"[{datetime.now().strftime('%H:%M:%S')}] {log}")
                proxima_opcion = menu_post_accion(opcion, log_sesion)
            elif opcion == '4':
                log = mostrar_puertos_abiertos()
                log_sesion.append(f"[{datetime.now().strftime('%H:%M:%S')}] {log}")
                proxima_opcion = menu_post_accion(opcion, log_sesion)
            elif opcion == '5':
                log = mostrar_usuarios()
                log_sesion.append(f"[{datetime.now().strftime('%H:%M:%S')}] {log}")
                proxima_opcion = menu_post_accion(opcion, log_sesion)
            elif opcion == '6':
                log = mostrar_programas_instalados()
                log_sesion.append(f"[{datetime.now().strftime('%H:%M:%S')}] {log}")
                proxima_opcion = menu_post_accion(opcion, log_sesion)
            elif opcion == '7':
                log = analizar_procesos()
                log_sesion.append(f"[{datetime.now().strftime('%H:%M:%S')}] {log}")
                proxima_opcion = menu_post_accion(opcion, log_sesion)
            elif opcion == '8':
                log = ejecutar_apocalipsis()
                log_sesion.append(f"[{datetime.now().strftime('%H:%M:%S')}] {log}")
                proxima_opcion = menu_post_accion(opcion, log_sesion)
            elif opcion == '9':
                log = ejecutar_programa()
                log_sesion.append(f"[{datetime.now().strftime('%H:%M:%S')}] {log}")
                proxima_opcion = menu_post_accion(opcion, log_sesion)
            elif opcion == '10':
                log = modo_espia()
                log_sesion.append(f"[{datetime.now().strftime('%H:%M:%S')}] {log}")
                proxima_opcion = menu_post_accion(opcion, log_sesion)
            elif opcion == '11':
                log = herramienta_ping()
                log_sesion.append(f"[{datetime.now().strftime('%H:%M:%S')}] {log}")
                proxima_opcion = menu_post_accion(opcion, log_sesion)
            elif opcion == '12':
                log = analizador_disco()
                log_sesion.append(f"[{datetime.now().strftime('%H:%M:%S')}] {log}")
                proxima_opcion = menu_post_accion(opcion, log_sesion)
            elif opcion == '13':
                log = analizar_redes_wifi()
                log_sesion.append(f"[{datetime.now().strftime('%H:%M:%S')}] {log}")
                proxima_opcion = menu_post_accion(opcion, log_sesion)
            elif opcion == '14':
                log = depredador_silencioso()
                log_sesion.append(f"[{datetime.now().strftime('%H:%M:%S')}] {log}")
                proxima_opcion = menu_post_accion(opcion, log_sesion)
            elif opcion == '15':
                log = cazador_shodan()
                log_sesion.append(f"[{datetime.now().strftime('%H:%M:%S')}] {log}")
                proxima_opcion = menu_post_accion(opcion, log_sesion)
            elif opcion == '16':
                log = cerebro_numerico()
                log_sesion.append(f"[{datetime.now().strftime('%H:%M:%S')}] {log}")
                proxima_opcion = menu_post_accion(opcion, log_sesion)
            elif opcion == '17':
                log = visor_presupuestos()
                log_sesion.append(f"[{datetime.now().strftime('%H:%M:%S')}] {log}")
                proxima_opcion = menu_post_accion(opcion, log_sesion)
            elif opcion == '18':
                log = gestionar_stock()
                log_sesion.append(f"[{datetime.now().strftime('%H:%M:%S')}] {log}")
                proxima_opcion = menu_post_accion(opcion, log_sesion)
            elif opcion == '19':
                log = actualizar_programa()
                log_sesion.append(f"[{datetime.now().strftime('%H:%M:%S')}] {log}")
                proxima_opcion = menu_post_accion(opcion, log_sesion)
            elif opcion == '0':
                if not gestionar_salida(log_sesion):
                    print("\nCerrando El Cerebro. ¡Hasta la próxima, richon!")
                    break
                # Si el usuario decide volver, se mostrará el menú principal
            else:
                print(f"\n{Colors.RED}[ERROR] Opción '{opcion}' no válida. Inténtalo de nuevo.{Colors.ENDC}")
                input("\n--- Presiona Enter para continuar ---")

            # Si la siguiente acción es volver al menú, se limpia la pantalla y se muestra el encabezado
            if proxima_opcion is None:
                mostrar_encabezado()

    except KeyboardInterrupt:
        print("\n\nCierre forzado. ¡Adiós, richon!")

def main():
    """Función principal que decide qué mostrar."""
    iniciar_panel()

if __name__ == "__main__":
    main()
