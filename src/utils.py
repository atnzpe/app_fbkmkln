# src/utils.py

import logging
import flet as ft  # Importar flet é necessário para a classe FeedbackManager
import os  # Importar para operações de sistema de arquivos, como criar diretórios


# Configuração básica do logger
def setup_logging():
    """
    Configura o sistema de logging para a aplicação, definindo o formato,
    o nível de saída e os destinos (console e arquivo).

    Esta função inicializa o logger raiz para garantir que todas as mensagens
    de log da aplicação sejam capturadas e direcionadas corretamente
    para o console e para um arquivo de log.
    """
    # Cria o diretório de logs se ele não existir
    log_directory = "logs"  # src/utils.py


import logging
import flet as ft  # Importar flet é necessário para a classe FeedbackManager
import os  # Importar para criar diretórios de log
import numpy as np  # Necessário para cálculos numéricos (calculate_angle)
import math  # Necessário para operações matemáticas (calculate_angle)


# Configuração básica do logger
def setup_logging():
    """
    Configura o sistema de logging para a aplicação, definindo o formato
    e o nível de saída para INFO. Esta função deve ser chamada uma única vez
    na inicialização da aplicação para configurar os handlers globais.
    """
    # Obtém o logger raiz
    root_logger = logging.getLogger()
    # Define o nível mínimo de logging para o logger raiz.
    # Mensagens com nível INFO, WARNING, ERROR, CRITICAL serão processadas.
    root_logger.setLevel(logging.INFO)

    # Define o formato das mensagens de log
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Verifica se os handlers já foram configurados para evitar duplicação
    # Isso é importante para evitar que o mesmo log apareça várias vezes
    # no console ou no arquivo se setup_logging for chamado múltiplas vezes.
    if not root_logger.handlers:
        # Handler para console (StreamHandler)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
        root_logger.info("Console Handler configurado para logging.")

        # Handler para arquivo (FileHandler)
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            root_logger.info(
                f"Diretório de logs '{log_dir}' criado."
            )  # Log da criação do diretório
        file_handler = logging.FileHandler(os.path.join(log_dir, "app.log"))
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
        root_logger.info(
            f"File Handler configurado para salvar logs em: {os.path.join(log_dir, 'app.log')}"
        )

    root_logger.info("Configuração de logging inicializada com sucesso.")


def get_logger(name: str):
    """
    Retorna uma instância de logger com o nome especificado.
    Cada módulo deve obter seu próprio logger usando esta função.

    Args:
        name (str): O nome do logger (geralmente __name__ do módulo).

    Returns:
        logging.Logger: A instância do logger.
    """
    return logging.getLogger(name)


class FeedbackManager:
    """
    Gerencia a exibição de feedback e mensagens de status na interface do usuário (UI).
    Usa um controle `ft.Text` para exibir mensagens, atualizando-o conforme necessário.
    """

    def __init__(self, feedback_text_control: ft.Text = None):
        """
        Inicializa o FeedbackManager.

        Args:
            feedback_text_control (ft.Text): O controle ft.Text onde as mensagens serão exibidas.
        """
        self.feedback_text_control = feedback_text_control
        # Obtém um logger nomeado para FeedbackManager
        self.logger = get_logger(__name__)
        self.logger.info("FeedbackManager inicializado.")

    def update_feedback(
        self, message: str, is_error: bool = False, is_multiline: bool = False
    ):
        """
        Atualiza o texto de feedback na UI e registra a mensagem.

        Args:
            message (str): A mensagem a ser exibida.
            is_error (bool): Se True, a mensagem será exibida em vermelho.
            is_multiline (bool): Se True, permite que o texto se estenda por várias linhas.
        """
        if self.feedback_text_control:
            self.feedback_text_control.value = message
            self.feedback_text_control.color = (
                ft.Colors.RED_500 if is_error else ft.Colors.BLACK
            )
            self.feedback_text_control.max_lines = 10 if is_multiline else 1
            self.feedback_text_control.update()
            if is_error:
                self.logger.error(f"Feedback UI (ERRO): {message}")
            else:
                self.logger.info(f"Feedback UI: {message}")
        else:
            if is_error:
                self.logger.error(f"FeedbackManager não configurado para UI: {message}")
            else:
                self.logger.info(f"FeedbackManager não configurado para UI: {message}")


