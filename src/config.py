# src/config.py

# MÓDULO DE CONFIGURAÇÃO DA APLICAÇÃO
# Este arquivo centraliza as configurações e regras de negócio principais.

# logging é importado para registrar informações sobre a configuração.
import logging

# Obtém uma instância do logger.
logger = logging.getLogger(__name__)

# LISTA ORDENADA DE GRADUAÇÕES (HIERARQUIA DE FAIXAS)
# Esta lista define a ordem de progressão, da faixa mais baixa para a mais alta.
# É a "fonte da verdade" para a lógica de liberação de conteúdo.
# Se a ordem ou os nomes das faixas mudarem no futuro, este é o único local
# que precisará ser atualizado.
RANK_HIERARCHY = [
    "Branca",
    "Amarela",
    "Laranja",
    "Verde",
    "Azul",
    "Verde Escuro",   # Instrutor Nível 1
    "Azul Escuro",    # Instrutor Nível 2
    "Marrom",         # Instrutor Nível 3
    "Preta e Branca"  # Professor
]

# Log para confirmar que a configuração foi carregada.
logger.debug(f"Hierarquia de faixas configurada com {len(RANK_HIERARCHY)} níveis.")