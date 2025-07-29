# src/auth.py

import pandas as pd
import logging

# Simplesmente pega o logger raiz configurado no main.py
logger = logging.getLogger(__name__)


class AuthService:
    """
    Serviço de autenticação responsável por carregar e validar as credenciais dos usuários.
    """

    def __init__(self, sheet_url: str):
        """
        Construtor do serviço de autenticação.

        Args:
            sheet_url (str): A URL pública do Google Sheet no formato CSV.
        """
        self.sheet_url = sheet_url
        self.user_data = None
        self.load_users()

    def load_users(self):
        """
        Carrega os dados dos usuários da planilha CSV do Google Sheets para um DataFrame pandas.
        """
        try:
            logger.info(f"Carregando dados dos usuários de: {self.sheet_url}")
            # O pandas lê o CSV diretamente da URL.
            self.user_data = pd.read_csv(self.sheet_url)
            # Converte a coluna CPF para string para evitar problemas de formatação.
            self.user_data["CPF"] = self.user_data["CPF"].astype(str)
            logger.info(f"{len(self.user_data)} usuários carregados com sucesso.")
        except Exception as e:
            logger.error(
                f"Falha ao carregar ou processar a planilha de usuários: {e}",
                exc_info=True,
            )
            # Se falhar, cria um DataFrame vazio para não quebrar o app.
            self.user_data = pd.DataFrame()

    def login(self, cpf: str, senha: str) -> dict | None:
        """
        Valida as credenciais de um usuário.

        Args:
            cpf (str): O CPF fornecido pelo usuário.
            senha (str): A senha fornecida pelo usuário.

        Returns:
            dict | None: Um dicionário com os dados do usuário se o login for bem-sucedido,
                         caso contrário, retorna None.
        """
        if self.user_data is None or self.user_data.empty:
            logger.error("Tentativa de login sem dados de usuários carregados.")
            return None

        # Procura por um usuário com o CPF fornecido.
        user_row = self.user_data[self.user_data["CPF"] == cpf]

        # Se encontrou exatamente um usuário com aquele CPF...
        if not user_row.empty:
            user = user_row.iloc[0]
            # ...e a senha confere e o status é 'Ativo'...
            if str(user["Senha"]) == senha and user["STATUS"] == "Ativo":
                logger.info(f"Login bem-sucedido para o usuário: {user['NOME']}.")
                # Retorna os dados do usuário como um dicionário.
                return user.to_dict()

        logger.warning(f"Tentativa de login falhou para o CPF: {cpf}.")
        return None
