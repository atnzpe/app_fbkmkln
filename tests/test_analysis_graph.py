# -*- coding: utf-8 -*-

# --------------------------------------------------------------------------------------------------
#  Krav Maga Motion Analyzer - Testes
#  version 1.2.0
#  Copyright (C) 2024,
#  開発者名 [Sujeito Programador]
# --------------------------------------------------------------------------------------------------

# --------------------------------------------------------------------------------------------------
# Importação de Bibliotecas
# --------------------------------------------------------------------------------------------------

import pytest
from unittest.mock import MagicMock, patch
import flet as ft
import plotly.graph_objects as go

# Importa as classes e funções que serão testadas ou mockadas.
from main import KravMagaApp
from src.video_analyzer import VideoAnalyzer

# --------------------------------------------------------------------------------------------------
# Fixtures e Dados de Teste
# --------------------------------------------------------------------------------------------------

@pytest.fixture
def mock_app_with_data(event_loop):
    """
    Cria uma instância mock da aplicação Flet com dados de análise já processados.
    Isso nos permite testar a lógica da UI sem rodar a análise de vídeo completa.
    """
    # Mock da página Flet
    mock_page = MagicMock(spec=ft.Page)
    
    # Cria a instância da App. O __init__ construirá a UI com mocks.
    # Usamos patch para evitar que ft.app seja chamado.
    with patch('flet.app'):
        app = KravMagaApp(mock_page)

    # Simula um VideoAnalyzer com dados já processados.
    app.video_analyzer = MagicMock(spec=VideoAnalyzer)
    app.video_analyzer.angle_diffs_history = [
        {'LEFT_ELBOW_ANGLE': 10, 'RIGHT_KNEE_ANGLE': 5},
        {'LEFT_ELBOW_ANGLE': 12, 'RIGHT_KNEE_ANGLE': 7},
        {'LEFT_ELBOW_ANGLE': 8, 'RIGHT_KNEE_ANGLE': 6},
    ]
    
    # Mock dos controles da UI que serão usados no teste.
    app.analysis_chart_control = MagicMock(spec=ft.plotly_chart.PlotlyChart)
    app.angle_dropdown_control = MagicMock(spec=ft.Dropdown)
    
    return app

# --------------------------------------------------------------------------------------------------
# Casos de Teste para a Lógica do Gráfico
# --------------------------------------------------------------------------------------------------

def test_update_graph_with_selected_angle(mock_app_with_data):
    """
    Testa se a função `update_frame_display` cria corretamente a figura do Plotly.
    
    Cenário: Um ângulo é selecionado no dropdown e a função de atualização é chamada.
    Resultado Esperado: O controle do gráfico (`analysis_chart_control`) deve receber
                       um objeto `Figure` do Plotly contendo os dados corretos.
    """
    app = mock_app_with_data
    
    # Simula a seleção de um ângulo pelo usuário no dropdown.
    selected_angle = 'LEFT_ELBOW_ANGLE'
    app.angle_dropdown_control.value = selected_angle
    
    current_frame = 1 # O frame que o usuário está visualizando.
    
    # Chama o método que atualiza o gráfico.
    app.update_frame_display(current_frame)
    
    # Asserções: Verificamos se o gráfico foi criado e configurado como esperado.
    
    # 1. Verifica se a propriedade 'figure' do nosso controle de gráfico foi atribuída.
    #    Isso significa que um gráfico foi gerado.
    assert app.analysis_chart_control.figure is not None
    
    # 2. Verifica se o objeto atribuído é de fato uma figura do Plotly.
    figure = app.analysis_chart_control.figure
    assert isinstance(figure, go.Figure)
    
    # 3. Verifica se os dados no gráfico estão corretos.
    #    O gráfico deve ter uma linha (trace) com os dados de diferença do cotovelo.
    graph_data = figure.data[0]
    expected_y_data = (10, 12, 8) # Extraído do mock_analysis_data.
    assert tuple(graph_data.y) == expected_y_data
    
    # 4. Verifica se a linha vertical que marca o frame atual foi adicionada corretamente.
    #    A linha vertical é uma "shape" no layout da figura do Plotly.
    assert len(figure.layout.shapes) == 1
    vertical_line = figure.layout.shapes[0]
    assert vertical_line.type == 'line'
    assert vertical_line.x0 == current_frame # Verifica a posição da linha.

def test_update_graph_with_no_angle_selected(mock_app_with_data):
    """
    Testa o comportamento quando nenhum ângulo foi selecionado no dropdown.
    
    Cenário: A função de atualização é chamada, mas o valor do dropdown é None.
    Resultado Esperado: O gráfico não deve ser atualizado para evitar erros.
    """
    app = mock_app_with_data
    
    # Garante que nenhum ângulo está selecionado.
    app.angle_dropdown_control.value = None
    
    # Zera a propriedade 'figure' para garantir que o teste está limpo.
    app.analysis_chart_control.figure = None
    
    # Chama o método de atualização.
    app.update_frame_display(0)
    
    # Asserção: A propriedade 'figure' deve permanecer None, pois não havia
    # ângulo selecionado para plotar.
    assert app.analysis_chart_control.figure is None