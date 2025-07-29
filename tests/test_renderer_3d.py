# tests/test_renderer_3d.py

import pytest
import numpy as np
import os
import sys

# Adiciona o diretório raiz ao path para permitir a importação dos módulos.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.renderer_3d import render_3d_skeleton

@pytest.fixture
def sample_landmarks():
    """Cria um conjunto de dados de landmarks 3D falsos para os testes."""
    landmark_names = [
        "LEFT_SHOULDER", "RIGHT_SHOULDER", "LEFT_ELBOW", "LEFT_WRIST",
        "RIGHT_ELBOW", "RIGHT_WRIST", "LEFT_HIP", "RIGHT_HIP",
        "LEFT_KNEE", "LEFT_ANKLE", "RIGHT_KNEE", "RIGHT_ANKLE"
    ]
    landmarks = [{"name": name, "x": np.random.rand(), "y": np.random.rand(), "z": np.random.rand(), "visibility": 0.99} for name in landmark_names]
    return landmarks

def test_render_3d_skeleton_returns_valid_image(sample_landmarks):
    """Testa se a função retorna uma imagem válida quando recebe landmarks."""
    print("\nExecutando test_render_3d_skeleton_returns_valid_image...")
    image = render_3d_skeleton(sample_landmarks)
    assert isinstance(image, np.ndarray), "A função deveria retornar um array numpy."
    assert image.ndim == 3, "A imagem retornada deveria ter 3 dimensões."
    assert image.shape[2] == 3, "A imagem retornada deveria ter 3 canais de cor (BGR)."
    print("✓ Teste de imagem válida passou.")

def test_render_3d_skeleton_handles_empty_input():
    """Testa se a função lida corretamente com uma entrada vazia, sem quebrar."""
    print("\nExecutando test_render_3d_skeleton_handles_empty_input...")
    image = render_3d_skeleton([])
    assert isinstance(image, np.ndarray)
    assert image.sum() == 0, "A imagem deveria ser preta para uma entrada vazia."
    print("✓ Teste de entrada vazia passou.")