# tests/test_video_analyzer.py
import pytest
from unittest.mock import MagicMock, patch
from src.video_analyzer import VideoAnalyzer
from src.pose_estimator import PoseEstimator
from src.motion_comparator import MotionComparator
from src.utils import get_logger # Importar para mockar o logger

# Mock do logger para evitar saída real durante os testes e verificar chamadas
@pytest.fixture(autouse=True)
def mock_logger():
    """
    Mocka a função get_logger para controlar o logger nos testes.
    """
    with patch('src.video_analyzer.get_logger') as mock_get_logger:
        mock_logger_instance = MagicMock()
        mock_get_logger.return_value = mock_logger_instance
        yield mock_logger_instance

# Mock do PoseEstimator e MotionComparator para isolar o teste do VideoAnalyzer
@pytest.fixture(autouse=True)
def mock_components():
    """
    Mocka PoseEstimator e MotionComparator para evitar dependências externas.
    """
    with patch('src.video_analyzer.PoseEstimator') as MockPoseEstimator, \
         patch('src.video_analyzer.MotionComparator') as MockMotionComparator:
        yield MockPoseEstimator, MockMotionComparator

def test_video_analyzer_initialization(mock_logger, mock_components):
    """
    Testa se o VideoAnalyzer é inicializado corretamente e se o logger é usado.
    """
    MockPoseEstimator, MockMotionComparator = mock_components

    # Instancia o VideoAnalyzer
    analyzer = VideoAnalyzer()

    # Verifica se o logger foi chamado para informar a inicialização
    mock_logger.info.assert_any_call("Inicializando VideoAnalyzer...")
    mock_logger.info.assert_any_call("PoseEstimator inicializado.")
    mock_logger.info.assert_any_call("MotionComparator inicializado.")
    mock_logger.info.assert_any_call("Variáveis de estado do VideoAnalyzer configuradas.")

    # Verifica se PoseEstimator e MotionComparator foram instanciados
    MockPoseEstimator.assert_called_once()
    MockMotionComparator.assert_called_once()

    # Verifica se os atributos foram definidos
    assert isinstance(analyzer.pose_estimator, MagicMock) # Deve ser uma instância do mock
    assert isinstance(analyzer.motion_comparator, MagicMock) # Deve ser uma instância do mock
    assert analyzer.cap_aluno is None
    assert analyzer.cap_mestre is None
    assert analyzer.video_aluno_path is None
    assert analyzer.video_mestre_path is None
    assert analyzer.aluno_landmarks == []
    assert analyzer.mestre_landmarks == []
    assert analyzer.comparison_results == []
    assert analyzer.is_processing is False
    assert analyzer.processing_thread is None
    assert analyzer.current_frame_aluno is None
    assert analyzer.current_frame_mestre is None

def test_video_analyzer_del_method(mock_logger, mock_components):
    """
    Testa se o método __del__ do VideoAnalyzer é executado sem erros
    e se os recursos são "liberados" (mockados).
    """
    MockPoseEstimator, MockMotionComparator = mock_components

    # Instancia o VideoAnalyzer
    analyzer = VideoAnalyzer()

    # Simula a existência de recursos para serem liberados
    analyzer.cap_aluno = MagicMock()
    analyzer.cap_aluno.isOpened.return_value = True
    analyzer.cap_mestre = MagicMock()
    analyzer.cap_mestre.isOpened.return_value = True

    # Simula arquivos temporários
    with patch('os.path.exists', return_value=True), \
         patch('os.remove') as mock_os_remove:
        analyzer.video_aluno_path = "/tmp/aluno.mp4"
        analyzer.video_mestre_path = "/tmp/mestre.mp4"

        # Chama explicitamente __del__ para testar, embora Python o chame automaticamente
        analyzer.__del__()

        # Verifica se o logger registrou a destruição
        mock_logger.info.assert_any_call("Destruindo VideoAnalyzer e liberando recursos.")
        mock_logger.info.assert_any_call("Cap_aluno liberado.")
        mock_logger.info.assert_any_call("Cap_mestre liberado.")
        mock_logger.info.assert_any_call(f"Arquivo temporário do aluno removido: {analyzer.video_aluno_path}")
        mock_logger.info.assert_any_call(f"Arquivo temporário do mestre removido: {analyzer.video_mestre_path}")
        mock_logger.info.assert_any_call("PoseEstimator recursos liberados.")
        mock_logger.info.assert_any_call("MotionComparator recursos liberados.")

        # Verifica se os métodos de liberação foram chamados nos mocks
        analyzer.cap_aluno.release.assert_called_once()
        analyzer.cap_mestre.release.assert_called_once()
        mock_os_remove.assert_any_call("/tmp/aluno.mp4")
        mock_os_remove.assert_any_call("/tmp/mestre.mp4")
        MockPoseEstimator.return_value.__del__.assert_called_once()
        MockMotionComparator.return_value.__del__.assert_called_once()