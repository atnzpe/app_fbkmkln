# src/playlist_service.py

import os
import json
import logging
from src.config import RANK_HIERARCHY

logger = logging.getLogger(__name__)


class PlaylistService:
    def __init__(self, videos_base_path: str):
        self.videos_base_path = videos_base_path
        logger.debug(
            f"PlaylistService inicializado com o caminho base: {self.videos_base_path}"
        )

    def get_rank_playlist(self, rank: str) -> list[dict]:
        playlist_file = os.path.join(self.videos_base_path, rank, "playlist.json")
        if not os.path.exists(playlist_file):
            logger.warning(
                f"Arquivo de playlist não encontrado para a faixa '{rank}' em: {playlist_file}"
            )
            return []
        try:
            with open(playlist_file, "r", encoding="utf-8") as f:
                playlist_data = json.load(f)
                # **ALTERAÇÃO:** Adiciona a informação da pasta da faixa em cada vídeo.
                for video_info in playlist_data:
                    video_info["rank_folder"] = rank
                logger.info(
                    f"Playlist para a faixa '{rank}' carregada com sucesso com {len(playlist_data)} vídeos."
                )
                return playlist_data
        except Exception as e:
            logger.error(
                f"Erro ao ler ou processar o arquivo JSON '{playlist_file}': {e}",
                exc_info=True,
            )
            return []

    def get_exam_playlist(self, target_rank: str) -> list[dict]:
        logger.info(f"Construindo playlist de exame para a faixa alvo: {target_rank}")
        exam_playlist = []
        for rank in RANK_HIERARCHY:
            rank_playlist = self.get_rank_playlist(rank)
            exam_playlist.extend(rank_playlist)
            if rank == target_rank:
                break
        logger.info(
            f"Playlist de exame para '{target_rank}' construída com um total de {len(exam_playlist)} vídeos."
        )
        return exam_playlist
