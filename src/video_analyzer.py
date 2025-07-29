# src/video_analyzer.py

import cv2
import os
import tempfile
import threading
import numpy as np
from src.utils import get_logger
from src.pose_estimator import PoseEstimator
from src.motion_comparator import MotionComparator

logger = get_logger(__name__)


class VideoAnalyzer:
    """
    Classe responsável por analisar vídeos, detectar poses, comparar movimentos
    e fornecer feedback.
    """

    def __init__(self):
        logger.info("Inicializando VideoAnalyzer...")
        self.pose_estimator = PoseEstimator()
        self.motion_comparator = MotionComparator()

        # Armazena os frames originais (sem anotação)
        self.raw_frames_aluno = []
        self.raw_frames_mestre = []

        # Armazena os frames processados com esqueleto colorido por lado
        self.processed_frames_aluno = []
        self.processed_frames_mestre = []

        # Armazena a lista de dicionários de landmarks (para comparação)
        self.aluno_landmarks_list = []
        self.mestre_landmarks_list = []

        # CORREÇÃO: Armazena o objeto original de landmarks do MediaPipe (para redesenho)
        self.aluno_landmarks_raw = []
        self.mestre_landmarks_raw = []

        self.comparison_results = []

        self.cap_aluno = None
        self.cap_mestre = None
        self.video_aluno_path = None
        self.video_mestre_path = None

        self.is_processing = False
        self.processing_thread = None
        logger.info("Variáveis de estado do VideoAnalyzer configuradas.")

    def load_video_from_bytes(self, video_bytes: bytes, is_aluno: bool):
        # ... (código inalterado) ...
        logger.info(
            f"Carregando vídeo a partir de bytes para {'aluno' if is_aluno else 'mestre'}."
        )
        try:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
            temp_file.write(video_bytes)
            temp_file.close()
            video_path = temp_file.name

            if is_aluno:
                self.video_aluno_path = video_path
                self.cap_aluno = cv2.VideoCapture(video_path)
            else:
                self.video_mestre_path = video_path
                self.cap_mestre = cv2.VideoCapture(video_path)

            logger.info(
                f"Vídeo {'aluno' if is_aluno else 'mestre'} carregado de: {video_path}"
            )
            return video_path
        except Exception as e:
            logger.error(f"Erro ao carregar vídeo de bytes: {e}", exc_info=True)
            raise

    def analyze_and_compare(self, post_analysis_callback, progress_callback=None):
        # ... (código inalterado) ...
        if self.is_processing:
            logger.info("Análise já em andamento.")
            return

        def target():
            self._run_analysis_thread(progress_callback)
            post_analysis_callback()

        self.is_processing = True
        logger.info("Iniciando a thread de processamento de vídeo.")
        self.processing_thread = threading.Thread(target=target, daemon=True)
        self.processing_thread.start()

    def _run_analysis_thread(self, progress_callback=None):
        try:
            logger.info("Thread de análise iniciada.")

            # Limpa listas de dados de análises anteriores
            for lst in [
                self.aluno_landmarks_list,
                self.mestre_landmarks_list,
                self.aluno_landmarks_raw,
                self.mestre_landmarks_raw,
                self.processed_frames_aluno,
                self.processed_frames_mestre,
                self.raw_frames_aluno,
                self.raw_frames_mestre,
                self.comparison_results,
            ]:
                lst.clear()

            num_frames = min(
                int(self.cap_aluno.get(cv2.CAP_PROP_FRAME_COUNT)),
                int(self.cap_mestre.get(cv2.CAP_PROP_FRAME_COUNT)),
            )
            logger.info(f"Iniciando processamento e comparação de {num_frames} frames.")

            for i in range(num_frames):
                ret_aluno, frame_aluno = self.cap_aluno.read()
                ret_mestre, frame_mestre = self.cap_mestre.read()

                if not ret_aluno or not ret_mestre:
                    break

                self.raw_frames_aluno.append(frame_aluno)
                self.raw_frames_mestre.append(frame_mestre)

                results_aluno = self.pose_estimator.estimate_pose(frame_aluno)
                results_mestre = self.pose_estimator.estimate_pose(frame_mestre)

                # ALTERAÇÃO: Usa a nova função para desenhar o esqueleto colorido por lado
                annotated_aluno = self.pose_estimator.draw_skeleton_by_side(
                    frame_aluno, results_aluno.pose_landmarks
                )
                annotated_mestre = self.pose_estimator.draw_skeleton_by_side(
                    frame_mestre, results_mestre.pose_landmarks
                )

                self.processed_frames_aluno.append(annotated_aluno)
                self.processed_frames_mestre.append(annotated_mestre)

                # Armazena ambos os formatos de landmarks
                lm_list_aluno = self.pose_estimator.get_landmarks_as_list(
                    results_aluno.pose_landmarks
                )
                lm_list_mestre = self.pose_estimator.get_landmarks_as_list(
                    results_mestre.pose_landmarks
                )

                self.aluno_landmarks_list.append(lm_list_aluno)
                self.mestre_landmarks_list.append(lm_list_mestre)
                self.aluno_landmarks_raw.append(results_aluno.pose_landmarks)
                self.mestre_landmarks_raw.append(results_mestre.pose_landmarks)

                score, feedback, diffs = self.motion_comparator.compare_poses(
                    lm_list_aluno, lm_list_mestre
                )
                self.comparison_results.append(
                    {"score": score, "feedback": feedback, "diffs": diffs}
                )

                if progress_callback:
                    progress_callback((i + 1) / num_frames)

        except Exception as e:
            logger.error(f"Erro na thread de análise: {e}", exc_info=True)
        finally:
            self.is_processing = False
            if self.cap_aluno:
                self.cap_aluno.release()
            if self.cap_mestre:
                self.cap_mestre.release()
            logger.info("Thread de análise finalizada.")

    def __del__(self):
        # ... (código inalterado) ...
        logger.info("Destruindo VideoAnalyzer e limpando arquivos.")
        try:
            if self.video_aluno_path and os.path.exists(self.video_aluno_path):
                os.remove(self.video_aluno_path)
            if self.video_mestre_path and os.path.exists(self.video_mestre_path):
                os.remove(self.video_mestre_path)
        except Exception as e:
            logger.error(f"Erro ao limpar arquivos temporários: {e}")
