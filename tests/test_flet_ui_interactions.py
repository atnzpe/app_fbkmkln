# tests/test_flet_ui_interactions.py

# --------------------------------------------------------------------------------------------------
# Importação de Bibliotecas
# --------------------------------------------------------------------------------------------------
import pytest
import flet as ft
from unittest.mock import MagicMock, patch
import os
import sys

# Adiciona o diretório raiz ao path para permitir a importação dos módulos da aplicação.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.Old_main_flet import KravMagaApp

# --------------------------------------------------------------------------------------------------
# Fixtures de Teste (Configuração do Ambiente de Teste)
# --------------------------------------------------------------------------------------------------


@pytest.fixture
def app():
    """
    Esta fixture cria uma instância da nossa aplicação Flet para cada teste.
    Ela usa "mocks", que são objetos simulados, para a página (Page) e o
    armazenamento do cliente (client_storage), para que possamos testar a lógica
    da aplicação de forma isolada, sem precisar de uma janela gráfica real.
    """
    # Mock para a página principal do Flet.
    mock_page = MagicMock(spec=ft.Page)
    # Mock para o armazenamento de estado do Flet.
    mock_page.client_storage = MagicMock()
    # Mock para a fila de sobreposição (overlay) onde os FilePickers são adicionados.
    mock_page.overlay = []

    # Cria a instância da nossa aplicação, passando a página mockada.
    krav_maga_app = KravMagaApp(mock_page)
    return krav_maga_app


# --------------------------------------------------------------------------------------------------
# Casos de Teste
# --------------------------------------------------------------------------------------------------


def test_initial_state(app: KravMagaApp):
    """
    Testa o estado inicial da aplicação logo após ser criada.

    Cenário: A aplicação acaba de ser iniciada.
    Resultado Esperado: O botão de análise deve estar desabilitado.
    """
    # Log para indicar qual teste está sendo executado.
    print("\nExecutando test_initial_state...")

    # Asserção: Verifica se o botão 'analyze_button' está desabilitado por padrão.
    assert (
        app.analyze_button.disabled is True
    ), "O botão de análise deveria estar desabilitado inicialmente."
    print("✓ Estado inicial verificado: Botão de análise está desabilitado.")


def test_analyze_button_enables_after_both_files_are_selected(app: KravMagaApp):
    """
    Testa se o botão de análise é habilitado somente após ambos os vídeos serem selecionados.

    Cenário: O usuário faz o upload do vídeo do aluno e depois do vídeo do mestre.
    Resultado Esperado: O botão de análise deve permanecer desabilitado após o primeiro upload
                       e ser habilitado após o segundo.
    """
    print("\nExecutando test_analyze_button_enables_after_both_files_are_selected...")

    # --- Passo 1: Simula o upload do vídeo do ALUNO ---

    # Cria um evento falso de seleção de arquivo, como se o usuário tivesse escolhido um arquivo.
    mock_file_aluno = MagicMock()
    mock_file_aluno.path = "/fake/path/aluno.mp4"
    aluno_event = MagicMock(spec=ft.FilePickerResultEvent, files=[mock_file_aluno])

    # Configura o mock do client_storage para simular o armazenamento do caminho do arquivo.
    # Quando `set` é chamado, configuramos o `get` para retornar o valor correto.
    app.page.client_storage.get.side_effect = lambda key: (
        "/fake/path/aluno.mp4" if key == "video_aluno_path" else None
    )
    app.page.client_storage.contains_key.side_effect = (
        lambda key: key == "video_aluno_path"
    )

    # Chama o método que lida com o resultado da seleção do arquivo.
    app.pick_file_result(aluno_event, is_aluno=True)

    # Asserção: Após um único arquivo, o botão ainda deve estar desabilitado.
    assert (
        app.analyze_button.disabled is True
    ), "O botão de análise deveria continuar desabilitado após um único upload."
    print("✓ Verificado: Botão permanece desabilitado após o primeiro upload.")

    # --- Passo 2: Simula o upload do vídeo do MESTRE ---

    mock_file_mestre = MagicMock()
    mock_file_mestre.path = "/fake/path/mestre.mp4"
    mestre_event = MagicMock(spec=ft.FilePickerResultEvent, files=[mock_file_mestre])

    # Reconfigura o mock do storage para simular que ambos os caminhos estão salvos.
    app.page.client_storage.get.side_effect = lambda key: {
        "video_aluno_path": "/fake/path/aluno.mp4",
        "video_mestre_path": "/fake/path/mestre.mp4",
    }.get(key)
    app.page.client_storage.contains_key.side_effect = lambda key: key in [
        "video_aluno_path",
        "video_mestre_path",
    ]

    # Chama o método para o segundo arquivo.
    app.pick_file_result(mestre_event, is_aluno=False)

    # Asserção Final: Agora, com ambos os arquivos "selecionados", o botão deve estar habilitado.
    assert (
        app.analyze_button.disabled is False
    ), "O botão de análise deveria estar habilitado após ambos os uploads."
    print("✓ Verificado: Botão foi habilitado com sucesso após o segundo upload.")
