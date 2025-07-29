# -*- coding: utf-8 -*-

# --------------------------------------------------------------------------------------------------
#  Krav Maga Motion Analyzer - Testes
#  version 1.1.0
#  Copyright (C) 2024,
#  開発者名 [Sujeito Programador]
# --------------------------------------------------------------------------------------------------

# --------------------------------------------------------------------------------------------------
# Importação de Bibliotecas
# --------------------------------------------------------------------------------------------------
import pytest  # Framework de testes para Python.
import numpy as np  # Biblioteca NumPy para manipulação de dados numéricos.
from unittest.mock import MagicMock  # Para criar objetos "mock" que simulam landmarks.

# Importa a classe que queremos testar.
# O caminho é relativo à raiz do projeto.
from src.motion_comparator import MotionComparator

# --------------------------------------------------------------------------------------------------
# Fixtures e Dados de Teste
# --------------------------------------------------------------------------------------------------

@pytest.fixture
def motion_comparator():
    """
    Cria uma instância do MotionComparator para ser usada em cada teste.
    Fixtures são funções que o pytest executa antes de cada função de teste.
    Isso garante que cada teste comece com um objeto "limpo".
    """
    return MotionComparator()

def create_mock_landmarks(angles_dict):
    """
    Função auxiliar para criar um objeto de landmarks falso.
    Como a lógica de cálculo de ângulo já é testada implicitamente pelo `compare_poses`,
    podemos simplificar aqui e focar na lógica de comparação.
    Esta função cria um mock que se parece com uma lista de landmarks do MediaPipe.
    
    Args:
        angles_dict (dict): Dicionário com os valores de ângulo desejados.
                            Não usado diretamente aqui, mas representa a pose.
    
    Returns:
        list: Uma lista de objetos MagicMock simulando landmarks.
    """
    landmarks = [MagicMock() for _ in range(33)] # Cria 33 landmarks falsos.
    for i, lm in enumerate(landmarks):
        # Atribui coordenadas x, y, z falsas para simular dados reais.
        # Isso é importante para que o `calculate_angle` não falhe.
        lm.x = np.sin(i)
        lm.y = np.cos(i)
        lm.z = 0.1
        lm.visibility = 1.0
    return landmarks

# --------------------------------------------------------------------------------------------------
# Casos de Teste para MotionComparator
# --------------------------------------------------------------------------------------------------

def test_compare_identical_poses(motion_comparator):
    """
    Testa se a comparação de duas poses idênticas resulta em uma pontuação de 100%.
    
    Cenário: Aluno e mestre estão na mesma postura.
    Resultado esperado: Pontuação máxima, feedback positivo.
    """
    # Cria uma pose de referência.
    landmarks = create_mock_landmarks({})
    
    # Sobrescrevemos o método `get_all_angles` para retornar ângulos fixos.
    # Isso isola o teste, focando apenas na lógica de `compare_poses`.
    motion_comparator.get_all_angles = MagicMock(return_value={
        'cotovelo_direito': 90, 'joelho_esquedo': 170
    })
    
    # Chama o método a ser testado com os mesmos landmarks para aluno e mestre.
    score, feedback = motion_comparator.compare_poses(landmarks, landmarks)
    
    # Asserções: verificam se o resultado é o esperado.
    assert score == 100.0
    assert feedback == "Excelente movimento!"

def test_compare_different_poses(motion_comparator):
    """
    Testa a comparação de duas poses diferentes.
    
    Cenário: O cotovelo do aluno está em um ângulo diferente do mestre.
    Resultado esperado: Pontuação menor que 100% e feedback corretivo.
    """
    landmarks_aluno = create_mock_landmarks({})
    landmarks_mestre = create_mock_landmarks({})
    
    # Mock do `get_all_angles` para retornar ângulos diferentes para aluno e mestre.
    def side_effect(landmarks):
        if landmarks is landmarks_aluno:
            return {'cotovelo_direito': 90, 'joelho_esquedo': 170}
        return {'cotovelo_direito': 120, 'joelho_esquedo': 170} # Diferença de 30 graus no cotovelo.
    
    motion_comparator.get_all_angles = MagicMock(side_effect=side_effect)

    # Chama o método a ser testado.
    score, feedback = motion_comparator.compare_poses(landmarks_aluno, landmarks_mestre)
    
    # Asserções.
    assert score < 100.0
    assert "Diminua o ângulo do Cotovelo Direito" in feedback

def test_compare_with_invalid_landmarks(motion_comparator):
    """
    Testa o comportamento do comparador quando um dos landmarks é inválido (None).
    
    Cenário: O detector de pose falhou em um dos frames.
    Resultado esperado: Pontuação 0 e feedback neutro, sem erros.
    """
    landmarks_validos = create_mock_landmarks({})
    
    # Teste com landmarks do aluno sendo None.
    score, feedback = motion_comparator.compare_poses(None, landmarks_validos)
    assert score == 0.0
    assert feedback == "Analisando..."

    # Teste com landmarks do mestre sendo None.
    score, feedback = motion_comparator.compare_poses(landmarks_validos, None)
    assert score == 0.0
    assert feedback == "Analisando..."
    
    # Teste com ambos sendo None.
    score, feedback = motion_comparator.compare_poses(None, None)
    assert score == 0.0
    assert feedback == "Analisando..."