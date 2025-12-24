# test_rbac.py
import unittest
import os
import json
import hashlib
from unittest.mock import patch
from componentes import modulo_seguridad

class TestRBAC(unittest.TestCase):
    def setUp(self):
        # Asegurar una bóveda limpia para los tests
        self.archivo = "boveda_celador.json"
        if os.path.exists(self.archivo):
            os.remove(self.archivo)
        
        # Inicializar bóveda de prueba
        self.boveda = {
            "director": "Richon",
            "hash_key1": hashlib.sha256(b"k1").hexdigest(),
            "hash_key2": hashlib.sha256(b"k2").hexdigest(),
            "usuarios_adicionales": [
                {
                    "nombre": "Socio1",
                    "nivel": 1,
                    "pin_hash": hashlib.sha256(b"1111").hexdigest()
                },
                {
                    "nombre": "Operador1",
                    "nivel": 2,
                    "pin_hash": hashlib.sha256(b"2222").hexdigest()
                }
            ]
        }
        with open(self.archivo, 'w', encoding='utf-8') as f:
            json.dump(self.boveda, f)

    def test_login_director(self):
        """Verifica que el Director loguea con nivel 0."""
        with patch('builtins.input', side_effect=['Richon', 'k1', 'k2']):
            with patch('componentes.modulo_seguridad.input_con_mascara', side_effect=['k1', 'k2']):
                user = modulo_seguridad.login_sistema()
                self.assertIsNotNone(user)
                self.assertEqual(user['nivel'], 0)
                self.assertEqual(user['nombre'], "Richon")

    def test_login_socio(self):
        """Verifica que un Socio loguea con nivel 1."""
        with patch('builtins.input', side_effect=['Socio1']):
            with patch('componentes.modulo_seguridad.input_con_mascara', side_effect=['1111']):
                user = modulo_seguridad.login_sistema()
                self.assertIsNotNone(user)
                self.assertEqual(user['nivel'], 1)
                self.assertEqual(user['nombre'], "Socio1")

    def test_login_operador(self):
        """Verifica que un Operador loguea con nivel 2."""
        with patch('builtins.input', side_effect=['Operador1']):
            with patch('componentes.modulo_seguridad.input_con_mascara', side_effect=['2222']):
                user = modulo_seguridad.login_sistema()
                self.assertIsNotNone(user)
                self.assertEqual(user['nivel'], 2)
                self.assertEqual(user['nombre'], "Operador1")

    def test_login_fallido(self):
        """Verifica que un PIN incorrecto deniega el acceso."""
        with patch('builtins.input', side_effect=['Operador1']):
            with patch('componentes.modulo_seguridad.input_con_mascara', side_effect=['wrong']):
                user = modulo_seguridad.login_sistema()
                self.assertIsNone(user)

if __name__ == '__main__':
    unittest.main()
