import pytest

import os
import sys
import asyncio
import flet as ft
import io
from unittest.mock import AsyncMock, patch

# Adiciona o diretório raiz do projeto ao sys.path para que as importações funcionem corretamente
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Importa a função main da sua aplicação Flet
from src.Old_main_flet import main


@pytest.fixture(scope="module", autouse=True)
def run_flet_app_for_tests():
    """
    Fixture para rodar a aplicação Flet em um ambiente de teste simulado.
    Define um escopo de módulo para que a aplicação seja iniciada apenas uma vez.
    """
    # Usa AppTest para simular a execução da aplicação Flet.
    # O timeout padrão pode ser ajustado conforme a complexidade da inicialização.
    app_test = AppTest(target=main)
    # Roda a aplicação assincronamente para que a UI seja construída
    asyncio.run(app_test.run_async())
    yield app_test
    # A limpeza aqui seria mínima, pois AppTest simula um ciclo de vida.
    # Para testes mais complexos, pode ser necessário um `app_test.shutdown()`
    # app_test.shutdown() # Descomente se for necessário um shutdown explícito


def test_app_loads_successfully(run_flet_app_for_tests):
    """
    Testa se a aplicação Flet carrega sem exceções e se o título está correto.
    """
    at = run_flet_app_for_tests
    # Verifica se não houve exceções durante a inicialização
    assert (
        len(at.page.errors) == 0
    ), f"A aplicação Flet falhou ao carregar com exceções: {at.page.errors}"
    # Verifica o título da página
    assert at.page.title == "Analisador de Movimentos de Krav Maga (Flet)"
    print("\nTeste: Aplicação Flet carregada com sucesso.")


def test_initial_ui_elements_exist(run_flet_app_for_tests):
    """
    Testa se os elementos essenciais da UI estão presentes após o carregamento da aplicação.
    """
    at = run_flet_app_for_tests

    # Verifica a presença dos botões de upload
    upload_aluno_button = at.get(
        lambda c: c.text == "Upload Vídeo do Aluno" and isinstance(c, ft.ElevatedButton)
    )
    assert (
        upload_aluno_button is not None
    ), "Botão 'Upload Vídeo do Aluno' não encontrado."

    upload_mestre_button = at.get(
        lambda c: c.text == "Upload Vídeo do Mestre"
        and isinstance(c, ft.ElevatedButton)
    )
    assert (
        upload_mestre_button is not None
    ), "Botão 'Upload Vídeo do Mestre' não encontrado."

    # Verifica se o botão "Analisar Movimentos" está inicialmente desabilitado
    analyze_button = at.get(
        lambda c: c.text == "Analisar Movimentos" and isinstance(c, ft.ElevatedButton)
    )
    assert analyze_button is not None, "Botão 'Analisar Movimentos' não encontrado."
    assert (
        analyze_button.disabled is True
    ), "Botão 'Analisar Movimentos' deveria estar desabilitado inicialmente."

    # Verifica se os IconButtons são criados corretamente sem o erro de 'text'
    # Procuramos pelo ícone esperado, pois o 'text' foi removido
    play_button_aluno = at.get(
        lambda c: c.tooltip == "Reproduzir/Pausar vídeo do aluno"
        and isinstance(c, ft.IconButton)
    )
    assert play_button_aluno is not None, "IconButton do aluno não encontrado."
    assert (
        play_button_aluno.icon == ft.icons.PLAY_ARROW
    ), "Ícone do botão de reprodução do aluno incorreto."

    play_button_mestre = at.get(
        lambda c: c.tooltip == "Reproduzir/Pausar vídeo do mestre"
        and isinstance(c, ft.IconButton)
    )
    assert play_button_mestre is not None, "IconButton do mestre não encontrado."
    assert (
        play_button_mestre.icon == ft.icons.PLAY_ARROW
    ), "Ícone do botão de reprodução do mestre incorreto."

    print("\nTeste: Elementos da UI iniciais presentes e corretos.")


@pytest.mark.asyncio
async def test_upload_buttons_enable_analyze(run_flet_app_for_tests):
    """
    Testa se o carregamento de ambos os vídeos habilita o botão "Analisar Movimentos".
    Simula a seleção de arquivos usando o FilePicker.
    """
    at = run_flet_app_for_tests
    page = at.page

    # Cria mock para FilePickerResultEvent.File e seus métodos
    mock_file_aluno = AsyncMock()
    mock_file_aluno.name = "video_aluno.mp4"
    mock_file_aluno.read_bytes.return_value = b"dummy_video_data_aluno"

    mock_file_mestre = AsyncMock()
    mock_file_mestre.name = "video_mestre.mp4"
    mock_file_mestre.read_bytes.return_value = b"dummy_video_data_mestre"

    # Obtém as instâncias do FilePicker
    file_picker_aluno = at.get(
        lambda c: isinstance(c, ft.FilePicker), to_wait_for=100
    )  # Pode precisar de um tempo para o FilePicker aparecer no overlay
    file_picker_mestre = at.get(
        lambda c: isinstance(c, ft.FilePicker), index=1, to_wait_for=100
    )  # Assumindo o segundo FilePicker

    assert file_picker_aluno is not None, "FilePicker do aluno não encontrado."
    assert file_picker_mestre is not None, "FilePicker do mestre não encontrado."

    # Simula o resultado da seleção para o vídeo do aluno
    await file_picker_aluno.on_result(
        ft.FilePickerResultEvent(
            data={"files": [mock_file_aluno], "control": file_picker_aluno}
        )
    )
    # page.update() já é chamado dentro do on_result, mas uma atualização extra não faz mal
    await page.update_async()

    # O botão de análise ainda deve estar desabilitado
    analyze_button = at.get(
        lambda c: c.text == "Analisar Movimentos" and isinstance(c, ft.ElevatedButton)
    )
    assert (
        analyze_button.disabled is True
    ), "Botão 'Analisar Movimentos' deveria estar desabilitado após upload de apenas um vídeo."
    feedback_text_container = at.get(
        lambda c: isinstance(c, ft.Container)
        and isinstance(c.content, ft.Text)
        and "Por favor, carregue ambos os vídeos" in c.content.value
    )
    assert (
        feedback_text_container is not None
    ), "Mensagem de feedback inicial ausente ou incorreta após upload de um vídeo."  # COMPLETOU AQUI
