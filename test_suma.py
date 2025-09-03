import unittest

class TestSuma(unittest.TestCase):
    def test_suma_basica(self):
        """Test básico para verificar la función de suma"""
        from suma import sumar  # Importamos la función a probar
        
        # Casos de prueba
        self.assertEqual(sumar(2, 3), 5)
        self.assertEqual(sumar(-1, 1), 0)
        self.assertEqual(sumar(0, 0), 0)
    
    def test_suma_flotantes(self):
        """Test para sumar números flotantes"""
        from suma import sumar
        
        self.assertAlmostEqual(sumar(2.5, 3.5), 6.0)

if __name__ == '__main__':
    unittest.main()