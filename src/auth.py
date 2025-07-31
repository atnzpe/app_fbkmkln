# src/auth.py

import pandas as pd
import logging
from src.config import RANK_HIERARCHY

logger = logging.getLogger(__name__)


class AuthService:
    """
    Serviço de autenticação e autorização que lê dados de uma planilha.
    """

    def __init__(self, sheet_url: str):
        self.sheet_url = sheet_url
        self.user_data = None
        self.load_users()

    def load_users(self):
        # ... (código existente inalterado) ...
        try:
            logger.info(f"Recarregando dados dos usuários de: {self.sheet_url}")
            self.user_data = pd.read_csv(self.sheet_url, dtype={"CPF": str})
            logger.info(f"{len(self.user_data)} usuários carregados com sucesso.")
        except Exception as e:
            logger.error(
                f"Falha ao carregar ou processar a planilha de usuários: {e}",
                exc_info=True,
            )
            self.user_data = pd.DataFrame()

    def login(self, cpf: str, senha: str) -> dict | None:
        # ... (código existente inalterado) ...
        if self.user_data is None or self.user_data.empty:
            logger.error("Tentativa de login sem dados de usuários carregados.")
            return None
        cpf_cleaned = cpf.replace(".", "").replace("-", "")
        user_row = self.user_data[self.user_data["CPF"] == cpf_cleaned]
        if not user_row.empty:
            user = user_row.iloc[0]
            if str(user["Senha"]) == senha and user["STATUS"] == "Ativo":
                logger.info(f"Login bem-sucedido para o usuário: {user['NOME']}.")
                return user.to_dict()
        logger.warning(f"Tentativa de login falhou para o CPF: {cpf_cleaned}.")
        return None

    def get_accessible_ranks(self, user_data: dict) -> list[str]:
        """
        Determina quais graduações um usuário pode acessar.
        - Se a faixa for "PRETA", libera todas.
        - Para as outras faixas, libera "todas as anteriores + a atual + a próxima".
        """
        user_rank = user_data.get("GRADUACAO_ATUAL")
        logger.debug(f"Calculando permissões para a faixa: '{user_rank}'.")

        # **REGRA ATUALIZADA:** Se a graduação do usuário for "PRETA", concede acesso total.
        if user_rank == "PRETA":
            logger.info(
                f"Usuário 'PRETA' (Mestre) detectado. Concedendo acesso a todas as {len(RANK_HIERARCHY)} faixas."
            )
            return RANK_HIERARCHY

        # Verifica se a faixa do usuário é válida.
        if user_rank not in RANK_HIERARCHY:
            logger.warning(
                f"A faixa '{user_rank}' do usuário não foi encontrada na hierarquia. Acesso negado."
            )
            return []

        try:
            # Lógica existente para alunos
            current_rank_index = RANK_HIERARCHY.index(user_rank)
            highest_accessible_index = min(
                current_rank_index + 1, len(RANK_HIERARCHY) - 1
            )
            accessible_ranks = RANK_HIERARCHY[: highest_accessible_index + 1]

            logger.info(
                f"Usuário com faixa '{user_rank}' tem acesso a: {accessible_ranks}"
            )
            return accessible_ranks
        except Exception as e:
            logger.error(
                f"Erro ao determinar faixas acessíveis para '{user_rank}': {e}"
            )
            return []
