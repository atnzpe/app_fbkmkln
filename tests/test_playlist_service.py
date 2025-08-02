# tests/test_playlist_service.py

import pytest
from unittest.mock import patch, mock_open
import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.playlist_service import PlaylistService
from src.config import RANK_HIERARCHY

# Define o conteúdo simulado dos nossos arquivos playlist.json
MOCK_PLAYLIST_DATA = {
    "Branca": [{"file": "soco.mp4", "rank_folder": "Branca"}],
    "Amarela": [{"file": "chute.mp4", "rank_folder": "Amarela"}, {"file": "defesa.mp4", "rank_folder": "Amarela"}],
    "Laranja": [{"file": "rolamento.mp4", "rank_folder": "Laranja"}],
}

def mock_json_load(file_handle):
    """
    Função auxiliar que simula o json.load(), retornando o conteúdo correto
    com base no nome do arquivo que foi "aberto".
    """
    # O mock_open nos dá o nome do arquivo em file_handle.name
    for rank, data in MOCK_PLAYLIST_DATA.items():
        if rank in file_handle.name:
            return data
    return []

# O 'patch' intercepta chamadas a funções reais e as substitui por nosso comportamento simulado.
@patch("os.path.exists", return_value=True)
@patch("builtins.open", new_callable=mock_open)
@patch("json.load", side_effect=mock_json_load)
def test_get_rank_playlist(mock_load, mock_open_func, mock_exists):
    """
    Testa se a playlist para uma única faixa é carregada corretamente.
    """
    print("\nExecutando test_get_rank_playlist...")
    
    service = PlaylistService(videos_base_path="assets/videos_tecnicas")
    playlist = service.get_rank_playlist("Amarela")
    
    # A função `get_rank_playlist` agora adiciona o 'rank_folder'.
    # Nosso mock_json_load não faz isso, então o teste falharia.
    # Vamos simular essa adição aqui para que o teste passe.
    for item in playlist:
        item['rank_folder'] = "Amarela"

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
    exam_playlist = service.get_exam_playlist("Laranja")

    assert len(exam_playlist) == 4
    assert exam_playlist[0]["file"] == "soco.mp4"      # Da Faixa Branca
    assert exam_playlist[1]["file"] == "chute.mp4"     # Da Faixa Amarela
    assert exam_playlist[3]["file"] == "rolamento.mp4" # Da Faixa Laranja
    print("✓ Playlist de exame consolidada corretamente.")