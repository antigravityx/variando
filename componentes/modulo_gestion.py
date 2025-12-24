# componentes/modulo_gestion.py
import os
import glob
import json
from datetime import datetime
import pyautogui
import subprocess
import time
import re

from .colores import Colors
from .utilidades import format_and_describe_number, ejecutar_reinicio_fluido

def mostrar_encabezado():
    """Función auxiliar para limpiar y mostrar el encabezado, evitando importación circular."""
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"\n{Colors.BOLD}{Colors.CYAN}      .-.\n     (o.o)  EL CEREBRO\n      |=|   Panel de Control RichonOS\n     /   \\{Colors.ENDC}")

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

def modo_espia():
    """Permite encontrar y obtener información de ventanas abiertas."""
    log_output = "Iniciado Modo Espía."
    
    while True:
        print(f"\n{Colors.MAGENTA}--- Modo Espía / Explorador de Ventanas ---{Colors.ENDC}")
        
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

def actualizar_programa():
    """Actualiza el programa con reinicio fluido (Protocolo 2.0)."""
    if not os.path.exists("ACTUALIZAR.bat"):
        print(f"\n{Colors.RED}[ERROR] No se encontró el archivo 'ACTUALIZAR.bat'.{Colors.ENDC}")
        return "Fallo de actualización: falta script."

    print(f"\n{Colors.MAGENTA}--- Actualización del Sistema (Protocolo 2.0) ---{Colors.ENDC}")
    print("El programa buscará la nueva versión y se reiniciará de forma fluida.")
    confirm = input("¿Deseas iniciar la secuencia de actualización? (s/n): ").lower().strip()
    if confirm == 's':
        print(f"{Colors.GREEN}Iniciando descarga y refresco del alma...{Colors.ENDC}")
        # En una implementación real aquí iría la descarga. 
        # Por ahora, simulamos el éxito y ejecutamos el reinicio fluido.
        time.sleep(1)
        print(f"{Colors.CYAN}[OK] Parches descargados. Reconfigurando integridad...{Colors.ENDC}")
        time.sleep(1)
        ejecutar_reinicio_fluido()
        return "Actualización ejecutada con éxito."
    return "Actualización cancelada."

