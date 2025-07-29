# tests/test_upload_logic.py

import pytest
import flet as ft
from unittest.mock import MagicMock
import os
import sys

# Adiciona o diretório raiz ao path para permitir a importação dos módulos da aplicação.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import KravMagaApp

@pytest.fixture
def app_instance():
    """
    Fixture que cria uma instância da nossa aplicação Flet para cada teste.
    Utiliza um 'mock' (objeto simulado) para a página do Flet, permitindo
    testar a lógica da aplicação de forma isolada, sem uma interface gráfica real.
    """
    # Cria um mock da página Flet com todos os métodos e atributos necessários.
    mock_page = MagicMock(spec=ft.Page)
    mock_page.client_storage = MagicMock()
    mock_page.overlay = []  # O FilePicker é adicionado ao overlay, então simulamos a lista.
    mock_page.update = MagicMock() # Simula a função de atualização da página.

    # Inicializa a nossa aplicação com a página mockada.
    krav_maga_app = KravMagaApp(mock_page)
    return krav_maga_app


def test_initial_state(app_instance: KravMagaApp):
    """
    Verifica o estado inicial da aplicação.
    O botão de análise deve começar desabilitado.
    """
    # Log para clareza na execução dos testes.
    print("\nExecutando test_initial_state...")

    # Asserção: Confirma que o botão 'analyze_button' está desabilitado.
    assert app_instance.analyze_button.disabled is True, "O botão de análise deveria estar desabilitado na inicialização."
    print("✓ Teste de estado inicial: Botão de análise está corretamente desabilitado.")


def test_analyze_button_enables_only_after_both_files_are_selected(app_instance: KravMagaApp):
    """
    Testa o fluxo completo de upload e a lógica de habilitação do botão 'Analisar'.

    Passos:
    1. Simula o upload do vídeo do aluno.
    2. Verifica se a mensagem de sucesso é específica para o aluno.
    3. Verifica se o botão 'Analisar' CONTINUA desabilitado.
    4. Simula o upload do vídeo do mestre.
    5. Verifica se a mensagem de sucesso é específica para o mestre.
    6. Verifica se o botão 'Analisar' AGORA está habilitado.
    """
    print("\nExecutando test_analyze_button_enables_only_after_both_files_are_selected...")

    # --- Passo 1: Simula o upload do vídeo do ALUNO ---
    # Cria um evento falso de seleção de arquivo para o aluno.
    mock_file_aluno = MagicMock()
    mock_file_aluno.path = "/fake/path/aluno.mp4"
    aluno_event = MagicMock(spec=ft.FilePickerResultEvent, files=[mock_file_aluno])

    # Chama o método que lida com o resultado da seleção do arquivo do aluno.
    app_instance.pick_file_result(aluno_event, is_aluno=True)
    
    # --- Verificações para o upload do ALUNO ---
    # Asserção 1: Verifica a mensagem de feedback específica para o aluno.
    assert app_instance.status_text.value == "Vídeo do aluno carregado com sucesso."
    print("✓ Feedback de sucesso para o aluno verificado.")
    
    # Asserção 2: Verifica se o botão de análise AINDA está desabilitado.
    assert app_instance.analyze_button.disabled is True, "O botão de análise deveria continuar desabilitado após um único upload."
    print("✓ Botão de análise corretamente desabilitado após o primeiro upload.")

    # --- Passo 2: Simula o upload do vídeo do MESTRE ---
    # Cria um evento falso de seleção de arquivo para o mestre.
    mock_file_mestre = MagicMock()
    mock_file_mestre.path = "/fake/path/mestre.mp4"
    mestre_event = MagicMock(spec=ft.FilePickerResultEvent, files=[mock_file_mestre])

    # Chama o método que lida com o resultado da seleção do arquivo do mestre.
    app_instance.pick_file_result(mestre_event, is_aluno=False)

    # --- Verificações para o upload do MESTRE ---
    # Asserção 3: Verifica a mensagem de feedback específica para o mestre (antes de habilitar o botão).
    assert app_instance.status_text.value == "Vídeos carregados. Pronto para analisar."
    print("✓ Feedback de 'pronto para analisar' verificado.")
    
    # Asserção 4 (Final): Verifica se o botão de análise AGORA está habilitado.
    assert app_instance.analyze_button.disabled is False, "O botão de análise deveria estar habilitado após ambos os uploads."
    print("✓ Botão de análise habilitado com sucesso após ambos os uploads.")


def test_upload_canceled(app_instance: KravMagaApp):
    """
    Testa o cenário onde o usuário abre o seletor de arquivos, mas cancela a operação.
    
    Cenário: O usuário clica em "Upload", mas fecha a janela sem escolher um arquivo.
    Resultado Esperado: A aplicação deve exibir uma mensagem informando que nenhum arquivo foi selecionado.
    """
    print("\nExecutando test_upload_canceled...")

    # Cria um evento de seleção de arquivo falso e VAZIO.
    canceled_event = MagicMock(spec=ft.FilePickerResultEvent, files=[])

    # Chama a função de callback com o evento vazio.
    app_instance.pick_file_result(canceled_event, is_aluno=True)

    # Asserção: Verifica se a mensagem de status reflete a ação cancelada.
    assert app_instance.status_text.value == "Nenhum vídeo do aluno selecionado."
    print("✓ Feedback para upload cancelado verificado com sucesso.")