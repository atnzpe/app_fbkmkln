# tests/test_video_access.py

import flet as ft
import pytest
from unittest.mock import MagicMock, patch
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import AppFBKMKLN

@patch('os.path.isdir')
@patch('os.listdir')
@patch('os.path.exists', return_value=True) # Adicionado para simular que playlist.json existe
def test_video_view_for_amarela(mock_exists, mock_listdir, mock_isdir):
    """
    Cenário de Teste: Aluno Faixa Amarela
    """
    print("\nExecutando test_video_view_for_amarela...")
    
    mock_isdir.return_value = True
    def listdir_side_effect(path):
        if "Branca" in path: return ["soco_direto.mp4"]
        if "Amarela" in path: return ["rolamento.mp4", "defesa_360.mp4"]
        if "Laranja" in path: return ["defesa_faca.mp4"]
        return []
    mock_listdir.side_effect = listdir_side_effect

    mock_page = MagicMock()
    app = AppFBKMKLN(mock_page)
    user_data = {"LOGIN": "Teste", "GRADUACAO_ATUAL": "Amarela", "PROXIMA_GRADUACAO": "Laranja"}
    app.auth_service.get_accessible_ranks = MagicMock(return_value=["Branca", "Amarela", "Laranja"])
    # Simula o playlist service para não depender do arquivo json real
    app.playlist_service.get_rank_playlist = MagicMock(return_value=[{"file": "dummy.mp4"}])


    video_view = app.create_videos_view(user_data)
    
    # **CORREÇÃO:** A estrutura da View é [Row(voltar), Text(título), Divider, Column(conteúdo)]
    # A coluna com os botões e títulos está no índice 3.
    content_column = video_view.controls[3]
    content_str = ""
    for control in content_column.controls:
        if isinstance(control, ft.Text):
            content_str += control.value
        elif isinstance(control, ft.Row): # Os botões estão em uma Row
            for button in control.controls:
                 if hasattr(button, 'text'):
                    content_str += button.text

    assert "Faixa Branca" in content_str
    assert "Faixa Amarela" in content_str
    assert "Faixa Laranja" in content_str
    assert "Faixa Verde" not in content_str
    print("✓ Seções de faixas renderizadas corretamente.")
    
    assert "Treinar Faixa Branca" in content_str
    assert "Simular Exame para Laranja" in content_str
    print("✓ Botões de treino e exame encontrados corretamente.")