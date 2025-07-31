# src/config.py

# MÓDULO DE CONFIGURAÇÃO DA APLICAÇÃO
# Este arquivo centraliza as configurações e regras de negócio principais.

# logging é importado para registrar informações sobre a configuração.
import logging

# Obtém uma instância do logger.
logger = logging.getLogger(__name__)

# LISTA ORDENADA DE GRADUAÇÕES (HIERARQUIA DE FAIXAS)
# Esta lista define a ordem de progressão, da faixa mais baixa para a mais alta.
# A graduação "PRETA" foi definida como o nível de acesso total (Mestre).
RANK_HIERARCHY = [
    "Branca",
    "Amarela",
    "Laranja",
    "Verde",
    "Azul",
    "Verde Escuro",   # Instrutor Nível 1
    "Azul Escuro",    # Instrutor Nível 2
    "Marrom",         # Instrutor Nível 3
    "Preta e Branca", # Professor
    "PRETA"           # Novo nível de acesso total (Mestre)
]

# Log para confirmar que a configuração foi carregada.
logger.debug(f"Hierarquia de faixas configurada com {len(RANK_HIERARCHY)} níveis.")