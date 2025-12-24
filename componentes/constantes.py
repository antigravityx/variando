# componentes/constantes.py
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