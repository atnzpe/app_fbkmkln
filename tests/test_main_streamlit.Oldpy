import pytest
from streamlit.testing.v1 import AppTest
import os
import sys
import numpy as np
import io

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@pytest.fixture(autouse=True)
def clean_streamlit_cache():
    pass


def test_streamlit_app_loads():
    at = AppTest.from_file("src/main_streamlit.py", default_timeout=5)
    at.run()
    assert (
        len(at.exception) == 0
    ), f"A aplicação Streamlit falhou ao carregar com exceções: {at.exception}"
    assert "🥋 Analisador de Movimentos de Krav Maga" in at.title[0].value


def test_streamlit_initial_status_message():
    at = AppTest.from_file("src/main_streamlit.py", default_timeout=5)
    at.run()
    assert (
        "Por favor, carregue ambos os vídeos para iniciar a análise."
        in at.warning[0].body
    )


def test_streamlit_analyze_button_initial_disabled_state():
    at = AppTest.from_file("src/main_streamlit.py", default_timeout=5)
    at.run()
    assert at.button("analyze_button").proto.disabled is True


def test_streamlit_analyze_button_enabled_after_simulated_upload():
    at = AppTest.from_file("src/main_streamlit.py", default_timeout=10)

    # Roda o app uma vez para inicializar
    at.run()

    # Debug print para ver o que 'at.file_uploader' retorna AGORA
    print(
        f"\nDebug (analyze_button_enabled_after_simulated_upload): at.file_uploader('aluno_video_uploader') result: {at.file_uploader('aluno_video_uploader')}"
    )

    # NOVO: Usamos at.file_uploader("key") diretamente
    aluno_uploader = at.file_uploader("aluno_video_uploader")
    mestre_uploader = at.file_uploader("mestre_video_uploader")

    aluno_uploader.set_value(io.BytesIO(b"dummy_video_data_aluno_mp4"), "aluno.mp4")
    mestre_uploader.set_value(io.BytesIO(b"dummy_video_data_mestre_mp4"), "mestre.mp4")

    at.run()  # Processa os uploads
    assert at.button("analyze_button").proto.disabled is False


def test_streamlit_analysis_flow_and_success_message(mocker):
    at = AppTest.from_file("src/main_streamlit.py", default_timeout=20)

    # Roda o app uma vez para inicializar
    at.run()

    mock_frame = np.zeros((100, 100, 3), dtype=np.uint8) + 128
    mock_landmarks = [{"x": 0.5, "y": 0.5, "z": 0.0, "visibility": 1.0}]
    mocker.patch(
        "src.video_analyzer.VideoAnalyzer.analyze_video",
        return_value=[(mock_frame, mock_landmarks)] * 5,
    )

    # Debug print para ver o que 'at.file_uploader' retorna AGORA
    print(
        f"\nDebug (analysis_flow_and_success_message): at.file_uploader('aluno_video_uploader') result: {at.file_uploader('aluno_video_uploader')}"
    )

    # NOVO: Usamos at.file_uploader("key") diretamente
    aluno_uploader = at.file_uploader("aluno_video_uploader")
    mestre_uploader = at.file_uploader("mestre_video_uploader")

    aluno_uploader.set_value(io.BytesIO(b"dummy_video_data_aluno_mp4"), "aluno.mp4")
    mestre_uploader.set_value(io.BytesIO(b"dummy_video_data_mestre_mp4"), "mestre.mp4")

    at.run()  # Processa os uploads e habilita o botão
    at.button("analyze_button").click()

    assert (
        "Iniciando a análise dos vídeos. Isso pode levar alguns minutos, por favor aguarde..."
        in at.info[0].body
    )
    assert "Ambos os vídeos processados! Exibindo resultados..." in at.success[0].body
    # A próxima asserção pode ser sensível ao Streamlit.text output
    # Se falhar, pode ser necessário ajustar a forma como o texto é capturado.
    assert (
        "Processamento do vídeo do Mestre concluído." in at.text[-1].value
        or "Análise de pose concluída! ✨" in at.text[-1].value
    )

    assert len(at.image) >= 2
    assert at.slider("aluno_frame_slider").value == 0
    assert at.slider("mestre_frame_slider").value == 0
