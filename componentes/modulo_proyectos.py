# componentes/modulo_proyectos.py
import os
import re
import json
from datetime import datetime
import time

from componentes.colores import Colors
from componentes.utilidades import format_and_describe_number

def consultar_precios_referencia():
    """Muestra una lista de precios de referencia para mano de obra."""
    log_output = "Consulta de precios de referencia."
    
    # Datos proporcionados por Richon
    precios = [
        ("Busqueda y reparación de corto circuitos", 34441.00, 74861.00),
        ("Certificado DCI", 79662.31, 122187.08),
        ("Colocación / cambio bomba presurizadora", 54600.00, 109000.00),
        ("Instalación boca eléctrica completa", 28205.00, 47039.00),
        ("Instalación eléctrica para aire acondicionado", 33600.00, 67000.00),
        ("Colocación / cambio tecla de encendido", 12385.00, 87167.00),
        ("Visita de diagnóstico / Presupuestación", 24861.00, 45920.00),
        ("Instalación de campana de extracción", 46092.00, 97734.00),
        ("Colocación pararrayos", 201558.00, 333560.00),
        ("Puesta a tierra / jabalina", 44047.41, 70638.15),
        ("Tramites conexión eléctrica", 71528.13, 104571.88),
        ("Instalación de detector de humo", 33657.00, 73912.00),
        ("Instalación portero eléctrico", 38648.00, 65698.00),
        ("Instalación de estufa eléctrica", 60517.00, 47738.00),
        ("Instalación de termotanque eléctrico", 46120.00, 70327.00),
        ("Instalación de anafe eléctrico", 27883.00, 45121.00),
        ("Instalación de horno eléctrico", 30740.00, 58035.00),
        ("Instalación de cocina eléctrica", 34508.00, 64074.00),
        ("Colocación ventilador de techo con luces", 47068.00, 75783.00),
        ("Colocación de ventilador de techo", 43045.00, 71862.00),
        ("Colocación de artefactos de iluminación por unidad", 13120.48, 30040.48),
        ("Colocación / cambio de tomacorriente", 13428.00, 21314.00),
        ("Cambio / instalacion de llave térmica", 23595.00, 36945.00),
        ("Cambio / instalacion de disyuntor", 25314.00, 39212.00)
    ]

    precios_aaieric = [
        ("AAIERIC - Visita: Diagnóstico y Presupuesto", 43043.00, 43043.00),
        ("AAIERIC - Urgencia (Lun-Sab >20hs / Dom / Fer)", 103191.00, 103191.00),
        ("AAIERIC - Unidad básica (1 boca completa)", 85935.00, 85935.00),
        ("AAIERIC - Service / Instalación mínima", 85935.00, 85935.00),
        ("AAIERIC - Hora de Trabajo", 43043.00, 43043.00),
        ("AAIERIC - Tablero en losa (caño met.)", 43505.00, 43505.00),
        ("AAIERIC - Tablero en loseta (caño met.)", 45680.00, 45680.00),
        ("AAIERIC - TP Monofásico (1 ID, 1 TM + PAT)", 253859.00, 253859.00),
        ("AAIERIC - TP Trifásico (1 ID, 1 TM + PAT)", 343773.00, 343773.00),
        ("AAIERIC - Amurado cañería (Ladrillo común)", 49441.00, 49441.00),
        ("AAIERIC - Amurado cañería (Ladrillo hueco)", 48266.00, 48266.00),
        ("AAIERIC - Amurado cañería vista (Metal/PVC)", 39517.00, 39517.00),
        ("AAIERIC - Pase de viga/columna", 45886.00, 45886.00),
        ("AAIERIC - Cable subterráneo (Tierra/Piso)", 43003.00, 45886.00),
        ("AAIERIC - Caja de paso adicional", 47225.00, 50428.00),
        ("AAIERIC - Cableado obra nueva (Opción 1)", 21144.00, 21144.00),
        ("AAIERIC - Cableado obra nueva (Opción 2)", 29442.00, 29442.00),
        ("AAIERIC - Recableado con artefactos", 44150.00, 44150.00),
        ("AAIERIC - Recableado sin artefactos", 29442.00, 29442.00),
        ("AAIERIC - Conexión: Punto/Toma/Portalámpara", 15347.00, 15347.00),
        ("AAIERIC - Conexión: Toma doble", 19437.00, 19437.00),
        ("AAIERIC - Conexión: Punto Combinación", 16518.00, 16518.00),
        ("AAIERIC - Artefacto aplique simple / Spot Led", 23550.00, 23550.00),
        ("AAIERIC - Colgante liviano (3 luces)", 47102.00, 47102.00),
        ("AAIERIC - Colgante liviano (5 luces)", 62397.00, 62397.00),
        ("AAIERIC - Colgante pesado (Mínimo)", 82406.00, 82406.00),
        ("AAIERIC - Tubo Led simple (7-36W)", 47102.00, 47102.00),
        ("AAIERIC - Tubo Led doble (7-36W)", 57982.00, 57982.00),
        ("AAIERIC - Tubo Led (45W)", 58901.00, 58901.00),
        ("AAIERIC - Tubo Led doble (45W)", 73091.00, 73091.00),
        ("AAIERIC - Ventilador de techo", 85935.00, 85935.00),
        ("AAIERIC - Ventilador de techo con luz", 107453.00, 107453.00),
        ("AAIERIC - Acometida: Gabinete 1 Medidor Mono", 180424.00, 180424.00),
        ("AAIERIC - Acometida: Pilar completo", 708895.00, 708895.00),
        ("AAIERIC - Acometida: Caño (amurado+conexión)", 180424.00, 180424.00),
        ("AAIERIC - PAT de Servicio (Jabalina+Caja)", 128855.00, 128855.00),
        ("AAIERIC - Automatismo: Contactores", 107453.00, 107453.00),
        ("AAIERIC - Automatismo: Sensores", 94530.00, 94530.00),
        ("AAIERIC - Proyecto Eléctrico (Mínimo)", 437623.00, 437623.00),
        ("AAIERIC - Bandeja <150mm H<3m (x metro)", 10433.00, 10433.00),
        ("AAIERIC - Bandeja <150mm H>3m (x metro)", 13931.00, 13931.00),
        ("AAIERIC - Jornal (8hs): Oficial Especializado", 75251.00, 75251.00),
        ("AAIERIC - Jornal (8hs): Oficial Electricista", 64124.00, 64124.00),
        ("AAIERIC - Jornal (8hs): Ayudante", 54274.00, 54274.00),
        ("AAIERIC - Certificado DCI T1 Mono (Res/Com)", 330000.00, 330000.00),
        ("AAIERIC - Certificado DCI T1 Trifásico", 495000.00, 495000.00),
        ("AAIERIC - Emergencia (Atención inmediata)", 85935.00, 85935.00),
        ("AAIERIC - Grupo Electrógeno Mono (<3.5kVA)", 214876.00, 214876.00)
    ]
    
    precios_electro = [
        ("ELECTRO - Acometida Mono hasta 10 kW", 185500.00, 185500.00),
        ("ELECTRO - Acometida Trifásica hasta 10 kW", 264700.00, 264700.00),
        ("ELECTRO - Acometida Trifásica 11-35 kW", 343600.00, 343600.00),
        ("ELECTRO - Acometida Trifásica 36-50 kW", 501600.00, 501600.00),
        ("ELECTRO - Cableado en cañería nueva (1-50 bocas)", 29400.00, 29400.00),
        ("ELECTRO - Cableado en cañería nueva (51-100 bocas)", 28400.00, 28400.00),
        ("ELECTRO - Cableado en cañería nueva (101-500 bocas)", 28200.00, 28200.00),
        ("ELECTRO - Subterráneo 1x4 a 4x16 mm2", 18800.00, 18800.00),
        ("ELECTRO - Subterráneo 1x25 a 4x35 mm2", 37700.00, 37700.00),
        ("ELECTRO - Subterráneo 1x35 a 4x70 mm2", 67400.00, 67400.00),
        ("ELECTRO - Subterráneo mayor a 1x95 mm2", 89800.00, 89800.00),
        ("ELECTRO - Re-cableado (1-50 bocas)", 36300.00, 36300.00),
        ("ELECTRO - Re-cableado (51-100 bocas)", 34600.00, 34600.00),
        ("ELECTRO - Re-cableado (101-500 bocas)", 30500.00, 30500.00),
        ("ELECTRO - Canalización Embutida Metálica (1-50)", 45700.00, 45700.00),
        ("ELECTRO - Canalización Embutida Metálica (51-100)", 44800.00, 44800.00),
        ("ELECTRO - Canalización Embutida PVC (1-50)", 44800.00, 44800.00),
        ("ELECTRO - Canalización Embutida PVC (51-100)", 43600.00, 43600.00),
        ("ELECTRO - Canalización Vista Metálica (1-50)", 43600.00, 43600.00),
        ("ELECTRO - Canalización Vista Metálica (51-100)", 42700.00, 42700.00),
        ("ELECTRO - Canalización Vista PVC (1-50)", 42700.00, 42700.00),
        ("ELECTRO - Canalización Vista PVC (51-100)", 41800.00, 41800.00),
        ("ELECTRO - Metálica 3/4 en Durlock (1-50)", 38000.00, 38000.00),
        ("ELECTRO - Metálica 3/4 en Durlock (51-100)", 34100.00, 34100.00),
        ("ELECTRO - PVC Rígido 3/4 en Durlock (1-50)", 34600.00, 34600.00),
        ("ELECTRO - PVC Rígido 3/4 en Durlock (51-100)", 32300.00, 32300.00),
        ("ELECTRO - Bandeja Metálica 300mm (<2m)", 43200.00, 43200.00),
        ("ELECTRO - Bandeja Metálica 300mm (3-5m)", 47000.00, 47000.00),
        ("ELECTRO - Bandeja Metálica 300mm (6-10m)", 51700.00, 51700.00),
        ("ELECTRO - Bandeja Metálica 450mm (<2m)", 47000.00, 47000.00),
        ("ELECTRO - Bandeja Metálica 450mm (3-5m)", 51700.00, 51700.00),
        ("ELECTRO - Bandeja Metálica 450mm (6-10m)", 56800.00, 56800.00),
        ("ELECTRO - Bandeja Metálica 600mm (<2m)", 52300.00, 52300.00),
        ("ELECTRO - Bandeja Metálica 600mm (3-5m)", 56800.00, 56800.00),
        ("ELECTRO - Bandeja Metálica 600mm (6-10m)", 62300.00, 62300.00),
        ("ELECTRO - Cablecanal Accesorios (1-50 bocas)", 40700.00, 40700.00),
        ("ELECTRO - Cablecanal metro adicional", 14000.00, 14000.00),
        ("ELECTRO - Pisoducto instalación x metro", 33700.00, 33700.00),
        ("ELECTRO - Pisoducto Cajas/Derivación", 49900.00, 49900.00),
        ("ELECTRO - Pisoducto Curvas", 39600.00, 39600.00),
        ("ELECTRO - Pisoducto Periscopios", 47100.00, 47100.00),
        ("ELECTRO - Pisoducto Cableado Energía", 44600.00, 44600.00),
        ("ELECTRO - Pisoducto Instalación Tomas", 32900.00, 32900.00),
        ("ELECTRO - CCTV Superficie x cámara", 73800.00, 73800.00),
        ("ELECTRO - CCTV Superficie BCR 3 cámaras", 257500.00, 257500.00),
        ("ELECTRO - CCTV Canalizado x cámara", 105900.00, 105900.00),
        ("ELECTRO - CCTV Canalizado BCR 3 cámaras", 307900.00, 307900.00),
        ("ELECTRO - Aplique 1-2 luces", 25000.00, 25000.00),
        ("ELECTRO - Aplique 3-5 luces", 28000.00, 28000.00),
        ("ELECTRO - Colgante 1 luz", 41000.00, 41000.00),
        ("ELECTRO - Colgante 2 luces", 44000.00, 44000.00),
        ("ELECTRO - Farola pared 1 luz", 45000.00, 45000.00),
        ("ELECTRO - Artefacto Tubo LED simple", 47000.00, 47000.00),
        ("ELECTRO - Artefacto Tubo LED doble", 57000.00, 57000.00),
        ("ELECTRO - Luz de emergencia", 37000.00, 37000.00),
        ("ELECTRO - Brazo alumbrado público", 158000.00, 158000.00),
        ("ELECTRO - Extractor baño", 136000.00, 136000.00),
        ("ELECTRO - Extractor cocina", 193000.00, 193000.00),
        ("ELECTRO - Campana tipo spar", 126000.00, 126000.00),
        ("ELECTRO - Ventilador techo s/luces", 83000.00, 83000.00),
        ("ELECTRO - Ventilador techo c/luces", 106000.00, 106000.00),
        ("ELECTRO - Tablero Mono hasta 2 Kvar", 245000.00, 245000.00),
        ("ELECTRO - Tablero Tri hasta 10 Kvar", 276500.00, 276500.00),
        ("ELECTRO - Tablero Tri c/contactor 10 Kvar", 390900.00, 390900.00),
        ("ELECTRO - Tablero Tri Auto 50 Kvar", 471500.00, 471500.00),
        ("ELECTRO - Tablero Domiciliario Superficie (1-54)", 40500.00, 40500.00),
        ("ELECTRO - Tablero Domiciliario Empotrado (1-24)", 170500.00, 170500.00),
        ("ELECTRO - Colocación Termomagnética/Diferencial Mono", 75300.00, 75300.00),
        ("ELECTRO - Colocación Termomagnética/Diferencial Tri", 99300.00, 99300.00),
        ("ELECTRO - Emergencia Lun-Vie <5km (x hora)", 57700.00, 57700.00),
        ("ELECTRO - Emergencia Sab-Dom <5km (x hora)", 80500.00, 80500.00),
        ("ELECTRO - UOCRA Oficial Especializado (x hora)", 5771.00, 5771.00),
        ("ELECTRO - UOCRA Oficial Electricista (x hora)", 4700.00, 4700.00),
        ("ELECTRO - UOCRA Ayudante (x hora)", 3817.00, 3817.00),
        ("ELECTRO - Proyecto Eléctrico (hasta 25 bocas)", 356900.00, 356900.00),
        ("ELECTRO - Puesta a Tierra (Jabalina+Caja)", 87000.00, 87000.00)
    ]

    precios.extend(precios_aaieric)
    precios.extend(precios_electro)

    while True:
        print(f"\n{Colors.MAGENTA}--- Lista de Precios de Referencia (Mano de Obra) ---{Colors.ENDC}")
        print(f"{Colors.YELLOW}[INFO] Estos precios son orientativos. Úsalos como guía.{Colors.ENDC}")
        
        search = input("\n>> Buscar servicio (o presiona Enter para ver todos, 'v' para volver): ").lower().strip()
        
        if search == 'v':
            break
            
        print(f"\n{Colors.BOLD}{'Servicio':<55}{'Mínimo':<15}{'Máximo':<15}{Colors.ENDC}")
        print("-" * 85)
        
        found = False
        for item in precios:
            servicio, min_p, max_p = item
            if search in servicio.lower():
                found = True
                min_str = f"$ {min_p:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                max_str = f"$ {max_p:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                print(f"{servicio:<55}{Colors.GREEN}{min_str:<15}{Colors.ENDC}{Colors.CYAN}{max_str:<15}{Colors.ENDC}")
        
        if not found:
            print(f"{Colors.RED}No se encontraron servicios que coincidan con '{search}'.{Colors.ENDC}")
            
        input("\n--- Presiona Enter para realizar otra consulta ---")

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
    
    clean_output = [re.sub(r'\033\[[0-9;]*m', '', line) for line in output]
    
    return clean_output

def calculadora_proyectos_detallada():
    """Calcula un presupuesto detallado desglosando costos de fabricación, ganancia e instalación."""
    log_output = "Iniciada Calculadora de Proyectos Detallada."
    print(f"\n{Colors.CYAN}--- Calculadora de Proyectos (Detallada) ---{Colors.ENDC}")
    print("Ideal para presupuestos complejos con desglose de costos.")

    while True:
        try:
            print(f"\n{Colors.MAGENTA}PASO 0: Identificación del Proyecto.{Colors.ENDC}")
            project_title = input(">> Introduce un título o alias para este presupuesto (ej: Cartel Luminoso Calle 123): ").strip()
            if not project_title:
                print(f"{Colors.RED}[ERROR] El título es obligatorio para guardar el presupuesto.{Colors.ENDC}")
                continue
            
            base = float(input(">> Introduce la medida de la BASE del proyecto (ej: 4.5): ").strip() or "0")
            altura = float(input(">> Introduce la medida de la ALTURA del proyecto (ej: 2.3): ").strip() or "0")
            
            budget_output = []

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

            print(f"\n{Colors.MAGENTA}PASO 2: Margen de ganancia.{Colors.ENDC}")
            margen_ganancia_pct = float(input(">> ¿Qué porcentaje de ganancia quieres añadir sobre la fabricación? (ej: 30): ").strip() or "0")
            
            print(f"\n{Colors.MAGENTA}PASO 3: Costo de instalación.{Colors.ENDC}")
            costo_instalacion = 0
            if input(">> ¿La instalación tiene un costo aparte? (s/n): ").lower() == 's':
                costo_instalacion = float(input(">> Introduce el costo total de la instalación: $ ").strip())

            ganancia_fabricacion = costo_fabricacion_total * (margen_ganancia_pct / 100)
            subtotal_producto = costo_fabricacion_total + ganancia_fabricacion
            precio_venta_cliente = subtotal_producto + costo_instalacion
            ganancia_total = precio_venta_cliente - (costo_fabricacion_total + costo_instalacion)

            budget_output = generar_texto_presupuesto(
                project_title, items_costo, costo_fabricacion_total, margen_ganancia_pct, 
                ganancia_fabricacion, costo_instalacion, precio_venta_cliente, ganancia_total
            )
            colored_output = "\n".join(budget_output)
            total_f_str = format_and_describe_number(precio_venta_cliente)[0]
            colored_output = colored_output.replace(f"$ {total_f_str}", f"{Colors.GREEN}{Colors.BOLD}$ {total_f_str}{Colors.ENDC}")
            print(colored_output)

            budget_dir = "presupuestos"
            os.makedirs(budget_dir, exist_ok=True)
            safe_title = re.sub(r'[^\w\s-]', '', project_title).strip().replace(' ', '_')
            filename = os.path.join(budget_dir, f"{safe_title}.txt")
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("\n".join(budget_output))
            
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

def calculadora_presupuestos():
    """Calcula el área y el costo de un proyecto basado en dimensiones y precios."""
    log_output = "Iniciada Calculadora de Presupuestos."
    print(f"\n{Colors.CYAN}--- Calculadora de Costos por Superficie ---{Colors.ENDC}")
    print("Calcula el costo total para un área (materiales o mano de obra).")

    while True:
        costo_base = 0
        area = 0
        try:
            base = float(input("\n>> Introduce la medida de la BASE (ej: 4.5): "))
            altura = float(input(">> Introduce la medida de la ALTURA (ej: 2.3): "))
            area = base * altura

            costo_base = float(input(f"{Colors.YELLOW}>> Introduce el COSTO BASE por m² (Material o Mano de Obra): {Colors.ENDC}"))

            margen_pct = float(input(f"{Colors.YELLOW}>> Introduce el margen de ganancia a añadir (%) (ej: 30): {Colors.ENDC}") or "0")

            costo_total_fabricacion = area * costo_base
            ganancia = costo_total_fabricacion * (margen_pct / 100)
            precio_venta_final = costo_total_fabricacion + ganancia

            costo_base_f, _ = format_and_describe_number(costo_base)
            costo_total_f, _ = format_and_describe_number(costo_total_fabricacion)
            precio_venta_f, precio_venta_palabras = format_and_describe_number(precio_venta_final)
            ganancia_f, _ = format_and_describe_number(ganancia)

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

def calculadora_por_artefactos():
    """Calcula el costo y los materiales necesarios para ensamblar múltiples artefactos idénticos."""
    log_output = "Iniciada Calculadora por Artefactos."
    print(f"\n{Colors.CYAN}--- Calculadora de Presupuestos por Artefactos ---{Colors.ENDC}")
    print("Define los componentes de UN artefacto y luego calcula el total para varios.")

    while True:
        try:
            nombre_artefacto = input("\n>> Introduce el nombre del artefacto (ej: Caja de luz, Tablero): ").strip()
            if not nombre_artefacto:
                print(f"{Colors.RED}[ERROR] El nombre es obligatorio.{Colors.ENDC}")
                continue

            print(f"\n{Colors.MAGENTA}--- Componentes para UN/A '{nombre_artefacto}' ---{Colors.ENDC}")
            componentes = []
            while True:
                nombre_item = input("  >> Nombre del componente (o 'fin' para terminar): ").strip()
                if nombre_item.lower() == 'fin':
                    if not componentes:
                        print(f"{Colors.YELLOW}[INFO] No se añadieron componentes. Volviendo...{Colors.ENDC}")
                        break
                    else:
                        break
                
                costo_item = float(input(f"     - Precio de costo de '{nombre_item}': $ ").strip())
                cantidad_item = int(input(f"     - ¿Cuántos '{nombre_item}' lleva UN/A '{nombre_artefacto}'?: ").strip())
                
                componentes.append({
                    'nombre': nombre_item, 
                    'costo_unitario': costo_item, 
                    'cantidad_por_artefacto': cantidad_item
                })
                print(f"{Colors.GREEN}   -> Componente añadido.{Colors.ENDC}")

            if not componentes:
                break

            total_artefactos = int(input(f"\n>> ¿Cuántos artefactos '{nombre_artefacto}' necesitas armar en total?: ").strip())

            costo_un_artefacto = 0
            lista_compras = {}

            for item in componentes:
                costo_un_artefacto += item['costo_unitario'] * item['cantidad_por_artefacto']
                
                cantidad_total_item = item['cantidad_por_artefacto'] * total_artefactos
                lista_compras[item['nombre']] = lista_compras.get(item['nombre'], 0) + cantidad_total_item
            
            costo_total_proyecto = costo_un_artefacto * total_artefactos

            costo_unitario_f, _ = format_and_describe_number(costo_un_artefacto)
            costo_total_f, _ = format_and_describe_number(costo_total_proyecto)

            print(f"\n{Colors.BOLD}{Colors.GREEN}--- RESULTADO PARCIAL (ARTEFACTOS) ---{Colors.ENDC}")
            print(f"  - {'Artefacto base:':<30} {nombre_artefacto}")
            print(f"  - {'Costo por CADA artefacto:':<30} {Colors.YELLOW}$ {costo_unitario_f}{Colors.ENDC}")
            print(f"  - {'Cantidad total de artefactos:':<30} {total_artefactos}")
            print("-" * 50)
            print(f"  {Colors.BOLD}{'SUBTOTAL ARTEFACTOS:':<30}{Colors.ENDC} {Colors.GREEN}{Colors.BOLD}$ {costo_total_f}{Colors.ENDC}")

            costo_total_cables = 0
            lista_cables = []
            
            print(f"\n{Colors.MAGENTA}--- FASE 2: CABLEADO Y CONEXIONES ---{Colors.ENDC}")
            agregar_cables = input(f">> ¿Quieres agregar cables a este presupuesto? (s/n): ").lower().strip()
            
            if agregar_cables == 's':
                print(f"{Colors.CYAN}Introduce los cables necesarios (ej: 1.5mm, 2.5mm, Sintenax, etc.){Colors.ENDC}")
                while True:
                    tipo_cable = input("  >> Tipo de cable (o 'fin'): ").strip()
                    if tipo_cable.lower() == 'fin':
                        break
                    
                    try:
                        costo_metro = float(input(f"     - Costo por metro de '{tipo_cable}': $ ").strip())
                        metros = float(input(f"     - Cantidad de metros lineales: ").strip())
                        
                        subtotal_cable = costo_metro * metros
                        costo_total_cables += subtotal_cable
                        
                        lista_cables.append({
                            'tipo': tipo_cable,
                            'costo_metro': costo_metro,
                            'metros': metros,
                            'subtotal': subtotal_cable
                        })
                        print(f"{Colors.GREEN}   -> Cable añadido al presupuesto.{Colors.ENDC}")
                    except ValueError:
                        print(f"{Colors.RED}[ERROR] Introduce números válidos.{Colors.ENDC}")

            gran_total = costo_total_proyecto + costo_total_cables
            gran_total_f, gran_total_palabras = format_and_describe_number(gran_total)
            costo_cables_f, _ = format_and_describe_number(costo_total_cables)

            print(f"\n{Colors.BOLD}{Colors.GREEN}=== RESUMEN FINAL DEL PROYECTO ==={Colors.ENDC}")
            print(f"  1. Total Artefactos ({total_artefactos} u.): {Colors.YELLOW}$ {costo_total_f}{Colors.ENDC}")
            if costo_total_cables > 0:
                print(f"  2. Total Cableado:              {Colors.YELLOW}$ {costo_cables_f}{Colors.ENDC}")
            print("-" * 50)
            print(f"  {Colors.BOLD}TOTAL GENERAL:{Colors.ENDC}                  {Colors.GREEN}{Colors.BOLD}$ {gran_total_f}{Colors.ENDC}")
            print(f"  {Colors.CYAN}{gran_total_palabras}{Colors.ENDC}")

            print(f"\n{Colors.CYAN}{Colors.BOLD}--- LISTA DE COMPRAS CONSOLIDADA ---{Colors.ENDC}")
            print(f"  {Colors.BOLD}A) Componentes para {total_artefactos} {nombre_artefacto}(s):{Colors.ENDC}")
            for nombre, cantidad in sorted(lista_compras.items()):
                print(f"     - {cantidad} x {nombre}")
            
            if lista_cables:
                print(f"  {Colors.BOLD}B) Cables:{Colors.ENDC}")
                for cab in lista_cables:
                    print(f"     - {cab['metros']} mts x Cable {cab['tipo']}")

            log_output += f"\n  └─ Proyecto '{nombre_artefacto}': Artefactos=${costo_total_f} + Cables=${costo_cables_f} = Total ${gran_total_f}"

            guardar = input(f"\n{Colors.MAGENTA}>> ¿Quieres GUARDAR este presupuesto en un archivo? (s/n): {Colors.ENDC}").lower().strip()
            
            if guardar == 's':
                lines = []
                lines.append(f"--- PRESUPUESTO DE PROYECTO: {nombre_artefacto.upper()} + CABLEADO ---")
                lines.append(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
                lines.append("\n--- A) ARTEFACTOS ---")
                lines.append(f"Artefacto Base: {nombre_artefacto}")
                lines.append(f"Componentes por unidad:")
                for item in componentes:
                    lines.append(f"  - {item['cantidad_por_artefacto']} x {item['nombre']} ($ {item['costo_unitario']:.2f} c/u)")
                lines.append(f"Costo unitario armado: $ {costo_unitario_f}")
                lines.append(f"Cantidad total: {total_artefactos}")
                lines.append(f"SUBTOTAL ARTEFACTOS: $ {costo_total_f}")
                
                if lista_cables:
                    lines.append("\n--- B) CABLEADO ---")
                    for cab in lista_cables:
                        lines.append(f"  - {cab['tipo']}: {cab['metros']} mts x $ {cab['costo_metro']:.2f} = $ {cab['subtotal']:,.2f}")
                    lines.append(f"SUBTOTAL CABLEADO: $ {costo_cables_f}")
                
                lines.append("\n" + "="*40)
                lines.append(f"TOTAL GENERAL DEL PROYECTO: $ {gran_total_f}")
                lines.append(gran_total_palabras)
                lines.append("="*40)
                
                lines.append("\n--- LISTA DE COMPRAS CONSOLIDADA ---")
                for nombre, cantidad in sorted(lista_compras.items()):
                    lines.append(f"  [ ] {cantidad} x {nombre}")
                if lista_cables:
                    for cab in lista_cables:
                        lines.append(f"  [ ] {cab['metros']} mts x Cable {cab['tipo']}")

                budget_dir = "presupuestos"
                if not os.path.exists(budget_dir):
                    os.makedirs(budget_dir)
                
                safe_name = re.sub(r'[^\w\s-]', '', nombre_artefacto).strip().replace(' ', '_')
                filename = f"{budget_dir}/Proyecto_{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(lines))
                
                print(f"\n{Colors.GREEN}[SUCCESS] Presupuesto guardado en: {filename}{Colors.ENDC}")

        except ValueError:
            print(f"{Colors.RED}[ERROR] Entrada no válida. Por favor, introduce solo números donde se pida.{Colors.ENDC}")
        
        if input("\n>> ¿Hacer otro cálculo por artefactos? (s/n): ").lower() != 's':
            break
            
    return log_output

def cerebro_numerico():
    """Módulo con herramientas de cálculo matemático."""
    log_output = "Iniciado Cerebro Numérico."
    
    while True:
        print(f"\n{Colors.MAGENTA}--- Cerebro Numérico ---{Colors.ENDC}")
        print("  1. Calculadora Estándar")
        print("  2. Calculadora de Porcentajes")
        print(f"  3. Calculadora de Costos por Superficie")
        print(f"  {Colors.GREEN}4. Calculadora de Proyectos (Detallada){Colors.ENDC}")
        print(f"  {Colors.CYAN}5. Calculadora por Artefactos{Colors.ENDC}")
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

        elif choice == '5':
            log = calculadora_por_artefactos()
            log_output += f"\n  └─ {log}"

        elif choice == '0':
            break
        else:
            print(f"\n{Colors.RED}[ERROR] Opción no válida.{Colors.ENDC}")
            time.sleep(1)
            
    return log_output