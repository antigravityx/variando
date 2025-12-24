# componentes/modulo_sistema.py
import os
import psutil
import time
import subprocess
import winreg
from datetime import datetime
import shutil

from .colores import Colors
from .constantes import PROCESOS_CONOCIDOS
from .utilidades import get_color_for_usage, get_color_for_mem_mb

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
    output_log = f"Uso de RAM actual: {uso}% ({memoria.used / 1024**3:.2f} GB / {memoria.total / 1024**3:.2f} GB)"
    print(output_colored)
    return output_log

def gestionar_proceso(pid):
    """Muestra información detallada de un proceso por su PID y devuelve un log."""
    try:
        p = psutil.Process(pid)
        with p.oneshot():
            print(f"\n{Colors.MAGENTA}--- Detalles del Proceso (PID: {pid}) ---{Colors.ENDC}")
            
            proc_name = p.name()
            if proc_name.lower() in PROCESOS_CONOCIDOS:
                print(f"{Colors.CYAN}  [i] Descripción de '{proc_name}': {PROCESOS_CONOCIDOS[proc_name.lower()]}{Colors.ENDC}")

            print(f"{Colors.BOLD}Nombre:{Colors.ENDC} {p.name()}")
            print(f"{Colors.BOLD}Ruta:{Colors.ENDC} {p.exe()}")
            print(f"{Colors.BOLD}Usuario:{Colors.ENDC} {p.username()}")
            
            cpu_usage = p.cpu_percent(interval=0.1)
            mem_usage_mb = p.memory_info().rss / (1024 * 1024)
            print(f"{Colors.BOLD}Uso de CPU:{Colors.ENDC} {get_color_for_usage(cpu_usage)}{cpu_usage:.2f}%{Colors.ENDC}")
            print(f"{Colors.BOLD}Uso de Memoria (RSS):{Colors.ENDC} {mem_usage_mb:.2f} MB")

            create_time = datetime.fromtimestamp(p.create_time()).strftime("%Y-%m-%d %H:%M:%S")
            print(f"{Colors.BOLD}Iniciado el:{Colors.ENDC} {create_time}")
            print(f"{Colors.BOLD}Estado:{Colors.ENDC} {p.status()}")
            
            log_output = [f"Consulta de detalles para PID {pid}: Nombre={p.name()}, Usuario={p.username()}, CPU={cpu_usage:.2f}%, Mem={mem_usage_mb:.2f}MB"]

        while True:
            status = p.status()
            print(f"\n{Colors.MAGENTA}--- Acciones para PID {pid} ({p.name()}) ---{Colors.ENDC}")
            
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
                time.sleep(1)
                if not p.is_running():
                    print(f"{Colors.GREEN}[SUCCESS] El proceso se ha cerrado.{Colors.ENDC}")
                    return "\n".join(log_output)
            
            elif accion == 'k':
                p.kill()
                print(f"{Colors.BOLD}{Colors.RED}[ACTION] Proceso {pid} forzado a terminar (kill).{Colors.ENDC}")
                log_output.append(f"  └─ ACCIÓN: Proceso {pid} forzado a terminar (kill).")
                time.sleep(1)
                if not p.is_running():
                    print(f"{Colors.GREEN}[SUCCESS] El proceso ha sido eliminado.{Colors.ENDC}")
                    return "\n".join(log_output)
            
            elif accion == 'kt':
                print(f"{Colors.BOLD}{Colors.RED}[ACTION] ¡Desatando KillTrueno sobre PID {pid} y su árbol de procesos!{Colors.ENDC}")
                log_output.append(f"  └─ ACCIÓN: KillTrueno ejecutado sobre {pid} ({p.name()}).")
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

def mostrar_usuarios():
    """Muestra los usuarios actualmente logueados en el sistema."""
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
                proc_username = p.info['username'].split('\\')[-1] if p.info['username'] else ''
                if proc_username and username_input.lower() in proc_username.lower():
                    user_procs.append(p)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        sorted_procs = sorted(user_procs, key=lambda p: p.info['memory_info'].rss if p.info['memory_info'] else 0, reverse=True)

        if not sorted_procs:
            print(f"\n{Colors.YELLOW}[INFO] No se encontraron procesos para el usuario '{username_input}'.{Colors.ENDC}")
            continue
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
        for p in psutil.process_iter(['pid']):
            try:
                p.cpu_percent(interval=0.01)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        time.sleep(0.5)

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
            subprocess.run(['taskkill', '/F', '/IM', proc_name], capture_output=True, text=True)
            time.sleep(1)
            
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

def analizador_disco():
    """Encuentra los archivos más grandes en una ruta específica."""
    log_output = "Iniciada herramienta de análisis de disco."
    print(f"\n{Colors.MAGENTA}--- Analizador de Disco ---{Colors.ENDC}")
    print("Esta herramienta busca los archivos más grandes en una carpeta y sus subcarpetas.")

    while True:
        current_path = os.path.abspath(os.sep)

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

                    while True:
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

def limpieza_sistema():
    """Elimina archivos temporales y basura del sistema."""
    log_output = "Iniciada Limpieza del Sistema."
    print(f"\n{Colors.MAGENTA}--- Limpieza del Sistema ---{Colors.ENDC}")
    print(f"{Colors.RED}ADVERTENCIA: Se eliminarán archivos temporales y cachés.{Colors.ENDC}")
    print("Esto libera espacio. Asegúrate de haber guardado tu trabajo en otros programas.")
    
    rutas_a_limpiar = [
        os.environ.get('TEMP'),
        os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'Temp'),
        os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'Prefetch')
    ]

    print(f"\n{Colors.CYAN}Se analizarán y limpiarán las siguientes rutas:{Colors.ENDC}")
    for ruta in rutas_a_limpiar:
        if ruta and os.path.exists(ruta):
            print(f"  -> {ruta}")

    if input("\n>> ¿Continuar con la limpieza? (s/n): ").lower().strip() != 's':
        return "Limpieza cancelada."

    bytes_liberados = 0
    print("\nIniciando limpieza...")
    
    for carpeta in rutas_a_limpiar:
        if not carpeta or not os.path.exists(carpeta):
            continue
            
        print(f"  -> Barriendo: {carpeta}")
        for root, dirs, files in os.walk(carpeta):
            for f in files:
                try:
                    file_path = os.path.join(root, f)
                    size = os.path.getsize(file_path)
                    os.remove(file_path)
                    bytes_liberados += size
                except (PermissionError, OSError):
                    pass
            
            for d in dirs:
                try:
                    dir_path = os.path.join(root, d)
                    shutil.rmtree(dir_path)
                except (PermissionError, OSError):
                    pass

    mb_liberados = bytes_liberados / (1024 * 1024)
    print(f"\n{Colors.GREEN}[SUCCESS] Limpieza completada.{Colors.ENDC}")
    print(f"Espacio recuperado: {Colors.BOLD}{mb_liberados:.2f} MB{Colors.ENDC}")
    
    return f"Limpieza del sistema: {mb_liberados:.2f} MB liberados."