def calculate_angle(p1: dict, p2: dict, p3: dict) -> float:
    """
    Calcula o ângulo (em graus) entre três pontos 3D (landmarks),
    com p2 sendo o vértice do ângulo.

    Args:
        p1 (dict): Dicionário com as coordenadas 'x', 'y', 'z' e 'visibility' do primeiro ponto.
        p2 (dict): Dicionário com as coordenadas 'x', 'y', 'z' e 'visibility' do ponto do vértice.
        p3 (dict): Dicionário com as coordenadas 'x', 'y', 'z' e 'visibility' do terceiro ponto.

    Returns:
        float: O ângulo em graus. Retorna 0.0 se algum ponto não for visível
               ou se os vetores forem nulos/coincidentes.

    Raises:
        ValueError: Se as coordenadas 'x', 'y' ou 'z' não estiverem presentes nos dicionários.
    """
    # Verifica a visibilidade dos pontos
    # Um limiar de visibilidade de 0.5 é comum para considerar o landmark detectado.
    if (
        p1.get("visibility", 0) < 0.5
        or p2.get("visibility", 0) < 0.5
        or p3.get("visibility", 0) < 0.5
    ):
        # Se algum ponto não for suficientemente visível, retorna 0.0 e loga um aviso.
        get_logger(__name__).warning(
            "Ponto(s) invisível(is) ou com baixa visibilidade detectado(s) ao calcular ângulo. Retornando 0.0."
        )
        return 0.0

    # Extrai as coordenadas e garante que são floats para cálculos robustos
    try:
        p1_array = np.array([float(p1["x"]), float(p1["y"]), float(p1["z"])])
        p2_array = np.array([float(p2["x"]), float(p2["y"]), float(p2["z"])])
        p3_array = np.array([float(p3["x"]), float(p3["y"]), float(p3["z"])])
    except KeyError as e:
        # Captura KeyError se alguma coordenada estiver faltando no dicionário
        raise ValueError(f"Coordenada ausente no dicionário do landmark: {e}")
    except TypeError as e:
        # Captura TypeError se o valor da coordenada não puder ser convertido para float
        raise ValueError(f"Tipo de dado inválido para coordenada do landmark: {e}")

    # Cria vetores dos lados do ângulo, com p2 como origem.
    # v1 aponta de p2 para p1, e v2 aponta de p2 para p3.
    v1 = p1_array - p2_array
    v2 = p3_array - p2_array

    # Calcula o produto escalar dos dois vetores.
    # O produto escalar está relacionado ao cosseno do ângulo entre os vetores.
    dot_product = np.dot(v1, v2)

    # Calcula a magnitude (comprimento) de cada vetor.
    # A magnitude é necessária para normalizar o produto escalar.
    magnitude_v1 = np.linalg.norm(v1)
    magnitude_v2 = np.linalg.norm(v2)

    # Verifica se alguma magnitude é zero para evitar divisão por zero.
    # Isso pode ocorrer se os pontos forem coincidentes, o que resultaria em vetores nulos.
    if magnitude_v1 == 0 or magnitude_v2 == 0:
        # Se os vetores são nulos, os pontos são coincidentes ou não válidos para cálculo de ângulo.
        # Loga um aviso e retorna 0.0 para evitar erros.
        get_logger(__name__).warning(
            "Ponto(s) coincidente(s) ou vetor(es) nulo(s) detectado(s) ao calcular ângulo. Retornando 0.0."
        )
        return 0.0

    # Calcula o cosseno do ângulo.
    # Adiciona np.clip para garantir que o valor esteja no intervalo [-1, 1]
    # devido a possíveis imprecisões de ponto flutuante, que podem causar erros no arccos.
    cosine_angle = np.clip(dot_product / (magnitude_v1 * magnitude_v2), -1.0, 1.0)

    # Calcula o ângulo em radianos e depois converte para graus.
    angle_rad = math.acos(cosine_angle)
    angle_deg = np.degrees(angle_rad)

    # Retorna o ângulo como float
    return float(angle_deg)
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
        logging.info(
            f"Diretório de logs '{log_directory}' criado."
        )  # Log da criação do diretório

    # Define o nome do arquivo de log
    log_file_path = os.path.join(log_directory, "app.log")

    # Obtém o logger raiz
    root_logger = logging.getLogger()
    # Define o nível mínimo de logging para o logger raiz.
    # Mensagens com nível INFO, WARNING, ERROR, CRITICAL serão processadas.
    root_logger.setLevel(logging.INFO)

    # Define o formato das mensagens de log
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Configura o Console Handler (para exibir logs no console)
    # Garante que o console handler não seja adicionado múltiplas vezes
    if not any(
        isinstance(handler, logging.StreamHandler) for handler in root_logger.handlers
    ):
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
        logging.info("Console Handler configurado para logging.")

    # Configura o File Handler (para salvar logs em arquivo)
    # O modo 'a' (append) garante que o log seja adicionado ao final do arquivo existente.
    # Garante que o file handler não seja adicionado múltiplas vezes
    if not any(
        isinstance(handler, logging.FileHandler) for handler in root_logger.handlers
    ):
        file_handler = logging.FileHandler(log_file_path, mode="a", encoding="utf-8")
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
        logging.info(f"File Handler configurado para salvar logs em: {log_file_path}")

    logging.info("Configuração de logging inicializada com sucesso.")


