# test_admin.py
import unittest
import os
import json
import shutil
from unittest.mock import patch
from componentes import modulo_admin

class TestAdmin(unittest.TestCase):
    def setUp(self):
        # Limpiar entorno de prueba
        if os.path.exists(modulo_admin.BASE_DIR):
            shutil.rmtree(modulo_admin.BASE_DIR)
        modulo_admin.inicializar_entorno_admin()

    def test_cronica_firma(self):
        """Verifica que las crónicas se registren y la firma coincida."""
        modulo_admin.registrar_cronica("Acción de prueba", "Richon")
        
        with open(modulo_admin.LOG_FILE, 'r', encoding='utf-8') as f:
            datos = json.load(f)
            self.assertEqual(len(datos), 1)
            entrada = datos[0]
            self.assertEqual(entrada["accion"], "Acción de prueba")
            
            # Verificar integridad de la firma
            firma_recalculada = modulo_admin._generar_firma_log(entrada)
            self.assertEqual(entrada["firma"], firma_recalculada)

    def test_crear_punto_restauracion(self):
        """Prueba la creación de un snapshot."""
        # Simular algunos archivos .py
        with open("fake_component.py", "w") as f: f.write("print('fake')")
        if not os.path.exists("componentes"): os.makedirs("componentes")
        with open("componentes/fake_sub.py", "w") as f: f.write("print('sub')")
        
        modulo_admin.crear_punto_restauracion()
        
        snapshots = os.listdir(modulo_admin.BACKUP_DIR)
        self.assertTrue(len(snapshots) > 0)
        
        # Limpiar fakes
        os.remove("fake_component.py")
        os.remove("componentes/fake_sub.py")

    @patch('builtins.input', side_effect=['1', 's']) # Selecciona snapshot 1 y confirma
    def test_restauracion(self, mock_input):
        """Prueba el flujo de restauración (simulado)."""
        # 1. Crear snapshot original
        with open("original.py", "w") as f: f.write("original")
        modulo_admin.crear_punto_restauracion()
        
        # 2. Modificar archivo
        with open("original.py", "w") as f: f.write("modificado")
        
        # 3. Restaurar
        modulo_admin.restaurar_sistema()
        
        # 4. Verificar
        with open("original.py", "r") as f:
            content = f.read()
            self.assertEqual(content, "original")
        
        # Limpiar
        os.remove("original.py")

if __name__ == '__main__':
    unittest.main()
