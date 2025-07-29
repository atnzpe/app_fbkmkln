# tests/test_pose_estimator.py
import pytest
from unittest.mock import MagicMock, patch
from src.pose_estimator import PoseEstimator
from src.utils import get_logger # Importar para mockar o logger
import mediapipe as mp
import numpy as np
import cv2

# Mock do logger para evitar saída real durante os testes e verificar chamadas
@pytest.fixture(autouse=True)
def mock_logger():
    """
    Mocka a função get_logger para controlar o logger nos testes.
    """
    with patch('src.pose_estimator.get_logger') as mock_get_logger:
        mock_logger_instance = MagicMock()
        mock_get_logger.return_value = mock_logger_instance
        yield mock_logger_instance

# Mock do mp.solutions.pose.Pose e mp.solutions.drawing_utils
@pytest.fixture(autouse=True)
def mock_mediapipe_components():
    """
    Mocka os componentes do MediaPipe para isolar o teste do PoseEstimator.
    """
    with patch('mediapipe.solutions.pose.Pose') as MockPose, \
         patch('mediapipe.solutions.drawing_utils') as MockDrawingUtils, \
         patch('mediapipe.solutions.drawing_styles') as MockDrawingStyles:
        yield MockPose, MockDrawingUtils, MockDrawingStyles

def test_pose_estimator_initialization(mock_logger, mock_mediapipe_components):
    """
    Testa se o PoseEstimator é inicializado corretamente e se o logger é usado.
    """
    MockPose, MockDrawingUtils, MockDrawingStyles = mock_mediapipe_components

    # Instancia o PoseEstimator
    estimator = PoseEstimator()

    # Verifica se o logger foi chamado para informar a inicialização
    mock_logger.info.assert_any_call("Inicializando PoseEstimator com MediaPipe Pose...")
    mock_logger.info.assert_any_call("Modelo MediaPipe Pose inicializado.")
    mock_logger.info.assert_any_call("Utilidades de desenho do MediaPipe inicializadas.")

    # Verifica se o modelo Pose foi instanciado com os parâmetros corretos
    MockPose.assert_called_once_with(
        static_image_mode=False,
        model_complexity=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )

    # Verifica se os utilitários de desenho foram atribuídos
    assert estimator.mp_drawing == MockDrawingUtils
    assert estimator.mp_drawing_styles == MockDrawingStyles

def test_pose_estimator_del_method(mock_logger, mock_mediapipe_components):
    """
    Testa se o método __del__ do PoseEstimator é executado sem erros
    e se os recursos são "liberados" (mockados).
    """
    MockPose, _, _ = mock_mediapipe_components

    # Instancia o PoseEstimator
    estimator = PoseEstimator()

    # Garante que o método close do mock do pose seja chamado
    MockPose.return_value.close = MagicMock()

    # Chama explicitamente __del__ para testar, embora Python o chame automaticamente
    estimator.__del__()

    # Verifica se o logger registrou a destruição
    mock_logger.info.assert_any_call("Destruindo PoseEstimator e liberando recursos do MediaPipe Pose.")
    mock_logger.info.assert_any_call("Recursos do MediaPipe Pose liberados.")

    # Verifica se o método close do modelo pose foi chamado
    MockPose.return_value.close.assert_called_once()

def test_estimate_pose(mock_logger, mock_mediapipe_components):
    """
    Testa o método estimate_pose.
    """
    MockPose, MockDrawingUtils, MockDrawingStyles = mock_mediapipe_components
    estimator = PoseEstimator()

    # Cria uma imagem dummy
    dummy_image = np.zeros((480, 640, 3), dtype=np.uint8)

    # Mock do retorno de pose.process
    mock_results = MagicMock()
    mock_results.pose_landmarks = MagicMock() # Simula que landmarks foram detectados
    MockPose.return_value.process.return_value = mock_results

    # Mock do draw_landmarks para verificar se foi chamado
    MockDrawingUtils.draw_landmarks = MagicMock()

    results, annotated_image = estimator.estimate_pose(dummy_image)

    # Verifica se pose.process foi chamado
    MockPose.return_value.process.assert_called_once()

    # Verifica se draw_landmarks foi chamado (pois mock_results.pose_landmarks existe)
    MockDrawingUtils.draw_landmarks.assert_called_once()
    assert results == mock_results
    assert isinstance(annotated_image, np.ndarray)

def test_estimate_pose_no_landmarks(mock_logger, mock_mediapipe_components):
    """
    Testa o método estimate_pose quando nenhum landmark é detectado.
    """
    MockPose, MockDrawingUtils, MockDrawingStyles = mock_mediapipe_components
    estimator = PoseEstimator()

    dummy_image = np.zeros((480, 640, 3), dtype=np.uint8)

    # Mock do retorno de pose.process sem landmarks
    mock_results = MagicMock()
    mock_results.pose_landmarks = None # Simula que nenhum landmark foi detectado
    MockPose.return_value.process.return_value = mock_results

    # Mock do draw_landmarks para verificar que NÃO foi chamado
    MockDrawingUtils.draw_landmarks = MagicMock()

    results, annotated_image = estimator.estimate_pose(dummy_image)

    # Verifica se pose.process foi chamado
    MockPose.return_value.process.assert_called_once()

    # Verifica se draw_landmarks NÃO foi chamado
    MockDrawingUtils.draw_landmarks.assert_not_called()
    assert results == mock_results
    assert isinstance(annotated_image, np.ndarray)

def test_get_landmarks_as_list(mock_logger):
    """
    Testa o método get_landmarks_as_list.
    """
    estimator = PoseEstimator()

    # Cria um mock de pose_landmarks
    mock_landmark1 = MagicMock(x=0.1, y=0.2, z=0.3, visibility=0.9)
    mock_landmark2 = MagicMock(x=0.4, y=0.5, z=0.6, visibility=0.8)
    mock_pose_landmarks = MagicMock()
    mock_pose_landmarks.landmark = [mock_landmark1, mock_landmark2]

    landmarks_list = estimator.get_landmarks_as_list(mock_pose_landmarks)

    expected_list = [
        {'x': 0.1, 'y': 0.2, 'z': 0.3, 'visibility': 0.9},
        {'x': 0.4, 'y': 0.5, 'z': 0.6, 'visibility': 0.8}
    ]
    assert landmarks_list == expected_list

def test_get_landmarks_as_list_none_input(mock_logger):
    """
    Testa o método get_landmarks_as_list com entrada None.
    """
    estimator = PoseEstimator()
    landmarks_list = estimator.get_landmarks_as_list(None)
    assert landmarks_list is None