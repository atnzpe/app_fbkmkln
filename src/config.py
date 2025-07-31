# src/config.py

import logging

logger = logging.getLogger(__name__)

# LISTA ORDENADA DE GRADUAÇÕES (HIERARQUIA DE FAIXAS)
# Esta lista define a ordem de progressão, da faixa mais baixa para a mais alta.
# É a "fonte da verdade" para a lógica de liberação de conteúdo.
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

logger.debug(
    f"Hierarquia de faixas configurada com {len(RANK_HIERARCHY)} níveis.")
