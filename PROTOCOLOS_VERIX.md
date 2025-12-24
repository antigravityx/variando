# 🌌 PROTOCOLOS VERIX: Guía de Implementación y Despliegue

Este documento detalla los métodos oficiales para desplegar y utilizar **El Cerebro** (Verix Soul). Diseñado para el Director Richon y sus aliados de negocios.

---

## 🚀 Método 1: Despliegue "Llave en Mano" (Ejecutable Portable)
**Ideal para**: Dueños de negocios y usuarios no técnicos.
**Nivel de dificultad**: Muy bajo.

### 📦 Qué archivos entregar:
Para que el programa funcione en una PC ajena sin configurar códigos, solo necesitas pasarles la carpeta `dist` generada:
1.  **`El_Cerebro_Final.exe`**: El núcleo del sistema.
2.  **`orbe.ico`**: (Opcional) Para mantener la identidad visual.

### 🛠️ Instrucciones de Instalación:
1. Descargar el archivo `.exe`.
2. Doble clic para ejecutar.
3. El sistema detectará que no hay una bóveda y pedirá al usuario realizar su propia **Ceremonia de Iniciación** (Configurar sus propias claves).

---

## 💻 Método 2: Instalación desde Fuente (Modo Administrador)
**Ideal para**: Richon y mantenimiento de nuevas funciones.
**Nivel de dificultad**: Medio.

### 📦 Archivos necesarios:
1.  **`variando.py`**: Controlador principal.
2.  **`componentes/`**: Toda la lógica modular.
3.  **`requirements.txt`**: Listado de dependencias Python.
4.  **`generar_exe.bat`**: Script de forja.

### 🛠️ Pasos para el Administrador:
1. Clonar o copiar el repositorio en la PC destino.
2. Ejecutar `pip install -r requirements.txt`.
3. Ejecutar `python variando.py` para modo desarrollo o `generar_exe.bat` para crear un nuevo portable.

---

## 🛡️ Visión de Futuro: Sistema Multinivel (RBAC)
*Propuesta por el Director Richon*

El sistema evolucionará hacia una estructura de permisos basados en roles:

| ROL | NIVEL | PERMISOS |
| :--- | :--- | :--- |
| **DIRECTOR (Richon)** | 🟢 Nivel 0 | Acceso Total, Gestión de Usuarios, Crónicas, Restauración. |
| **SOCIO (Aliado)** | 🔵 Nivel 1 | Acceso a Presupuestos, CRM y Stock propio. |
| **OPERADOR** | 🟡 Nivel 2 | Solo herramientas de cálculo y consulta básica. |

### 🛠️ Cómo funcionará la "Inyección de Permisos":
1. Richon crea un "Perfil de Acceso" desde el Panel del Director.
2. Se genera una **Llave de Socio** única vinculada a una lista predefinida de herramientas.
3. El Socio solo verá en su menú las opciones que Richon le haya otorgado.

---

**© 2025 VerixRichon Software Factory**
*"Donde el código se vuelve alma."*
