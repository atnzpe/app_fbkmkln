import pytest
import numpy as np
import os
import sys

# IMPORTANTE: Adiciona o diretório raiz do projeto ao sys.path para importações.
# Isso garante que você possa importar src.utils corretamente.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Importa a função calculate_angle do seu módulo src.utils
from src.utils import calculate_angle, setup_logging

# Configura o logger para este módulo de teste
logger = setup_logging()

class TestCalculateAngle:
    """
    Classe de testes para a função calculate_angle em src/utils.py.
    Esta classe garante que a função de cálculo de ângulo, crucial para a análise
    de poses, funcione corretamente sob diversas condições.
    """

    def test_straight_line_180_degrees(self):
        """
        Testa o cálculo do ângulo para pontos que formam uma linha reta (180 graus).
        Isso simula, por exemplo, um braço totalmente esticado.
        """
        logger.info("Executando test_straight_line_180_degrees...")
        # Pontos alinhados no eixo X
        p1 = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        p2 = {'x': 0.5, 'y': 0.0, 'z': 0.0}
        p3 = {'x': 1.0, 'y': 0.0, 'z': 0.0}
        
        angle = calculate_angle(p1, p2, p3)
        # Usamos pytest.approx para comparar floats, pois pode haver pequenas imprecisões.
        assert angle == pytest.approx(180.0, abs=0.01)
        logger.info(f"Ângulo para 180 graus: {angle:.2f} graus. Teste PASSED.")

    def test_right_angle_90_degrees(self):
        """
        Testa o cálculo do ângulo para pontos que formam um ângulo reto (90 graus).
        Simula, por exemplo, um cotovelo flexionado em 90 graus.
        """
        logger.info("Executando test_right_angle_90_degrees...")
        # Pontos formando um L no plano XY
        p1 = {'x': 0.0, 'y': 1.0, 'z': 0.0}
        p2 = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        p3 = {'x': 1.0, 'y': 0.0, 'z': 0.0}
        
        angle = calculate_angle(p1, p2, p3)
        assert angle == pytest.approx(90.0, abs=0.01)
        logger.info(f"Ângulo para 90 graus: {angle:.2f} graus. Teste PASSED.")

    def test_acute_angle_45_degrees(self):
        """
        Testa o cálculo de um ângulo agudo (45 graus).
        """
        logger.info("Executando test_acute_angle_45_degrees...")
        # Pontos para um ângulo de 45 graus (aprox.)
        p1 = {'x': 0.0, 'y': 1.0, 'z': 0.0}
        p2 = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        p3 = {'x': 1.0, 'y': 1.0, 'z': 0.0} # Este ponto forma 45 graus com (0,0) e (0,1)
        
        angle = calculate_angle(p1, p2, p3)
        assert angle == pytest.approx(45.0, abs=0.01)
        logger.info(f"Ângulo para 45 graus: {angle:.2f} graus. Teste PASSED.")

    def test_obtuse_angle_135_degrees(self):
        """
        Testa o cálculo de um ângulo obtuso (135 graus).
        """
        logger.info("Executando test_obtuse_angle_135_degrees...")
        # Pontos para um ângulo de 135 graus.
        p1 = {'x': 0.0, 'y': 1.0, 'z': 0.0}
        p2 = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        # CORREÇÃO AQUI: Altere p3 para que o ângulo seja 135 graus
        p3 = {'x': -1.0, 'y': -1.0, 'z': 0.0} # Este ponto forma 135 graus com (0,0,0) e (0,1,0)
        
        angle = calculate_angle(p1, p2, p3)
        assert angle == pytest.approx(135.0, abs=0.01)
        logger.info(f"Ângulo para 135 graus: {angle:.2f} graus. Teste PASSED.")


    def test_points_coincident(self):
        """
        Testa o caso onde pontos são coincidentes (vetores nulos), esperando 0.0 graus.
        A função deve lidar com isso graciosamente para evitar erros de divisão por zero.
        """
        logger.info("Executando test_points_coincident...")
        p1 = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        p2 = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        p3 = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        
        angle = calculate_angle(p1, p2, p3)
        assert angle == pytest.approx(0.0, abs=0.01)
        logger.info(f"Ângulo para pontos coincidentes: {angle:.2f} graus. Teste PASSED.")

    def test_points_with_z_coordinate(self):
        """
        Testa o cálculo do ângulo com coordenadas Z não nulas (em 3D).
        """
        logger.info("Executando test_points_with_z_coordinate...")
        p1 = {'x': 1.0, 'y': 0.0, 'z': 1.0}
        p2 = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        p3 = {'x': 0.0, 'y': 1.0, 'z': 1.0}
        
        # Este ângulo é de 90 graus se projetado no plano YZ ou XZ,
        # mas em 3D, precisamos calcular as distâncias e produto escalar corretamente.
        # Vetores: v1 = (1,0,1), v2 = (0,1,1)
        # Produto escalar = 1*0 + 0*1 + 1*1 = 1
        # Mag v1 = sqrt(1^2+0^2+1^2) = sqrt(2)
        # Mag v2 = sqrt(0^2+1^2+1^2) = sqrt(2)
        # cos(angle) = 1 / (sqrt(2) * sqrt(2)) = 1 / 2 = 0.5
        # angle = arccos(0.5) = 60 graus
        angle = calculate_angle(p1, p2, p3)
        assert angle == pytest.approx(60.0, abs=0.01)
        logger.info(f"Ângulo 3D para (1,0,1)-(0,0,0)-(0,1,1): {angle:.2f} graus. Teste PASSED.")

    def test_p1_equals_p2(self):
        """
        Testa o cenário onde o primeiro ponto é igual ao ponto do vértice.
        Deve retornar 0.0 devido a um vetor nulo.
        """
        logger.info("Executando test_p1_equals_p2...")
        p1 = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        p2 = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        p3 = {'x': 1.0, 'y': 1.0, 'z': 1.0}
        
        angle = calculate_angle(p1, p2, p3)
        assert angle == pytest.approx(0.0, abs=0.01)
        logger.info(f"Ângulo para p1=p2: {angle:.2f} graus. Teste PASSED.")

    def test_p3_equals_p2(self):
        
        """
        Testa o cenário onde o terceiro ponto é igual ao ponto do vértice.
        Deve retornar 0.0 devido a um vetor nulo.
        """
        logger.info("Executando test_p3_equals_p2...")
        p1 = {'x': 1.0, 'y': 1.0, 'z': 1.0}
        p2 = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        p3 = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        
        angle = calculate_angle(p1, p2, p3)
        assert angle == pytest.approx(0.0, abs=0.01)
        logger.info(f"Ângulo para p3=p2: {angle:.2f} graus. Teste PASSED.")