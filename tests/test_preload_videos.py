# tests/test_preload_videos.py

import pytest
import flet as ft
from unittest.mock import MagicMock, patch
import os
import sys

# Adiciona o diretório raiz ao path para permitir a importação dos módulos da aplicação.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import KravMagaApp

# Define um caminho falso para o diretório de assets para os testes.
FAKE_ASSETS_PATH = "tests/fake_assets/master_videos"

@pytest.fixture
def app_with_mocked_assets():
    """
    Fixture que cria uma instância da aplicação Flet e simula (mock)
    a existência de vídeos na pasta de assets para os testes.
    """
    # Garante que o diretório falso exista antes do teste.
    os.makedirs(FAKE_ASSETS_PATH, exist_ok=True)
    # Cria arquivos de vídeo falsos.
    with open(os.path.join(FAKE_ASSETS_PATH, "soco_direto.mp4"), "w") as f:
        f.write("fake video")
    with open(os.path.join(FAKE_ASSETS_PATH, "defesa_360.mp4"), "w") as f:
        f.write("fake video")

    # Usa 'patch' para forçar a aplicação a usar nosso diretório falso.
    with patch.object(KravMagaApp, 'master_videos_path', FAKE_ASSETS_PATH):
        mock_page = MagicMock(spec=ft.Page)
        mock_page.overlay = []
        mock_page.update = MagicMock()
        
        # Inicializa a aplicação, que agora lerá os vídeos do nosso diretório falso.
        krav_maga_app = KravMagaApp(mock_page)
        yield krav_maga_app

    # Limpeza: remove os arquivos e diretório falsos após a execução do teste.
    for f in os.listdir(FAKE_ASSETS_PATH):
        os.remove(os.path.join(FAKE_ASSETS_PATH, f))
    os.rmdir(FAKE_ASSETS_PATH)
    os.rmdir("tests/fake_assets")

def test_dropdown_is_populated_with_master_videos(app_with_mocked_assets):
    """
    Verifica se o Dropdown é preenchido corretamente com os vídeos encontrados
    na pasta de assets simulada.
    """
    print("\nExecutando test_dropdown_is_populated_with_master_videos...")
    
    app = app_with_mocked_assets
    dropdown_options = app.master_video_dropdown.options

    # Asserção 1: Verifica se o número de opções no dropdown é igual ao número de vídeos falsos.
    assert len(dropdown_options) == 2, "O Dropdown deveria ter 2 opções de vídeo."
    print("✓ Número correto de opções no dropdown.")

    # Asserção 2: Verifica se os nomes dos vídeos foram formatados corretamente para exibição.
    option_texts = {opt.text for opt in dropdown_options}
    assert "Soco Direto" in option_texts, "A opção 'Soco Direto' deveria estar no dropdown."
    assert "Defesa 360" in option_texts, "A opção 'Defesa 360' deveria estar no dropdown."
    print("✓ Nomes das opções formatados corretamente.")

def test_selecting_from_dropdown_updates_master_video_path(app_with_mocked_assets):
    """
    Testa se a seleção de um item no Dropdown atualiza o caminho do vídeo mestre
    no estado da aplicação.
    """
    print("\nExecutando test_selecting_from_dropdown_updates_master_video_path...")
    
    app = app_with_mocked_assets
    
    # Simula o evento 'on_change' do Dropdown.
    # O valor do controle (value) é a 'key' da opção, que é o nome do arquivo.
    mock_event = MagicMock()
    mock_event.control.value = "soco_direto.mp4"
    app.on_master_video_selected(mock_event)
    
    # Asserção: Verifica se o caminho do vídeo mestre foi definido corretamente.
    expected_path = os.path.join(FAKE_ASSETS_PATH, "soco_direto.mp4")
    assert app.video_mestre_path == expected_path, "O caminho do vídeo mestre não foi atualizado corretamente."
    print(f"✓ Caminho do vídeo mestre atualizado para '{app.video_mestre_path}'.")

    # Asserção 2: Verifica se o status foi atualizado para o usuário.
    assert "soco_direto.mp4" in app.status_text.value
    print("✓ Texto de status foi atualizado com a seleção.")