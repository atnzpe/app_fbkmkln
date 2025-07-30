# src/utils.py

import logging
import os

def setup_logging():
    """
    Configura o sistema de logging para a aplicação, definindo o formato,
    o nível de saída e os destinos (console e arquivo).
    """
    log_dir = "logs"
    log_file = os.path.join(log_dir, "app.log")

    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file, mode='w'),
            logging.StreamHandler()
        ]
    )
    logging.info("Sistema de logging configurado para console (DEBUG) e arquivo.")

def get_logger(name: str):
    """Retorna uma instância de logger com o nome especificado."""
    return logging.getLogger(name)