
# tests/test_auth.py

import pytest
from unittest.mock import MagicMock
import os
import sys

# Adiciona o diretório raiz ao path para permitir a importação dos módulos da aplicação.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.auth import AuthService

# Simula um AuthService sem precisar de uma URL real para os testes.
@pytest.fixture
def auth_service():
    """Cria uma instância de AuthService para os testes."""
    return AuthService(sheet_url="fake_url")

def test_get_accessible_ranks_for_branca(auth_service):
    """Verifica se um Faixa Branca tem acesso a Branca e Amarela."""
    print("\nExecutando test_get_accessible_ranks_for_branca...")
    user_data = {"GRADUACAO_ATUAL": "Branca"}
    expected_ranks = ["Branca", "Amarela"]
    
    # Executa a função que queremos testar.
    result = auth_service.get_accessible_ranks(user_data)
    
    # Verifica se o resultado é o esperado.
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

def test_get_accessible_ranks_for_top_rank(auth_service):
    """Verifica se um aluno na graduação máxima tem acesso a todas as faixas."""
    print("\nExecutando test_get_accessible_ranks_for_top_rank...")
    user_data = {"GRADUACAO_ATUAL": "Preta e Branca"}
    # A lista esperada é toda a hierarquia de faixas.
    from src.config import RANK_HIERARCHY
    expected_ranks = RANK_HIERARCHY
    
    result = auth_service.get_accessible_ranks(user_data)
    
    assert result == expected_ranks
    print(f"✓ Resultado para a graduação máxima: Acesso a todas as {len(result)} faixas (Correto)")

def test_get_accessible_ranks_for_invalid_rank(auth_service):
    """Verifica se uma faixa inválida retorna uma lista vazia, por segurança."""
    print("\nExecutando test_get_accessible_ranks_for_invalid_rank...")
    user_data = {"GRADUACAO_ATUAL": "Faixa Inexistente"}
    expected_ranks = []
    
    result = auth_service.get_accessible_ranks(user_data)
    
    assert result == expected_ranks
    print(f"✓ Resultado para Faixa Inválida: {result} (Correto)")