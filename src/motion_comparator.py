# src/motion_comparator.py

import logging
import numpy as np
import mediapipe as mp
from src.utils import get_logger, calculate_angle

logger = get_logger(__name__)


class MotionComparator:
    """
    Compara os movimentos do aluno com os do mestre com lógica aprimorada e feedback em português.
    """

    def __init__(self):
        """
        Construtor da classe MotionComparator.
        Define os ângulos chave para a análise e seus nomes legíveis.
        """
        logger.info("Inicializando MotionComparator.")
        # Define as articulações (vértices) e os pontos que formam os ângulos.
        self.KEY_ANGLES = {
            "LEFT_ELBOW_ANGLE": ("LEFT_SHOULDER", "LEFT_ELBOW", "LEFT_WRIST"),
            "RIGHT_ELBOW_ANGLE": ("RIGHT_SHOULDER", "RIGHT_ELBOW", "RIGHT_WRIST"),
            "LEFT_SHOULDER_ANGLE": ("LEFT_HIP", "LEFT_SHOULDER", "LEFT_ELBOW"),
            "RIGHT_SHOULDER_ANGLE": ("RIGHT_HIP", "RIGHT_SHOULDER", "RIGHT_ELBOW"),
            "LEFT_KNEE_ANGLE": ("LEFT_HIP", "LEFT_KNEE", "LEFT_ANKLE"),
            "RIGHT_KNEE_ANGLE": ("RIGHT_HIP", "RIGHT_KNEE", "RIGHT_ANKLE"),
            "LEFT_HIP_ANGLE": ("LEFT_SHOULDER", "LEFT_HIP", "LEFT_KNEE"),
            "RIGHT_HIP_ANGLE": ("RIGHT_SHOULDER", "RIGHT_HIP", "RIGHT_KNEE"),
        }
        # Mapeia os nomes dos landmarks para seus índices numéricos no MediaPipe.
        self.landmark_indices = {
            name: landmark.value
            for name, landmark in mp.solutions.pose.PoseLandmark.__members__.items()
        }
        # Dicionário para traduzir os nomes dos ângulos para o relatório em português.
        self.readable_angle_names = {
            "LEFT_ELBOW_ANGLE": "Cotovelo Esquerdo",
            "RIGHT_ELBOW_ANGLE": "Cotovelo Direito",
            "LEFT_SHOULDER_ANGLE": "Ombro Esquerdo",
            "RIGHT_SHOULDER_ANGLE": "Ombro Direito",
            "LEFT_KNEE_ANGLE": "Joelho Esquerdo",
            "RIGHT_KNEE_ANGLE": "Joelho Direito",
            "LEFT_HIP_ANGLE": "Quadril Esquerdo",
            "RIGHT_HIP_ANGLE": "Quadril Direito",
        }
        logger.info(f"Ângulos chave definidos: {list(self.KEY_ANGLES.keys())}")

    def _get_landmark_coords(self, landmarks_data: list, name: str) -> dict:
        """Função auxiliar para encontrar um landmark pelo nome na lista."""
        if not landmarks_data:
            raise ValueError(f"Lista de landmarks está vazia.")
        # Procura o dicionário do landmark pelo seu nome.
        landmark = next((lm for lm in landmarks_data if lm["name"] == name), None)
        if landmark is None:
            raise ValueError(f"Landmark '{name}' não encontrado.")
        return landmark

    def compare_poses(self, aluno_landmarks_list, mestre_landmarks_list):
        """
        Compara as poses de aluno e mestre, frame a frame, com lógica aprimorada
        para lidar com landmarks de baixa visibilidade.
        """
        # Se uma das poses não foi detectada, retorna um estado neutro.
        if not aluno_landmarks_list or not mestre_landmarks_list:
            return 0.0, "Aguardando pose...", {}

        angles_aluno, angles_mestre, angle_diffs = {}, {}, {}

        # Itera sobre cada ângulo que definimos como importante.
        for angle_name, (p1, p2, p3) in self.KEY_ANGLES.items():
            try:
                # Calcula o ângulo para o aluno.
                aluno_angle = calculate_angle(
                    self._get_landmark_coords(aluno_landmarks_list, p1),
                    self._get_landmark_coords(aluno_landmarks_list, p2),
                    self._get_landmark_coords(aluno_landmarks_list, p3),
                )
                angles_aluno[angle_name] = aluno_angle

                # Calcula o ângulo para o mestre.
                mestre_angle = calculate_angle(
                    self._get_landmark_coords(mestre_landmarks_list, p1),
                    self._get_landmark_coords(mestre_landmarks_list, p2),
                    self._get_landmark_coords(mestre_landmarks_list, p3),
                )
                angles_mestre[angle_name] = mestre_angle

                # --- LÓGICA DE CORREÇÃO ---
                # Se algum dos ângulos for 0.0 (indicando baixa visibilidade),
                # a diferença é considerada 0 para não gerar um "falso negativo".
                # A penalidade só ocorre se ambos os ângulos forem válidos e diferentes.
                if aluno_angle == 0.0 or mestre_angle == 0.0:
                    angle_diffs[angle_name] = 0.0
                else:
                    angle_diffs[angle_name] = abs(aluno_angle - mestre_angle)

            except ValueError as e:
                # Se um landmark não for encontrado, trata como erro e assume a pior diferença.
                logger.warning(f"Não foi possível calcular o ângulo {angle_name}: {e}")
                (
                    angles_aluno[angle_name],
                    angles_mestre[angle_name],
                    angle_diffs[angle_name],
                ) = (0, 0, 180)

        # A lógica de pontuação é baseada na média da similaridade de cada ângulo.
        # Similaridade = 100% para 0 graus de diferença, 0% para 180 graus.
        similarities = [max(0, 1 - (diff / 180)) for diff in angle_diffs.values()]
        score = np.mean(similarities) * 100 if similarities else 0

        # Gera o feedback textual com base nas diferenças calculadas.
        feedback = self._generate_feedback(angle_diffs, angles_aluno, angles_mestre)
        return score, feedback, angle_diffs

    def _generate_feedback(self, angle_diffs, angles_aluno, angles_mestre):
        """Gera feedback consolidado para todos os ângulos com erros significativos."""
        if not angle_diffs:
            return "Movimento Perfeito!"

        error_threshold = 15.0  # Limite de 15 graus para considerar um erro.
        errors = []

        for angle_name, diff in angle_diffs.items():
            if diff > error_threshold:
                aluno_angle = angles_aluno.get(angle_name, 0)
                mestre_angle = angles_mestre.get(angle_name, 0)
                readable_label = self.readable_angle_names.get(angle_name, angle_name)

                # Só gera feedback se ambos os ângulos forem válidos (diferentes de 0).
                if aluno_angle > 0 and mestre_angle > 0:
                    action = "Aumente" if aluno_angle < mestre_angle else "Diminua"
                    errors.append(f"{action} o ângulo do {readable_label}")

        if not errors:
            return "Excelente movimento!"

        feedback = ". ".join(errors)
        logger.info(f"Feedback gerado: '{feedback}'")
        return feedback