def get_logger(name: str):
    """
    Retorna uma instância de logger com o nome especificado.

    Esta função permite obter um logger específico para um módulo, o que
    ajuda a rastrear de onde as mensagens de log estão vindo.

    Args:
        name (str): O nome do logger (geralmente __name__ do módulo que está chamando).

    Returns:
        logging.Logger: A instância do logger.
    """
    # Retorna um logger com o nome do módulo que o chamou.
    # Isso permite que as mensagens de log contenham o nome do módulo,
    # facilitando o debug e a rastreabilidade.
    return logging.getLogger(name)


class FeedbackManager:
    """
    Gerencia a exibição de feedback e mensagens de status na interface do usuário (UI).
    Usa um controle `ft.Text` para exibir mensagens, atualizando-o conforme necessário.

    Esta classe é responsável por comunicar o status da aplicação ao usuário,
    seja uma mensagem de progresso, sucesso ou erro.
    """

    def __init__(self, feedback_text_control: ft.Text = None):
        """
        Inicializa o FeedbackManager.

        Associa o FeedbackManager a um controle `ft.Text` específico na UI,
        onde as mensagens de feedback serão exibidas. Se nenhum controle for fornecido,
        ele operará de forma "headless", apenas logando as mensagens.

        Args:
            feedback_text_control (ft.Text, opcional): O controle ft.Text
                                                      onde as mensagens serão exibidas.
                                                      Padrão para None.
        """
        # A instância do logger para a classe FeedbackManager.
        self.logger = get_logger(__name__)
        self.feedback_text_control = feedback_text_control  # O controle de texto na UI
        self.logger.info("FeedbackManager inicializado.")

    def update_feedback(self, message: str, is_error: bool = False):
        """
        Atualiza a mensagem de feedback na UI e registra a mensagem no log.

        Esta função define o texto e a cor do controle de feedback na UI
        com base na mensagem e se é uma mensagem de erro, e também registra
        a mensagem usando o logger apropriado.

        Args:
            message (str): A mensagem de feedback a ser exibida.
            is_error (bool): Se True, a mensagem é tratada como um erro
                             (exibida em vermelho na UI e logada como ERROR).
                             Caso contrário, é uma mensagem informativa (exibida
                             em preto/padrão e logada como INFO).
        """
        # Verifica se um controle de texto foi fornecido para atualização da UI
        if self.feedback_text_control:
            self.feedback_text_control.value = message  # Define o texto da mensagem
            # Define a cor do texto com base se é uma mensagem de erro
            self.feedback_text_control.color = (
                ft.Colors.RED if is_error else ft.Colors.BLACK
            )
            # Atualiza a UI para refletir as mudanças
            # É importante chamar update_async() se estiver em um contexto assíncrono
            # ou page.update() se o controle estiver diretamente na página e a função for síncrona.
            # Aqui, assumimos que a atualização da página ocorrerá no contexto de Flet.
            # No Flet, a atualização dos controles é feita chamando page.update() ou control.update().
            # Para garantir a responsividade, é bom atualizar o controle diretamente se possível.
            # No entanto, em um contexto assíncrono, chamar page.update() ao final de uma operação é mais comum.
            # Para este FeedbackManager, é mais seguro que o chamador externo chame page.update().
            # Aqui, apenas configuramos os valores.
            pass  # A atualização real da UI ocorrerá via page.update() no main_flet.py

        # Loga a mensagem com o nível apropriado
        if is_error:
            self.logger.error(f"Atualizando feedback: {message} (Erro: {is_error})")
        else:
            self.logger.info(f"Atualizando feedback: {message} (Erro: {is_error})")


    def calculate_angle(p1: dict, p2: dict, p3: dict) -> float:
        """
        Calcula o ângulo (em graus) formado por três pontos 3D.

        Esta função é essencial para a análise de movimento, permitindo quantificar
        ângulos de articulações a partir dos landmarks detectados pelo MediaPipe.

        Args:
            p1 (dict): Dicionário com as coordenadas (x, y, z) do primeiro ponto.
            p2 (dict): Dicionário com as coordenadas (x, y, z) do ponto central (vértice do ângulo).
            p3 (dict): Dicionário com as coordenadas (x, y, z) do terceiro ponto.

        Returns:
            float: O ângulo em graus. Retorna 0.0 se houver pontos coincidentes
                para evitar divisão por zero.
        """
        # Converte os dicionários de pontos para arrays numpy para facilitar cálculos vetoriais.
        # É crucial que os pontos p1, p2, p3 sejam dicionários com chaves 'x', 'y', 'z'.
        p1_array = np.array([p1["x"], p1["y"], p1["z"]])
        p2_array = np.array([p2["x"], p2["y"], p2["z"]])
        p3_array = np.array([p3["x"], p3["y"], p3["z"]])

        # Cria vetores dos lados do ângulo, com p2 como origem.
        # v1 aponta de p2 para p1, e v2 aponta de p2 para p3.
        v1 = p1_array - p2_array
        v2 = p3_array - p2_array

        # Calcula o produto escalar dos dois vetores.
        # O produto escalar está relacionado ao cosseno do ângulo entre os vetores.
        dot_product = np.dot(v1, v2)

        # Calcula a magnitude (comprimento) de cada vetor.
        # A magnitude é necessária para normalizar o produto escalar.
        magnitude_v1 = np.linalg.norm(v1)
        magnitude_v2 = np.linalg.norm(v2)

        # Verifica se alguma magnitude é zero para evitar divisão por zero.
        # Isso pode ocorrer se os pontos forem coincidentes, o que resultaria em vetores nulos.
        if magnitude_v1 == 0 or magnitude_v2 == 0:
            # Se os vetores são nulos, os pontos são coincidentes ou não válidos para cálculo de ângulo.
            # Loga um aviso e retorna 0.0 para evitar erros.
            logging.warning(
                "Ponto(s) coincidente(s) ou vetor(es) nulo(s) detectado(s) ao calcular ângulo. Retornando 0.0."
            )
            return 0.0

        # Calcula o cosseno do ângulo.
        # Adiciona np.clip para garantir que o valor esteja no intervalo [-1, 1]
        # devido a possíveis imprecisões de ponto flutuante, que podem causar erros no arccos.
        cosine_angle = np.clip(dot_product / (magnitude_v1 * magnitude_v2), -1.0, 1.0)

        # Calcula o ângulo em radianos e depois converte para graus.
        angle_radians = np.arccos(cosine_angle)
        angle_degrees = np.degrees(angle_radians)

        # Retorna o ângulo arredondado para um valor prático.
        return round(angle_degrees, 2)
