# main.py

import flet as ft
import logging
import sys
import os
import json

# Importações necessárias para o player de vídeo corrigido
import threading
import time

try:
    from src.auth import AuthService
    from src.utils import setup_logging
    from src.config import RANK_HIERARCHY
    from src.playlist_service import PlaylistService
except ImportError:
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    from src.auth import AuthService
    from src.utils import setup_logging
    from src.config import RANK_HIERARCHY
    from src.playlist_service import PlaylistService

SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ3u0Mnny-vm3aZkbYoXQo85IwbfkI6FtD7T_uNhnSLMTzZZarFgRJJTmONncFo8U7cUGlsYTj17aMM/pub?gid=0&single=true&output=csv"

setup_logging()
logger = logging.getLogger(__name__)


class AppFBKMKLN:
    def __init__(self, page: ft.Page):
        logger.debug("Inicializando a classe AppFBKMKLN.")
        self.page = page
        self.auth_service = AuthService(sheet_url=SHEET_URL)
        self.program_path = "assets/programa_tecnico"
        self.videos_path = "assets/videos_tecnicas"
        self.playlist_service = PlaylistService(videos_base_path=self.videos_path)
        self.is_training_active = False  # Flag para controlar a thread do player

        os.makedirs(self.program_path, exist_ok=True)
        os.makedirs(self.videos_path, exist_ok=True)

        self.setup_page_and_routes()
        self.page.go("/")

    def setup_page_and_routes(self):
        logger.debug("Configurando propriedades da página Flet e rotas.")
        self.page.title = "FBKMKLN - Leão do Norte"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.bgcolor = ft.Colors.BLACK
        self.page.on_route_change = self.on_route_change
        self.page.on_view_pop = self.on_view_pop

    def on_route_change(self, route):
        logger.info(f"Navegando para a rota: {self.page.route}")
        self.page.views.clear()

        user_data = self.page.client_storage.get("user_data")

        if self.page.route == "/":
            self.page.views.append(self.create_login_view())
        elif self.page.route == "/dashboard" and user_data:
            self.page.views.append(self.create_dashboard_view(user=user_data))
        elif self.page.route == "/program" and user_data:
            self.page.views.append(self.create_program_view(user=user_data))
        elif self.page.route == "/videos" and user_data:
            self.page.views.append(self.create_videos_view(user=user_data))
        elif self.page.route.startswith("/training_player") and user_data:
            playlist_json = self.page.client_storage.get("current_playlist")
            if playlist_json:
                playlist = json.loads(playlist_json)
                self.page.views.append(
                    self.create_training_player_view(playlist=playlist, user=user_data)
                )
            else:
                self.page.go("/videos")
        elif self.page.route == "/training_complete" and user_data:
            self.page.views.append(self.create_training_complete_view(user=user_data))
        elif self.page.route == "/training_location" and user_data:
            self.page.views.append(self.create_training_location_view())
        else:
            self.page.views.append(self.create_login_view())

        self.page.update()

    def on_view_pop(self, view):
        logger.debug("Evento on_view_pop acionado.")
        self.page.views.pop()
        top_view = self.page.views[-1]
        self.page.go(top_view.route)

    def login(self, e):
        cpf = self.cpf_field.value
        senha = self.password_field.value
        logger.info(f"Tentativa de login para o CPF: {cpf}")
        user_data = self.auth_service.login(cpf, senha)

        if user_data:
            self.page.client_storage.set("user_data", user_data)
            self.page.go("/dashboard")
        else:
            self.login_status.value = "CPF, senha inválidos ou usuário inativo."
            self.page.update()

    def logout(self, e):
        logger.info(
            f"Usuário '{self.page.client_storage.get('user_data').get('LOGIN')}' fazendo logout."
        )
        self.page.client_storage.remove("user_data")
        self.page.go("/")

    def create_login_view(self) -> ft.View:
        """
        Cria e retorna a View (página) de Login.
        Esta função é responsável por construir todos os elementos visuais da tela de login.
        """
        # Log para registrar que a View está sendo criada.
        logger.debug("Criando a View de Login.")
        # Garante que a lista de usuários da planilha seja carregada ou recarregada.
        self.auth_service.load_users()

        # Cria o controle de imagem para o logo da federação.
        logo = ft.Image(
            src="/icon.jpg",  # Caminho para o arquivo na pasta 'assets'.
            width=150,
            height=150,
            fit=ft.ImageFit.CONTAIN,
        )

        # Define um estilo padrão para os campos de texto para garantir consistência e legibilidade.
        text_field_style = {
            "label_style": ft.TextStyle(color=ft.Colors.WHITE),
            "border_color": ft.Colors.with_opacity(0.5, ft.Colors.WHITE),
            "width": 300,
        }

        # Cria os campos de entrada para CPF e Senha, aplicando o estilo.
        self.cpf_field = ft.TextField(label="CPF", autofocus=True, **text_field_style)
        self.password_field = ft.TextField(
            label="Senha", password=True, can_reveal_password=True, **text_field_style
        )
        # Cria o texto que exibirá mensagens de erro de login.
        self.login_status = ft.Text(value="", color=ft.Colors.RED_ACCENT)
        # Cria o botão principal de login.
        login_button = ft.ElevatedButton(text="Entrar", width=300, on_click=self.login)

        # Cria o botão para encerrar a aplicação.
        exit_button = ft.OutlinedButton(
            text="Encerrar Aplicativo",
            width=300,
            on_click=lambda _: self.page.window_destroy(),
        )

        # Retorna o objeto View, que representa a tela completa.
        return ft.View(
            "/",  # A rota (URL) desta View.
            [
                # Organiza todos os controles verticalmente em uma Coluna.
                ft.Column(
                    [
                        logo,
                        ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                        self.cpf_field,
                        self.password_field,
                        self.login_status,
                        login_button,
                        exit_button,
                    ],
                    # Configurações para garantir que a coluna se expanda e centralize seu conteúdo.
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=15,
                    expand=True,
                )
            ],
            # Configurações de layout da View.
            padding=20,
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def create_dashboard_view(self, user: dict) -> ft.View:
        """
        Cria e retorna a View (página) do Dashboard principal após o login.

        Args:
            user (dict): Um dicionário com os dados do usuário logado.
        """
        # Extrai o nome de login do usuário para a mensagem de boas-vindas.
        user_login_name = user.get("LOGIN", "Usuário")
        logger.info(f"Exibindo dashboard para o usuário: {user_login_name}")

        # Cria os elementos do cabeçalho.
        logo_header = ft.Image(
            src="/icon.jpg", width=80, height=80, border_radius=ft.border_radius.all(40)
        )
        welcome_message = ft.Text(
            f"Kidá (קִדָּה), {user_login_name}!", size=24, weight=ft.FontWeight.BOLD
        )

        # Agrupa o logo e a mensagem em uma coluna centralizada.
        header_content = ft.Column(
            [logo_header, welcome_message],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )

        # Cria o botão de logout.
        btn_logout = ft.IconButton(
            icon=ft.Icons.LOGOUT, on_click=self.logout, tooltip="Sair"
        )

        # Cria uma linha para o cabeçalho, com o logout alinhado à direita.
        header_row = ft.Row([ft.Container(expand=True), btn_logout])

        # Define um estilo padrão para os botões do dashboard para consistência visual.
        button_style = ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.WHITE24)

        # Cria cada botão de funcionalidade, atribuindo seu ícone, texto e ação.
        btn_programa = ft.ElevatedButton(
            "Programa Técnico",
            icon=ft.Icons.DESCRIPTION,
            on_click=lambda _: self.page.go("/program"),
            height=50,
            style=button_style,
        )
        btn_videos = ft.ElevatedButton(
            "Vídeos de Movimentos",
            icon=ft.Icons.VIDEO_LIBRARY,
            on_click=lambda _: self.page.go("/videos"),
            height=50,
            style=button_style,
        )
        btn_analisador = ft.ElevatedButton(
            "Analisador de Movimentos",
            icon=ft.Icons.ANALYTICS,
            on_click=lambda e: logger.debug("Botão 'Analisador de Movimentos' clicado"),
            height=50,
            style=button_style,
        )
        btn_cursos = ft.ElevatedButton(
            "Cursos",
            icon=ft.Icons.SCHOOL,
            on_click=lambda e: logger.debug("Botão 'Cursos' clicado"),
            height=50,
            style=button_style,
            disabled=True,
        )
        btn_local_treino = ft.ElevatedButton(
            "Onde Treinar",
            icon=ft.Icons.LOCATION_ON,
            on_click=lambda _: self.page.go("/training_location"),
            height=50,
            style=button_style,
        )
        btn_social = ft.ElevatedButton(
            "Mídias Sociais",
            icon=ft.Icons.GROUP,
            on_click=lambda e: logger.debug("Botão 'Mídias Sociais' clicado"),
            height=50,
            style=button_style,
        )

        # Organiza os botões em uma grade responsiva, que se adapta a diferentes tamanhos de tela.
        dashboard_buttons = ft.ResponsiveRow(
            [
                ft.Column([btn_programa], col={"xs": 12, "sm": 6, "md": 4}),
                ft.Column([btn_videos], col={"xs": 12, "sm": 6, "md": 4}),
                ft.Column([btn_analisador], col={"xs": 12, "sm": 6, "md": 4}),
                ft.Column([btn_cursos], col={"xs": 12, "sm": 6, "md": 4}),
                ft.Column([btn_local_treino], col={"xs": 12, "sm": 6, "md": 4}),
                ft.Column([btn_social], col={"xs": 12, "sm": 6, "md": 4}),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            run_spacing=10,
            spacing=10,
        )

        # Retorna a View do Dashboard, organizando todos os elementos.
        return ft.View(
            "/dashboard",
            [
                ft.Column(
                    [
                        header_row,
                        header_content,
                        ft.Divider(height=20, color=ft.Colors.WHITE24),
                        dashboard_buttons,
                    ],
                    spacing=25,
                    expand=True,
                    alignment=ft.MainAxisAlignment.START,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                )
            ],
            padding=20,
        )

    def create_program_view(self, user: dict) -> ft.View:
        """Cria e retorna a View que lista os PDFs de programa técnico acessíveis."""
        logger.info(
            f"Criando a tela de programa técnico para o usuário: {user.get('LOGIN')}"
        )

        # Pega a lista de faixas que o usuário pode acessar usando o AuthService.
        accessible_ranks = self.auth_service.get_accessible_ranks(user)

        # Cria uma lista vazia para armazenar os botões dos PDFs.
        program_buttons = []
        try:
            # Lista todos os arquivos na pasta de programas.
            all_programs = os.listdir(self.program_path)

            # Itera sobre a hierarquia oficial para manter a ordem correta das faixas.
            for rank in RANK_HIERARCHY:
                # Se a faixa estiver na lista de permissões do usuário...
                if rank in accessible_ranks:
                    pdf_file = f"{rank}.pdf"
                    # ...e se o arquivo PDF correspondente existir na pasta...
                    if pdf_file in all_programs:
                        pdf_path = os.path.join(self.program_path, pdf_file).replace(
                            "\\", "/"
                        )
                        # ...cria um botão para ele.
                        button = ft.ElevatedButton(
                            text=f"Programa - Faixa {rank}",
                            icon=ft.Icons.PICTURE_AS_PDF,
                            on_click=lambda _, p=pdf_path: self.page.launch_url(
                                f"file:///{os.path.abspath(p)}"
                            ),
                            height=50,
                        )
                        program_buttons.append(button)
                    else:
                        logger.warning(
                            f"O arquivo '{pdf_file}' para a faixa '{rank}' não foi encontrado."
                        )
        except Exception as e:
            logger.error(f"Erro ao listar os PDFs do programa técnico: {e}")
            program_buttons.append(
                ft.Text("Não foi possível carregar os programas.", color=ft.Colors.RED)
            )

        # Retorna a View da tela de programas.
        return ft.View(
            "/program",
            [
                ft.Row(
                    [
                        ft.IconButton(
                            icon=ft.Icons.ARROW_BACK,
                            on_click=lambda _: self.page.go("/dashboard"),
                            tooltip="Voltar",
                        )
                    ]
                ),
                ft.Text("Programa Técnico", size=24, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                # Adiciona os botões em uma coluna com scroll.
                ft.Column(
                    program_buttons,
                    spacing=15,
                    scroll=ft.ScrollMode.ADAPTIVE,
                    expand=True,
                    horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                ),
            ],
            padding=20,
        )

    
        """Prepara e inicia uma sessão de treino."""
        logger.info(
            f"Iniciando treino do tipo '{playlist_type}' para a faixa '{rank}'."
        )
        playlist = []
        if playlist_type == "rank":
            playlist = self.playlist_service.get_rank_playlist(rank)
        elif playlist_type == "exam":
            playlist = self.playlist_service.get_exam_playlist(rank)

        if not playlist:
            logger.warning("Nenhum vídeo encontrado para iniciar o treino.")
            return

        self.page.client_storage.set("current_playlist", json.dumps(playlist))
        self.page.go("/training_player")

    def create_videos_view(self, user: dict) -> ft.View:
        """Cria a View que mostra as opções de treino, com a nova regra de exame."""
        logger.info(f"Criando a tela de seleção de treino para: {user.get('LOGIN')}")
        accessible_ranks = self.auth_service.get_accessible_ranks(user)
        user_next_rank = user.get("PROXIMA_GRADUACAO")
        
        layout_controls = []
        try:
            for rank in RANK_HIERARCHY:
                if rank in accessible_ranks:
                    if os.path.exists(os.path.join(self.videos_path, rank, "playlist.json")):
                        layout_controls.append(ft.Text(f"Faixa {rank}", size=20, weight=ft.FontWeight.BOLD))
                        
                        train_button = ft.ElevatedButton(
                            text=f"Treinar Faixa {rank}",
                            icon=ft.Icons.PLAYLIST_PLAY,
                            on_click=lambda _, r=rank: self.start_training(playlist_type='rank', rank=r),
                            height=50
                        )
                        
                        # **NOVA REGRA:** O botão de exame só aparece se a próxima faixa
                        # da hierarquia for a PRÓXIMA GRADUAÇÃO oficial do aluno.
                        current_rank_index = RANK_HIERARCHY.index(rank)
                        if current_rank_index + 1 < len(RANK_HIERARCHY):
                            next_rank_in_hierarchy = RANK_HIERARCHY[current_rank_index + 1]
                            if next_rank_in_hierarchy == user_next_rank:
                                exam_button = ft.ElevatedButton(
                                    text=f"Simular Exame para {next_rank_in_hierarchy}",
                                    icon=ft.Icons.VIDEO_CAMERA_FRONT,
                                    on_click=lambda _, r=next_rank_in_hierarchy: self.start_training(playlist_type='exam', rank=r),
                                    height=50
                                )
                                layout_controls.append(ft.Row([train_button, exam_button], spacing=10, alignment=ft.MainAxisAlignment.CENTER))
                            else:
                                layout_controls.append(train_button)
                        else:
                            layout_controls.append(train_button)

                        layout_controls.append(ft.Divider(height=20))
        except Exception as e:
            logger.error(f"Erro ao criar a visualização de vídeos: {e}")
            layout_controls.append(ft.Text("Não foi possível carregar as opções de treino.", color=ft.colors.RED))

        return ft.View(
            "/videos",
            [
                ft.Row([ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda _: self.page.go("/dashboard"), tooltip="Voltar")]),
                ft.Text("Modos de Treino", size=24, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Column(layout_controls, spacing=15, scroll=ft.ScrollMode.ADAPTIVE, expand=True)
            ],
            padding=20
        )

    def start_training(self, playlist_type: str, rank: str):
        logger.info(f"Iniciando treino do tipo '{playlist_type}' para a faixa '{rank}'.")
        playlist = []
        if playlist_type == 'rank':
            playlist = self.playlist_service.get_rank_playlist(rank)
        elif playlist_type == 'exam':
            playlist = self.playlist_service.get_exam_playlist(rank)
            
        if not playlist:
            logger.warning("Nenhum vídeo encontrado para iniciar o treino.")
            return
        
        self.page.client_storage.set("current_playlist", json.dumps(playlist))
        self.page.go("/training_player")

    def create_training_player_view(self, playlist: list, user: dict) -> ft.View:
        """
        Cria e retorna a View do player de treino, agora corrigida.
        Esta tela é responsável por reproduzir a sequência de vídeos de uma playlist.

        Args:
            playlist (list): A lista de dicionários de vídeo a ser reproduzida.
            user (dict): Os dados do usuário logado.
        """
        # Refs são usados para manter o estado de variáveis que precisam ser acessadas
        # por diferentes funções dentro do escopo desta View.
        current_video_index = ft.Ref[int]()
        # Inicia o treino no primeiro vídeo da lista (índice 0).
        current_video_index.current = 0
        # Ativa a flag que controla o loop da nossa thread "vigia".
        self.is_training_active = True

        # Cria os controles da UI que serão atualizados dinamicamente (título e descrição).
        video_title = ft.Text(value="", size=22, weight=ft.FontWeight.BOLD)
        video_description = ft.Text(value="", size=14, color=ft.Colors.WHITE70)

        # **CORREÇÃO:** O player de vídeo é criado sem o argumento 'on_ended', que não é mais suportado.
        video_player = ft.Video(expand=True, autoplay=True)

        def update_video_display(start_watch_thread=False):
            """
            Função interna para atualizar o player de vídeo, o título e a descrição
            com base no vídeo atual da playlist.
            """
            # Verifica se o índice atual é válido para a playlist.
            if current_video_index.current < len(playlist):
                # Pega as informações do vídeo atual.
                video_info = playlist[current_video_index.current]
                # Pega o nome da pasta da faixa (ex: "Branca"), que foi adicionado pelo PlaylistService.
                rank_folder = video_info.get("rank_folder")

                if rank_folder:
                    # Constrói o caminho completo e correto para o arquivo de vídeo.
                    video_path = os.path.join(
                        self.videos_path, rank_folder, video_info["file"]
                    ).replace("\\", "/")

                    # Limpa a playlist atual do player e adiciona o novo vídeo.
                    video_player.playlist_clear()
                    # **CORREÇÃO:** A propriedade correta para assets locais é 'resource'.
                    video_player.playlist_add(ft.VideoMedia(video_path))

                    # Atualiza os textos na tela.
                    video_title.value = video_info.get("title", "Título indisponível")
                    video_description.value = video_info.get(
                        "description", "Descrição indisponível."
                    )

                    # Habilita ou desabilita os botões de navegação conforme a posição na playlist.
                    prev_button.disabled = current_video_index.current == 0
                    next_button.disabled = (
                        current_video_index.current == len(playlist) - 1
                    )

                    # Inicia a reprodução do vídeo.
                    video_player.play()
                    # Envia todas as atualizações para a interface do usuário.
                    self.page.update()

                    # Se instruído, inicia a thread "vigia" para este vídeo.
                    if start_watch_thread:
                        threading.Thread(target=watch_video_end, daemon=True).start()
                else:
                    logger.error(
                        f"Não foi possível encontrar 'rank_folder' para o vídeo: {video_info.get('file')}"
                    )

        def next_video(e=None):
            """Avança para o próximo vídeo na playlist ou finaliza o treino."""
            # Verifica se não estamos no último vídeo.
            if current_video_index.current < len(playlist) - 1:
                current_video_index.current += 1
                update_video_display(start_watch_thread=True)
            # Se for o último vídeo, encerra o treino.
            elif self.is_training_active:
                self.is_training_active = False  # Para a thread do vigia
                self.page.go("/training_complete")

        def prev_video(e):
            """Volta para o vídeo anterior na playlist."""
            if current_video_index.current > 0:
                current_video_index.current -= 1
                update_video_display(start_watch_thread=True)

        def watch_video_end():
            """
            Função "vigia" que roda em uma thread para detectar o fim do vídeo,
            já que o evento 'on_ended' não está mais disponível.
            """
            logger.debug(
                f"Vigia iniciado para o vídeo {current_video_index.current + 1}."
            )
            while self.is_training_active:
                time.sleep(1)  # Verifica a cada segundo.
                if not self.is_training_active:
                    break
                try:
                    # Pega a duração total e a posição atual do vídeo (em milissegundos).
                    duration = video_player.get_duration()
                    position = video_player.get_current_position()

                    # Se a duração e a posição forem válidas e a posição estiver perto do fim...
                    if (
                        duration and position and (duration - position) < 1000
                    ):  # 1000ms = 1 segundo
                        logger.info("Fim do vídeo detectado pelo vigia.")
                        # Chama a função 'next_video' na thread principal da UI para evitar erros.
                        self.page.run_thread(target=next_video)
                        break  # Encerra este vigia, pois o vídeo acabou.
                except:
                    # Se houver um erro (ex: a View foi destruída), apenas para o loop.
                    break
            logger.debug(
                f"Vigia finalizado para o vídeo {current_video_index.current + 1}."
            )

        # --- Lógica da Caixa de Diálogo de Confirmação ---
        def confirm_exit(e):
            """Função chamada se o usuário clicar 'Sim' no diálogo de saída."""
            self.is_training_active = False  # Para a thread do vigia
            self.page.go("/videos")  # Navega de volta para a seleção de treinos.

        def close_training_dialog(e):
            """Função chamada se o usuário clicar 'Não'."""
            confirm_dialog.open = False
            self.page.update()

        confirm_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar Saída"),
            content=ft.Text("Você tem certeza que deseja encerrar este treino?"),
            actions=[
                ft.TextButton("Sim", on_click=confirm_exit),
                ft.ElevatedButton("Não", on_click=close_training_dialog),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.dialog = confirm_dialog

        def open_exit_dialog(e):
            """Abre a caixa de diálogo de confirmação."""
            confirm_dialog.open = True
            self.page.update()

        # Cria os botões de navegação do player.
        prev_button = ft.IconButton(
            icon=ft.Icons.SKIP_PREVIOUS, on_click=prev_video, tooltip="Vídeo Anterior"
        )
        next_button = ft.IconButton(
            icon=ft.Icons.SKIP_NEXT, on_click=next_video, tooltip="Próximo Vídeo"
        )
        exit_button = ft.ElevatedButton("Encerrar Treino", on_click=open_exit_dialog)

        # Inicia a exibição com o primeiro vídeo da playlist e inicia o primeiro vigia.
        update_video_display(start_watch_thread=True)

        # Retorna a View completa do player de treino.
        return ft.View(
            "/training_player",
            [
                ft.Column(
                    [
                        ft.Container(
                            content=video_player,
                            height=250,
                            bgcolor=ft.Colors.BLACK,
                            border_radius=ft.border_radius.all(15),
                        ),
                        ft.Container(
                            ft.Column(
                                [video_title, video_description],
                                spacing=10,
                                scroll=ft.ScrollMode.ADAPTIVE,
                            ),
                            padding=20,
                            expand=True,
                        ),
                        ft.Row(
                            [
                                prev_button,
                                next_button,
                                ft.Container(expand=True),
                                exit_button,
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                    ],
                    expand=True,
                )
            ],
            padding=20,
        )

    def create_training_complete_view(self, user: dict) -> ft.View:
        """Cria e retorna a View de conclusão de treino."""
        user_name = user.get("LOGIN", "Usuário")
        logger.info(f"Usuário {user_name} concluiu um treino.")

        return ft.View(
            "/training_complete",
            [
                ft.Column(
                    [
                        ft.Icon(
                            name=ft.Icons.CHECK_CIRCLE_OUTLINE,
                            color=ft.Colors.GREEN,
                            size=80,
                        ),
                        ft.Text(
                            f"Parabéns, {user_name}!",
                            size=28,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Text("Playlist de treino concluída com sucesso.", size=16),
                        ft.ElevatedButton(
                            "Voltar para a Videoteca",
                            on_click=lambda _: self.page.go("/videos"),
                            height=50,
                        ),
                    ],
                    spacing=20,
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    expand=True,
                )
            ],
            padding=20,
        )

    def create_training_location_view(self) -> ft.View:
        """Cria e retorna a View (placeholder) para 'Onde Treinar'."""
        logger.info("Criando a tela 'Onde Treinar'.")

        return ft.View(
            "/training_location",
            [
                ft.Row(
                    [
                        ft.IconButton(
                            icon=ft.Icons.ARROW_BACK,
                            on_click=lambda _: self.page.go("/dashboard"),
                            tooltip="Voltar",
                        )
                    ]
                ),
                ft.Column(
                    [
                        ft.Text("Onde Treinar", size=24, weight=ft.FontWeight.BOLD),
                        ft.Divider(),
                        ft.Text("Funcionalidade em desenvolvimento.", size=16),
                        ft.Text("Em breve: Endereços, horários e mapa."),
                    ],
                    spacing=15,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            ],
            padding=20,
        )


def main(page: ft.Page):
    """
    Função principal que inicia a aplicação Flet.
    É o ponto de entrada que o `flet.app()` chama.
    """
    logger.info("Iniciando a aplicação AppFBKMKLN.")
    # Cria a instância da nossa classe principal, passando o objeto 'page'.
    AppFBKMKLN(page)


if __name__ == "__main__":
    """
    Este bloco é executado apenas quando o arquivo `main.py` é rodado diretamente.
    Ele não é executado se o arquivo for importado por outro.
    """
    logger.info("Executando a aplicação Flet via __main__.")
    # A função `flet.app()` inicia o servidor de desenvolvimento e abre a janela do aplicativo.
    # `target=main` diz ao Flet qual função deve ser chamada para construir a aplicação.
    # `assets_dir="assets"` informa ao Flet onde encontrar nossos arquivos estáticos (imagens, vídeos, etc.).
    ft.app(target=main, assets_dir="assets")
