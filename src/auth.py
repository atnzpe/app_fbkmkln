# src/auth.py

import pandas as pd
import logging

logger = logging.getLogger(__name__)

class AuthService:
    """
    Serviço de autenticação e autorização que lê dados de uma planilha.
    """
    def __init__(self, sheet_url: str):
        """
        Construtor do serviço.

        Args:
            sheet_url (str): A URL pública do Google Sheet no formato CSV.
        """
        self.sheet_url = sheet_url
        self.user_data = None
        self.load_users()

    def load_users(self):
        """
        Carrega os dados dos usuários da planilha CSV do Google Sheets.
        """
        try:
            logger.info(f"Recarregando dados dos usuários de: {self.sheet_url}")
            # Garante que a coluna CPF seja sempre lida como texto (string)
            self.user_data = pd.read_csv(self.sheet_url, dtype={'CPF': str})
            logger.info(f"{len(self.user_data)} usuários carregados com sucesso.")
        except Exception as e:
            logger.error(f"Falha ao carregar ou processar a planilha de usuários: {e}", exc_info=True)
            self.user_data = pd.DataFrame()

    def login(self, cpf: str, senha: str) -> dict | None:
        """
        Valida as credenciais de um usuário com base nos dados da planilha.
        """
        if self.user_data is None or self.user_data.empty:
            logger.error("Tentativa de login sem dados de usuários carregados.")
            return None
        
        cpf_cleaned = cpf.replace('.', '').replace('-', '')
        user_row = self.user_data[self.user_data['CPF'] == cpf_cleaned]

        if not user_row.empty:
            user = user_row.iloc[0]
            if str(user['Senha']) == senha and user['STATUS'] == 'Ativo':
                logger.info(f"Login bem-sucedido para o usuário: {user['NOME']}.")
                return user.to_dict()
        
        logger.warning(f"Tentativa de login falhou para o CPF: {cpf_cleaned}.")
        return None

    def get_accessible_ranks(self, user_data: dict) -> list[str]:
        """
        Determina quais graduações um usuário pode acessar com base nos dados da planilha.

        Args:
            user_data (dict): O dicionário contendo os dados do usuário logado.

        Returns:
            list[str]: Uma lista contendo as faixas que o usuário pode acessar.
        """
        # Pega a graduação atual do dicionário do usuário.
        graduacao_atual = user_data.get("GRADUACAO_ATUAL")
        # Pega a próxima graduação do dicionário do usuário.
        proxima_graduacao = user_data.get("PROXIMA_GRADUACAO")
        
        accessible_ranks = []
        
        # Adiciona a graduação atual à lista, se ela existir.
        if graduacao_atual and pd.notna(graduacao_atual):
            accessible_ranks.append(graduacao_atual)
            
        # Adiciona a próxima graduação à lista, se ela existir.
        if proxima_graduacao and pd.notna(proxima_graduacao):
            accessible_ranks.append(proxima_graduacao)
            
        logger.info(f"Usuário {user_data.get('LOGIN')} tem acesso às faixas: {accessible_ranks}")
        return accessible_ranks