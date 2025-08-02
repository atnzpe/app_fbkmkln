# src/playlist_service.py

# os é usado para manipulação de caminhos de arquivos.
import os

# json é usado para ler e interpretar o conteúdo dos arquivos playlist.json.
import json

# logging é usado para registrar informações e erros.
import logging

# Importa a hierarquia de faixas para a lógica do exame.
from src.config import RANK_HIERARCHY

# Obtém uma instância do logger.
logger = logging.getLogger(__name__)


class PlaylistService:
    """
    Serviço responsável por carregar e construir as playlists de treino
    a partir dos arquivos de configuração playlist.json.
    """

    def __init__(self, videos_base_path: str):
        """
        Construtor do serviço.
        Args:
            videos_base_path (str): O caminho para a pasta principal de vídeos (ex: 'assets/videos_tecnicas').
        """
        # Armazena o caminho base onde as pastas das faixas estão localizadas.
        self.videos_base_path = videos_base_path
        logger.debug(
            f"PlaylistService inicializado com o caminho base: {self.videos_base_path}"
        )

    def get_rank_playlist(self, rank: str) -> list[dict]:
        """
        Carrega a playlist para uma única graduação.

        Args:
            rank (str): O nome da graduação (ex: "Amarela").

        Returns:
            list[dict]: Uma lista de dicionários, onde cada dicionário representa um vídeo.
        """
        logger.info(f"Tentando carregar a playlist para a faixa: {rank}")
        # Constrói o caminho completo para o arquivo playlist.json da faixa especificada.
        playlist_file = os.path.join(self.videos_base_path, rank, "playlist.json")

        # Verifica se o arquivo de playlist realmente existe.
        if not os.path.exists(playlist_file):
            logger.warning(
                f"Arquivo de playlist não encontrado para a faixa '{rank}' em: {playlist_file}"
            )
            return []

        try:
            # Abre e lê o arquivo JSON.
            with open(playlist_file, "r", encoding="utf-8") as f:
                playlist_data = json.load(f)
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
        """
        Constrói uma playlist de exame, consolidando as playlists de todas as faixas
        até a graduação alvo.

        Args:
            target_rank (str): A faixa para a qual o exame está sendo simulado (ex: "Laranja").

        Returns:
            list[dict]: Uma lista consolidada de dicionários de vídeo para o exame.
        """
        logger.info(f"Construindo playlist de exame para a faixa alvo: {target_rank}")

        # Inicia uma lista vazia que irá acumular todos os vídeos do exame.
        exam_playlist = []

        # Itera sobre a hierarquia de faixas definida no nosso arquivo de configuração.
        for rank in RANK_HIERARCHY:
            # Para cada faixa na hierarquia, carrega sua playlist de treino.
            rank_playlist = self.get_rank_playlist(rank)
            # Adiciona (estende) a playlist do exame com os vídeos da faixa atual.
            exam_playlist.extend(rank_playlist)

            # Se a faixa atual for a faixa alvo do exame, interrompe o loop.
            if rank == target_rank:
                break

        logger.info(
            f"Playlist de exame para '{target_rank}' construída com um total de {len(exam_playlist)} vídeos."
        )
        return exam_playlist
