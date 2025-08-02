# tests/test_playlist_service.py

# pytest é a biblioteca que usamos para escrever e rodar os testes.
import pytest
# unittest.mock nos permite simular (mock) funções e objetos.
from unittest.mock import patch, mock_open
# os e sys são usados para ajustar o caminho de importação.
import os
import sys
# json é usado para converter texto em dicionários Python.
import json

# Adiciona o diretório raiz do projeto ao path do Python para que possamos importar de 'src'.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Importa a classe e a constante que queremos testar.
from src.playlist_service import PlaylistService
from src.config import RANK_HIERARCHY


# Define o conteúdo simulado dos nossos arquivos playlist.json
MOCK_PLAYLIST_DATA = {
    "Branca": [{"file": "soco.mp4"}],
    "Amarela": [{"file": "chute.mp4"}, {"file": "defesa.mp4"}],
    "Laranja": [{"file": "rolamento.mp4"}],
}

def mock_json_load(file_handle):
    """
    Uma função auxiliar para simular o comportamento de json.load().
    Ela retorna o conteúdo JSON correto com base no nome do arquivo que foi "aberto".
    """
    # O mock_open nos dá o nome do arquivo que foi aberto em file_handle.name
    if "Branca" in file_handle.name:
        return MOCK_PLAYLIST_DATA["Branca"]
    if "Amarela" in file_handle.name:
        return MOCK_PLAYLIST_DATA["Amarela"]
    if "Laranja" in file_handle.name:
        return MOCK_PLAYLIST_DATA["Laranja"]
    return []

# O 'patch' intercepta chamadas a funções reais e as substitui por nosso comportamento simulado.
@patch("os.path.exists", return_value=True) # Diz ao teste que todos os arquivos sempre existem.
@patch("builtins.open", new_callable=mock_open) # Simula a função 'open'.
@patch("json.load", side_effect=mock_json_load) # Simula a função 'json.load' usando nossa função auxiliar.
def test_get_rank_playlist(mock_load, mock_open_func, mock_exists):
    """
    Testa se a playlist para uma única faixa é carregada corretamente.
    """
    print("\nExecutando test_get_rank_playlist...")
    
    # Cria o serviço que queremos testar.
    service = PlaylistService(videos_base_path="assets/videos_tecnicas")
    # Executa a função.
    playlist = service.get_rank_playlist("Amarela")
    
    # Verifica se o resultado está correto.
    assert len(playlist) == 2
    assert playlist[0]["file"] == "chute.mp4"
    print("✓ Playlist de faixa única carregada corretamente.")


@patch("os.path.exists", return_value=True)
@patch("builtins.open", new_callable=mock_open)
@patch("json.load", side_effect=mock_json_load)
def test_get_exam_playlist(mock_load, mock_open_func, mock_exists):
    """
    Testa se a playlist de exame consolida os vídeos de múltiplas faixas corretamente.
    """
    print("\nExecutando test_get_exam_playlist...")
    
    service = PlaylistService(videos_base_path="assets/videos_tecnicas")
    # Simula um exame para a Faixa Laranja.
    exam_playlist = service.get_exam_playlist("Laranja")

    # O resultado esperado é a soma dos vídeos de Branca, Amarela e Laranja (1 + 2 + 1 = 4).
    assert len(exam_playlist) == 4
    assert exam_playlist[0]["file"] == "soco.mp4"      # Da Faixa Branca
    assert exam_playlist[1]["file"] == "chute.mp4"     # Da Faixa Amarela
    assert exam_playlist[3]["file"] == "rolamento.mp4" # Da Faixa Laranja
    print("✓ Playlist de exame consolidada corretamente.")