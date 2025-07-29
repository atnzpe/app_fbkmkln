# tests/test_file_upload.py
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import flet as ft
import os
import sys

# Adiciona o diretório raiz para importação correta
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Importa a função a ser testada e as dependências que ela manipula
from src.Old_main_flet import pick_file_result
from src.video_analyzer import VideoAnalyzer
from src.utils import FeedbackManager

@pytest.fixture
def mock_page_and_controls():
    """
    Cria mocks para a página Flet e os controles que a função de callback manipula.
    Isso nos permite simular a UI e verificar as interações.
    """
    page = AsyncMock(spec=ft.Page)
    page.update = AsyncMock()

    # Simula a estrutura de controles para que possamos acessar o botão de análise
    analyze_button = ft.ElevatedButton(disabled=True)
    page.controls = [
        ft.Column(
            controls=[
                ft.Row(), # Placeholder para a primeira linha de botões
                ft.Row(controls=[ft.ElevatedButton(), ft.ElevatedButton(), analyze_button]),
            ]
        )
    ]
    return page, analyze_button

@pytest.fixture
def mock_dependencies():
    """
    Cria mocks para as dependências externas que a função `pick_file_result` utiliza,
    como o VideoAnalyzer e o FeedbackManager.
    """
    with patch('src.main_flet.video_analyzer', spec=VideoAnalyzer) as mock_analyzer, \
         patch('src.main_flet.feedback_manager', spec=FeedbackManager) as mock_feedback:

        # Configura o estado inicial dos mocks
        mock_analyzer.video_aluno_path = None
        mock_analyzer.video_mestre_path = None
        mock_analyzer.load_video_from_bytes = MagicMock()

        yield mock_analyzer, mock_feedback

@pytest.mark.asyncio
async def test_pick_file_result_aluno_success(mock_page_and_controls, mock_dependencies):
    """
    Testa o upload bem-sucedido do vídeo do aluno.
    Verifica se o feedback é atualizado e se o botão de análise permanece desabilitado.
    """
    page, analyze_button = mock_page_and_controls
    mock_analyzer, mock_feedback = mock_dependencies

    # Simula um evento de seleção de arquivo
    mock_file = MagicMock(path="/fake/path/aluno.mp4", name="aluno.mp4")
    event = MagicMock(spec=ft.FilePickerResultEvent, files=[mock_file], page=page)

    # Simula a leitura do arquivo
    with patch("builtins.open", new_callable=MagicMock) as mock_open:
        mock_open.return_value.read.return_value = b"dummy_video_data"

        # Chama a função sob teste
        await pick_file_result(event, is_aluno=True)

    # Verifica se o feedback foi chamado corretamente
    mock_feedback.update_feedback.assert_any_call("Carregando vídeo do aluno: aluno.mp4...", is_error=False)
    mock_feedback.update_feedback.assert_any_call("Vídeo do aluno 'aluno.mp4' carregado.", is_error=False)

    # Verifica se o método de carregar vídeo foi chamado com os bytes corretos
    mock_analyzer.load_video_from_bytes.assert_called_once_with(b"dummy_video_data", True)

    # Verifica se a UI foi atualizada
    page.update.assert_called()

    # Após apenas um upload, o botão de análise deve continuar desabilitado
    assert analyze_button.disabled is True

@pytest.mark.asyncio
async def test_both_files_uploaded_enables_analysis(mock_page_and_controls, mock_dependencies):
    """
    Testa se o botão de análise é habilitado após o upload de AMBOS os vídeos.
    """
    page, analyze_button = mock_page_and_controls
    mock_analyzer, mock_feedback = mock_dependencies

    # --- Simula o upload do ALUNO ---
    mock_analyzer.video_aluno_path = "/fake/aluno.mp4" # Simula que já foi carregado
    mock_file_mestre = MagicMock(path="/fake/path/mestre.mp4", name="mestre.mp4")
    event_mestre = MagicMock(spec=ft.FilePickerResultEvent, files=[mock_file_mestre], page=page)

    with patch("builtins.open", new_callable=MagicMock) as mock_open:
        mock_open.return_value.read.return_value = b"dummy_video_data"
        await pick_file_result(event_mestre, is_aluno=False)

    # Verifica o feedback de sucesso para o segundo upload
    mock_feedback.update_feedback.assert_any_call("Ambos os vídeos carregados! Clique em 'Analisar' para iniciar.", is_error=False)

    # O botão de análise agora DEVE estar habilitado
    assert analyze_button.disabled is False

@pytest.mark.asyncio
async def test_pick_file_no_file_selected(mock_page_and_controls, mock_dependencies):
    """
    Testa o cenário onde o usuário cancela a seleção de arquivo.
    """
    page, _ = mock_page_and_controls
    mock_analyzer, mock_feedback = mock_dependencies

    # Simula um evento sem arquivos
    event = MagicMock(spec=ft.FilePickerResultEvent, files=[], page=page)

    await pick_file_result(event, is_aluno=True)

    # Verifica o feedback
    mock_feedback.update_feedback.assert_called_with("Nenhum vídeo do aluno selecionado.", is_error=False)
    # Garante que nenhuma tentativa de carregar o vídeo foi feita
    mock_analyzer.load_video_from_bytes.assert_not_called()
    # Verifica se a UI foi atualizada
    page.update.assert_called()