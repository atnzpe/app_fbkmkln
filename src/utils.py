# src/utils.py

import logging
import os


def setup_logging():
    """
    Configura o sistema de logging para a aplicação, definindo o formato,
    o nível de saída e os destinos (console e arquivo).
    """
    # Define o diretório e o arquivo de log.
    log_dir = "logs"
    log_file = os.path.join(log_dir, "app.log")

    # Cria o diretório de logs se ele não existir.
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Configura o logger raiz para registrar mensagens de nível INFO e acima.
    # O arquivo de log é recriado a cada execução (mode='w') para manter apenas os logs da sessão atual.
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file, mode="w"),  # Handler para salvar em arquivo.
            logging.StreamHandler(),  # Handler para exibir no console.
        ],
    )
    logging.info("Sistema de logging configurado para console e arquivo.")


def get_logger(name: str):
    """Retorna uma instância de logger com o nome especificado."""
    return logging.getLogger(name)
