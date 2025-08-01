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
def test_video_view_for_amarela(mock_listdir, mock_isdir):
    """
    Cenário de Teste: Aluno Faixa Amarela
    Verifica se a tela de vídeos exibe corretamente as seções e os vídeos
    para as faixas Branca, Amarela e Laranja.
    """
    print("\nExecutando test_video_view_for_amarela...")
    
    # Simula o ambiente, dizendo que as pastas existem e quais arquivos elas contêm.
    mock_isdir.return_value = True
    def listdir_side_effect(path):
        if "Branca" in path: return ["soco_direto.mp4"]
        if "Amarela" in path: return ["rolamento.mp4", "defesa_360.mp4"]
        if "Laranja" in path: return ["defesa_faca.mp4"]
        return []
    mock_listdir.side_effect = listdir_side_effect

    # Prepara o teste, criando uma instância do App e um usuário simulado.
    mock_page = MagicMock()
    app = AppFBKMKLN(mock_page)
    user_data = {"LOGIN": "Teste", "GRADUACAO_ATUAL": "Amarela"}
    app.auth_service.get_accessible_ranks = MagicMock(return_value=["Branca", "Amarela", "Laranja"])

    # Executa a função que queremos testar.
    video_view = app.create_videos_view(user_data)
    
    # Extrai o conteúdo da View para verificação.
    content_str = ""
    for control in video_view.controls[2].controls: # A coluna com o conteúdo
        if isinstance(control, ft.Text):
            content_str += control.value
        elif isinstance(control, ft.ResponsiveRow):
            for col in control.controls:
                content_str += col.controls[0].content.controls[1].value

    # Verifica se as seções corretas estão presentes e as incorretas não.
    assert "Faixa Branca" in content_str
    assert "Faixa Amarela" in content_str
    assert "Faixa Laranja" in content_str
    assert "Faixa Verde" not in content_str
    print("✓ Seções de faixas renderizadas corretamente.")
    
    # Verifica se os nomes dos vídeos estão corretos.
    assert "Soco Direto" in content_str
    assert "Rolamento" in content_str
    assert "Defesa 360" in content_str
    assert "Defesa Faca" in content_str
    print("✓ Cards de vídeo encontrados e nomeados corretamente.")