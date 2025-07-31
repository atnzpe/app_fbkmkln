# tests/test_auth.py

import pytest
from unittest.mock import MagicMock
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.auth import AuthService
from src.config import RANK_HIERARCHY


@pytest.fixture
def auth_service():
    """Cria uma instância de AuthService para os testes."""
    return AuthService(sheet_url="fake_url")


def test_get_accessible_ranks_for_branca(auth_service):
    """Verifica se um Faixa Branca tem acesso a Branca e Amarela."""
    print("\nExecutando test_get_accessible_ranks_for_branca...")
    user_data = {"GRADUACAO_ATUAL": "Branca"}
    expected_ranks = ["Branca", "Amarela"]
    result = auth_service.get_accessible_ranks(user_data)
    assert result == expected_ranks
    print(f"✓ Resultado para Faixa Branca: {result} (Correto)")


def test_get_accessible_ranks_for_laranja(auth_service):
    """Verifica se um Faixa Laranja tem acesso a Branca, Amarela, Laranja e Verde."""
    print("\nExecutando test_get_accessible_ranks_for_laranja...")
    user_data = {"GRADUACAO_ATUAL": "Laranja"}
    expected_ranks = ["Branca", "Amarela", "Laranja", "Verde"]
    result = auth_service.get_accessible_ranks(user_data)
    assert result == expected_ranks
    print(f"✓ Resultado para Faixa Laranja: {result} (Correto)")


def test_get_accessible_ranks_for_preta_e_branca_rank(auth_service):
    """Verifica se um aluno na graduação 'Preta e Branca' tem acesso a todas, incluindo a próxima (PRETA)."""
    print("\nExecutando test_get_accessible_ranks_for_preta_e_branca_rank...")
    user_data = {"GRADUACAO_ATUAL": "Preta e Branca"}
    # Sendo a penúltima, deve ter acesso a todas as faixas.
    expected_ranks = RANK_HIERARCHY
    result = auth_service.get_accessible_ranks(user_data)
    assert result == expected_ranks
    print(
        f"✓ Resultado para a graduação 'Preta e Branca': Acesso a todas as {len(result)} faixas (Correto)"
    )


def test_get_accessible_ranks_for_invalid_rank(auth_service):
    """Verifica se uma faixa inválida retorna uma lista vazia, por segurança."""
    print("\nExecutando test_get_accessible_ranks_for_invalid_rank...")
    user_data = {"GRADUACAO_ATUAL": "Faixa Inexistente"}
    expected_ranks = []
    result = auth_service.get_accessible_ranks(user_data)
    assert result == expected_ranks
    print(f"✓ Resultado para Faixa Inválida: {result} (Correto)")


# TESTE ATUALIZADO
def test_get_accessible_ranks_for_preta_rank(auth_service):
    """
    Cenário de Teste 5: Usuário Mestre (Faixa PRETA)
    Verifica se um usuário com a graduação "PRETA" tem acesso a todas as faixas.
    """
    print("\nExecutando test_get_accessible_ranks_for_preta_rank...")
    user_data = {"GRADUACAO_ATUAL": "PRETA"}
    # O resultado esperado é a lista completa de todas as graduações.
    expected_ranks = RANK_HIERARCHY

    result = auth_service.get_accessible_ranks(user_data)

    assert result == expected_ranks
    print(
        f"✓ Resultado para Graduação PRETA (Mestre): Acesso a todas as {len(result)} faixas (Correto)"
    )
