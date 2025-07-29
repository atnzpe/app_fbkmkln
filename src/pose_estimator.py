# src/pose_estimator.py

import mediapipe as mp
import cv2
import numpy as np
from src.utils import get_logger

# Obtém uma instância do logger para este módulo.
logger = get_logger(__name__)


class PoseEstimator:
    """
    Estima a pose usando MediaPipe Pose e permite desenhar esqueletos com estilos customizados.
    """

    def __init__(self):
        """
        Construtor da classe PoseEstimator.
        Inicializa o modelo MediaPipe Pose e define os diferentes estilos de desenho.
        """
        logger.info("Inicializando PoseEstimator com MediaPipe Pose...")
        # Inicializa o modelo de detecção de pose do MediaPipe.
        self.pose = mp.solutions.pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        # Utilitário de desenho do MediaPipe.
        self.mp_drawing = mp.solutions.drawing_utils

        # --- ESTILOS DE DESENHO PARA VÍDEO E PDF ---
        # Cor branca padrão para o esqueleto.
        self.default_style = self.mp_drawing.DrawingSpec(
            color=(255, 255, 255), thickness=2, circle_radius=2
        )
        # Cor verde para feedback de acerto.
        self.correct_style = self.mp_drawing.DrawingSpec(
            color=(0, 255, 0), thickness=3, circle_radius=4
        )
        # Cor vermelha para feedback de erro.
        self.incorrect_style = self.mp_drawing.DrawingSpec(
            color=(0, 0, 255), thickness=3, circle_radius=4
        )
        # Cor laranja para o lado esquerdo do corpo (no vídeo).
        self.left_side_style = self.mp_drawing.DrawingSpec(
            color=(0, 165, 255), thickness=2, circle_radius=2
        )  # Laranja
        # Cor azul para o lado direito do corpo (no vídeo).
        self.right_side_style = self.mp_drawing.DrawingSpec(
            color=(255, 100, 0), thickness=2, circle_radius=2
        )  # Azul

        # Mapeamento das conexões do esqueleto para os lados esquerdo e direito.
        # POSE_CONNECTIONS é uma lista de tuplas, cada tupla representa um "osso" conectando dois pontos (landmarks).
        pose_connections = mp.solutions.pose.POSE_CONNECTIONS

        # Filtra as conexões para identificar as que pertencem ao lado esquerdo do corpo.
        self.left_connections = {
            conn
            for conn in pose_connections
            if "LEFT" in str(conn[0]) and "LEFT" in str(conn[1])
        }
        # Filtra as conexões para identificar as que pertencem ao lado direito do corpo.
        self.right_connections = {
            conn
            for conn in pose_connections
            if "RIGHT" in str(conn[0]) and "RIGHT" in str(conn[1])
        }
        # As conexões restantes são consideradas centrais (tronco).
        self.center_connections = (
            pose_connections - self.left_connections - self.right_connections
        )

        logger.info(
            "PoseEstimator inicializado com estilos de desenho por lado e por feedback."
        )

    def estimate_pose(self, image: np.ndarray):
        """
        Estima a pose em um único frame, sem desenhar o esqueleto.
        Apenas retorna os resultados da detecção.

        Args:
            image (np.ndarray): O frame de imagem em formato BGR.

        Returns:
            mediapipe.python.solutions.pose.PoseResults: Os resultados da detecção de pose.
        """
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_rgb.flags.writeable = False
        results = self.pose.process(image_rgb)
        return results

    def draw_skeleton_by_side(self, image: np.ndarray, pose_landmarks) -> np.ndarray:
        """
        Desenha o esqueleto na imagem com cores diferentes para cada lado.
        Lado esquerdo em laranja, lado direito em azul.

        Args:
            image (np.ndarray): A imagem onde o esqueleto será desenhado.
            pose_landmarks: O objeto de landmarks retornado pelo MediaPipe.

        Returns:
            np.ndarray: A imagem com o esqueleto colorido desenhado.
        """
        annotated_image = image.copy()
        if pose_landmarks:
            # Desenha as conexões do lado esquerdo em laranja.
            self.mp_drawing.draw_landmarks(
                annotated_image,
                pose_landmarks,
                self.left_connections,
                self.left_side_style,
                self.left_side_style,
            )
            # Desenha as conexões do lado direito em azul.
            self.mp_drawing.draw_landmarks(
                annotated_image,
                pose_landmarks,
                self.right_connections,
                self.right_side_style,
                self.right_side_style,
            )
            # Desenha as conexões centrais com o estilo padrão (branco).
            self.mp_drawing.draw_landmarks(
                annotated_image,
                pose_landmarks,
                self.center_connections,
                self.default_style,
                self.default_style,
            )
        return annotated_image

    def draw_feedback_skeleton(
        self,
        image: np.ndarray,
        landmarks_list: list,
        angle_diffs: dict,
        key_angles: dict,
        threshold: float = 15.0,
    ) -> np.ndarray:
        """
        Desenha o esqueleto na imagem destacando acertos (verde) e erros (vermelho).
        Esta função foi corrigida para aceitar uma LISTA de landmarks, não o objeto MediaPipe.

        Args:
            image (np.ndarray): Imagem original para desenhar.
            landmarks_list (list): Lista de dicionários de landmarks (resultado de get_landmarks_as_list).
            angle_diffs (dict): Dicionário com as diferenças de ângulo para colorir.
            key_angles (dict): Mapeamento dos nomes dos ângulos para os landmarks que os formam.
            threshold (float): Limiar para considerar um ângulo como incorreto.

        Returns:
            np.ndarray: A imagem com o esqueleto de feedback.
        """
        annotated_image = image.copy()
        if not landmarks_list or not angle_diffs:
            return annotated_image

        # Dicionário para armazenar a cor de cada conexão.
        connection_colors = {}

        # Determina a cor de cada articulação com base na diferença de ângulo.
        for angle_name, diff in angle_diffs.items():
            style = self.correct_style if diff <= threshold else self.incorrect_style
            p1_name, p2_name, p3_name = key_angles[angle_name]

            # As duas "pernas" do ângulo (ex: Ombro-Cotovelo, Cotovelo-Pulso).
            connection1 = tuple(sorted((p1_name, p2_name)))
            connection2 = tuple(sorted((p2_name, p3_name)))

            # Prioriza o vermelho: se uma conexão fizer parte de um ângulo ruim, ela fica vermelha.
            if connection_colors.get(connection1) != self.incorrect_style.color:
                connection_colors[connection1] = style.color
            if connection_colors.get(connection2) != self.incorrect_style.color:
                connection_colors[connection2] = style.color

        # Desenha as conexões e os pontos com as cores definidas.
        for (p1_name, p2_name), color in connection_colors.items():
            p1 = next((lm for lm in landmarks_list if lm["name"] == p1_name), None)
            p2 = next((lm for lm in landmarks_list if lm["name"] == p2_name), None)

            if p1 and p2 and p1["visibility"] > 0.5 and p2["visibility"] > 0.5:
                pt1 = (int(p1["x"] * image.shape[1]), int(p1["y"] * image.shape[0]))
                pt2 = (int(p2["x"] * image.shape[1]), int(p2["y"] * image.shape[0]))
                # Desenha a linha e os círculos para cada conexão.
                cv2.line(annotated_image, pt1, pt2, color, self.correct_style.thickness)
                cv2.circle(
                    annotated_image, pt1, self.correct_style.circle_radius, color, -1
                )
                cv2.circle(
                    annotated_image, pt2, self.correct_style.circle_radius, color, -1
                )

        return annotated_image

    def get_landmarks_as_list(self, pose_landmarks):
        """Converte o objeto de landmarks do MediaPipe para uma lista de dicionários."""
        if not pose_landmarks:
            return None

        # Adiciona o nome do landmark ao dicionário para facilitar a busca.
        landmark_names = {
            v: k for k, v in mp.solutions.pose.PoseLandmark.__members__.items()
        }
        return [
            {
                "x": lm.x,
                "y": lm.y,
                "z": lm.z,
                "visibility": lm.visibility,
                "name": landmark_names[i],
            }
            for i, lm in enumerate(pose_landmarks.landmark)
        ]

    def __del__(self):
        """Destrutor para liberar os recursos do MediaPipe Pose."""
        if hasattr(self, "pose") and self.pose:
            self.pose.close()
            logger.info("Recursos do MediaPipe Pose liberados.")