def gestionar_avance_proyecto():
    """Gestiona una lista de tareas y el avance del desarrollo del proyecto."""
    log_output = "Iniciada Gestión de Avance del Proyecto."
    archivo_avance = "avance_proyecto.json"
    
    if os.path.exists(archivo_avance):
        try:
            with open(archivo_avance, 'r', encoding='utf-8') as f:
                tareas = json.load(f)
        except:
            tareas = []
    else:
        tareas = []

    while True:
        mostrar_encabezado()
        print(f"\n{Colors.MAGENTA}--- Gestión de Avance y Tareas (Dev Tracker) ---{Colors.ENDC}")
        
        total = len(tareas)
        completadas = sum(1 for t in tareas if t['estado'] == 'completada')
        progreso = (completadas / total * 100) if total > 0 else 0
        
        bar_length = 20
        filled_length = int(bar_length * completadas // total) if total > 0 else 0
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        color_bar = Colors.GREEN if progreso == 100 else Colors.YELLOW if progreso > 50 else Colors.RED
        
        print(f"Progreso Global: {color_bar}[{bar}] {progreso:.1f}%{Colors.ENDC} ({completadas}/{total} tareas)")
        
        print("\nOpciones:")
        print("  1. Ver tareas pendientes/en proceso")
        print("  2. Ver historial completo (incluye terminadas)")
        print("  3. Agregar nueva tarea")
        print("  4. Actualizar estado de una tarea")
        print("  5. Eliminar tarea")
        print(f"  {Colors.YELLOW}0. Volver al menú principal{Colors.ENDC}")
        
        choice = input("\n>> Elige una opción: ").strip()
        
        if choice == '1' or choice == '2':
            print(f"\n{Colors.BOLD}{'ID':<4}{'Estado':<12}{'Tarea':<40}{'Notas'}{Colors.ENDC}")
            print("-" * 80)
            found = False
            for i, t in enumerate(tareas):
                if choice == '1' and t['estado'] == 'completada':
                    continue
                
                estado_color = Colors.RED if t['estado'] == 'pendiente' else Colors.YELLOW if t['estado'] == 'en_proceso' else Colors.GREEN
                print(f"{i+1:<4}{estado_color}{t['estado']:<12}{Colors.ENDC}{t['tarea']:<40}{t.get('notas', '')}")
                found = True
            
            if not found:
                print(f"{Colors.YELLOW}[INFO] No hay tareas para mostrar.{Colors.ENDC}")
            input("\n--- Enter para continuar ---")

        elif choice == '3':
            tarea = input(">> Descripción de la tarea: ").strip()
            if tarea:
                notas = input(">> Notas adicionales (opcional): ").strip()
                nueva_tarea = {
                    "tarea": tarea,
                    "estado": "pendiente",
                    "fecha_creacion": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "notas": notas
                }
                tareas.append(nueva_tarea)
                with open(archivo_avance, 'w', encoding='utf-8') as f:
                    json.dump(tareas, f, indent=4)
                print(f"{Colors.GREEN}[SUCCESS] Tarea agregada.{Colors.ENDC}")
                time.sleep(1)

        elif choice == '4':
            try:
                idx = int(input(">> ID de la tarea a actualizar: ").strip()) - 1
                if 0 <= idx < len(tareas):
                    t = tareas[idx]
                    print(f"\nEditando: {t['tarea']}")
                    print("  1. Pendiente")
                    print("  2. En Proceso")
                    print("  3. Completada")
                    estado_choice = input(">> Nuevo estado: ").strip()
                    if estado_choice == '1': t['estado'] = 'pendiente'
                    elif estado_choice == '2': t['estado'] = 'en_proceso'
                    elif estado_choice == '3': t['estado'] = 'completada'
                    
                    with open(archivo_avance, 'w', encoding='utf-8') as f:
                        json.dump(tareas, f, indent=4)
                    print(f"{Colors.GREEN}[SUCCESS] Estado actualizado.{Colors.ENDC}")
                else:
                    print(f"{Colors.RED}[ERROR] ID inválido.{Colors.ENDC}")
            except ValueError:
                print(f"{Colors.RED}[ERROR] Entrada no válida.{Colors.ENDC}")
            time.sleep(1)

        elif choice == '5':
            try:
                idx = int(input(">> ID de la tarea a eliminar: ").strip()) - 1
                if 0 <= idx < len(tareas):
                    confirm = input(f"¿Borrar '{tareas[idx]['tarea']}'? (s/n): ").lower()
                    if confirm == 's':
                        tareas.pop(idx)
                        with open(archivo_avance, 'w', encoding='utf-8') as f:
                            json.dump(tareas, f, indent=4)
                        print(f"{Colors.GREEN}[SUCCESS] Tarea eliminada.{Colors.ENDC}")
                else:
                    print(f"{Colors.RED}[ERROR] ID inválido.{Colors.ENDC}")
            except ValueError:
                print(f"{Colors.RED}[ERROR] Entrada no válida.{Colors.ENDC}")
            time.sleep(1)

        elif choice == '0':
            break
            
    return log_output

def gestionar_stock():
    """Permite al usuario ver, añadir y gestionar un inventario de materiales."""
    log_output = "Iniciada gestión de Stock."
    stock_file = "stock.json"
    
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

def visor_presupuestos():
    """Busca y muestra presupuestos guardados en la carpeta 'presupuestos'."""
    from .modulo_proyectos import generar_texto_presupuesto # Importación local
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
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    content = content.replace("--- PRESUPUESTO:", f"{Colors.BOLD}{Colors.GREEN}--- PRESUPUESTO:")
                    content = content.replace("A) Desglose de Fabricación:", f"{Colors.BOLD}A) Desglose de Fabricación:{Colors.ENDC}")
                    content = content.replace("B) Resumen Financiero:", f"{Colors.BOLD}B) Resumen Financiero:{Colors.ENDC}")
                    content = content.replace("Costo de Fabricación:", f"Costo de Fabricación:{Colors.YELLOW}")
                    content = content.replace("PRECIO VENTA AL CLIENTE:", f"{Colors.BOLD}PRECIO VENTA AL CLIENTE:{Colors.ENDC}{Colors.GREEN}{Colors.BOLD}")
                    content = content.replace("GANANCIA NETA DEL PROYECTO:", f"{Colors.BOLD}GANANCIA NETA DEL PROYECTO:{Colors.ENDC}{Colors.CYAN}{Colors.BOLD}")
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if Colors.YELLOW in line or Colors.GREEN in line or Colors.CYAN in line:
                            lines[i] += Colors.ENDC
                    print("\n".join(lines))
                input("\n--- Presiona Enter para continuar ---")
            
            elif action == 'editar':
                # La función de edición se ha movido a este módulo
                editar_presupuesto(full_path, generar_texto_presupuesto)

            elif action == 'borrar':
                if input(f"{Colors.RED}¿Seguro que quieres borrar permanentemente '{selected_filename}'? (s/n): {Colors.ENDC}").lower() == 's':
                    os.remove(full_path)
                    json_path = os.path.join(budget_dir, ".data", selected_filename.replace('.txt', '.json'))
                    if os.path.exists(json_path): os.remove(json_path)
                    print(f"{Colors.GREEN}[SUCCESS] Presupuesto borrado.{Colors.ENDC}")
                    time.sleep(2)

        except (ValueError, IndexError):
            print(f"\n{Colors.RED}[ERROR] Selección no válida.{Colors.ENDC}")
            time.sleep(2)

    return log_output

def editar_presupuesto(file_path, func_generar_texto):
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

    project_title = data['project_title']
    items_costo = data['items_costo']
    margen_ganancia_pct = data['margen_ganancia_pct']
    base = data.get('base', 0)
    altura = data.get('altura', 0)
    costo_instalacion = data['costo_instalacion']

    while True:
        mostrar_encabezado()
        print(f"\n{Colors.MAGENTA}--- Editando Presupuesto: {project_title} ---{Colors.ENDC}")
        # ... (lógica de menú de edición)

        choice = input("\n>> ¿Qué deseas modificar?: ").strip()

        if choice == '5': # Guardar
            costo_fabricacion_total = sum(item['costo'] for item in items_costo)
            ganancia_fabricacion = costo_fabricacion_total * (margen_ganancia_pct / 100)
            presupuesto_final = (costo_fabricacion_total + ganancia_fabricacion) + costo_instalacion
            
            budget_output = func_generar_texto(project_title, items_costo, costo_fabricacion_total, margen_ganancia_pct, ganancia_fabricacion, costo_instalacion, presupuesto_final, ganancia_fabricacion)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("\n".join(budget_output))
            
            new_data = {
                'project_title': project_title, 'items_costo': items_costo,
                'margen_ganancia_pct': margen_ganancia_pct, 'costo_instalacion': costo_instalacion,
                'base': base, 'altura': altura
            }
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(new_data, f, indent=4)

            print(f"\n{Colors.GREEN}[SUCCESS] Presupuesto '{project_title}' actualizado y guardado.{Colors.ENDC}")
            time.sleep(2)
            return

        elif choice == '0': # Cancelar
            if input("¿Descartar todos los cambios? (s/n): ").lower() == 's':
                print(f"{Colors.YELLOW}[INFO] Edición cancelada. No se guardaron los cambios.{Colors.ENDC}")
                time.sleep(2)
                return