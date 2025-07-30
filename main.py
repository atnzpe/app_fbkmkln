# main.py

import flet as ft
import logging

try:
    from src.auth import AuthService
    from src.utils import setup_logging
except ImportError:
    import sys
    import os

    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    from src.auth import AuthService
    from src.utils import setup_logging

SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ3u0Mnny-vm3aZkbYoXQo85IwbfkI6FtD7T_uNhnSLMTzZZarFgRJJTmONncFo8U7cUGlsYTj17aMM/pub?gid=0&single=true&output=csv"

setup_logging()
logger = logging.getLogger(__name__)


class AppFBKMKLN:
    """
    Classe principal que gerencia as telas (Views) e a lógica do aplicativo.
    """

    def __init__(self, page: ft.Page):
        logger.debug("Inicializando a classe AppFBKMKLN.")
        self.page = page
        self.auth_service = AuthService(sheet_url=SHEET_URL)

        self.setup_page_and_routes()
        self.page.go("/")  # Navega para a rota inicial (login)

    def setup_page_and_routes(self):
        """Configura as propriedades globais da página e o sistema de rotas."""
        logger.debug("Configurando propriedades da página Flet e rotas.")
        self.page.title = "FBKMKLN - Leão do Norte"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.on_route_change = self.on_route_change
        self.page.on_view_pop = self.on_view_pop

    def on_route_change(self, route):
        """Função chamada sempre que a rota (URL) da página muda."""
        logger.info(f"Navegando para a rota: {self.page.route}")
        self.page.views.clear()

        # Rota de Login
        if self.page.route == "/":
            self.page.views.append(self.create_login_view())

        # Rota do Dashboard (requer dados do usuário)
        elif self.page.route == "/dashboard" and self.page.client_storage.contains_key(
            "user_data"
        ):
            user_data = self.page.client_storage.get("user_data")
            self.page.views.append(self.create_dashboard_view(user=user_data))

        # Se a rota do dashboard for acessada sem login, redireciona para o login
        else:
            self.page.views.append(self.create_login_view())

        self.page.update()

    def on_view_pop(self, view):
        """Função chamada quando o usuário volta uma tela (não usada aqui, mas boa prática)."""
        self.page.views.pop()
        top_view = self.page.views[-1]
        self.page.go(top_view.route)

    def login(self, e):
        """Valida as credenciais e navega para o dashboard em caso de sucesso."""
        cpf = self.cpf_field.value
        senha = self.password_field.value
        logger.info(f"Tentativa de login para o CPF: {cpf}")

        user_data = self.auth_service.login(cpf, senha)

        if user_data:
            # Armazena os dados do usuário no armazenamento da sessão para recuperá-los na rota
            self.page.client_storage.set("user_data", user_data)
            self.page.go("/dashboard")
        else:
            self.login_status.value = "CPF, senha inválidos ou usuário inativo."
            self.page.update()

    def logout(self, e):
        """Limpa os dados da sessão e volta para a tela de login."""
        logger.info("Usuário fazendo logout.")
        self.page.client_storage.remove("user_data")
        self.page.go("/")

    def create_login_view(self) -> ft.View:
        """Cria e retorna a View (página) de Login."""
        self.auth_service.load_users()

        logo = ft.Image(
            src="/icon.jpg",  # Usando o logo que você forneceu
            width=150,
            height=150,
            fit=ft.ImageFit.CONTAIN,
        )

        text_field_style = {
            "label_style": ft.TextStyle(color=ft.Colors.WHITE),
            "border_color": ft.colors.with_opacity(0.5, ft.Colors.WHITE),
            "width": 300,
        }

        self.cpf_field = ft.TextField(label="CPF", autofocus=True, **text_field_style)
        self.password_field = ft.TextField(
            label="Senha", password=True, can_reveal_password=True, **text_field_style
        )
        self.login_status = ft.Text(value="", color=ft.Colors.RED_ACCENT)
        login_button = ft.ElevatedButton(text="Entrar", width=300, on_click=self.login)

        return ft.View(
            "/",
            [
                ft.Column(
                    [
                        logo,
                        ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                        self.cpf_field,
                        self.password_field,
                        self.login_status,
                        login_button,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=15,
                    expand=True,
                )
            ],
            padding=20,
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def create_dashboard_view(self, user: dict) -> ft.View:
        """Cria e retorna a View (página) do Dashboard."""
        user_name = user.get("NOME", "Usuário").split(" ")[0]

        welcome_message = ft.Text(
            f"Seja bem-vindo, {user_name}!",
            size=24,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER,
        )
        btn_logout = ft.IconButton(
            icon=ft.Icons.LOGOUT, on_click=self.logout, tooltip="Sair"
        )

        header = ft.Row(
            [
                ft.Container(
                    content=welcome_message,
                    expand=True,
                    alignment=ft.alignment.center_left,
                ),
                btn_logout,
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        # Estilo customizado para os botões do dashboard
        button_style = ft.ButtonStyle(
            color=ft.Colors.WHITE,  # Cor da fonte
            bgcolor=ft.Colors.WHITE24,  # Cor de fundo (cinza claro transparente)
        )

        btn_programa = ft.ElevatedButton(
            "Programa Técnico",
            icon=ft.Icons.DESCRIPTION,
            on_click=lambda e: logger.debug("Botão 'Programa Técnico' clicado"),
            height=50,
            style=button_style,
        )
        btn_videos = ft.ElevatedButton(
            "Vídeos de Movimentos",
            icon=ft.Icons.VIDEO_LIBRARY,
            on_click=lambda e: logger.debug("Botão 'Vídeos de Movimentos' clicado"),
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
        btn_social = ft.ElevatedButton(
            "Mídias Sociais",
            icon=ft.Icons.GROUP,
            on_click=lambda e: logger.debug("Botão 'Mídias Sociais' clicado"),
            height=50,
            style=button_style,
        )

        dashboard_buttons = ft.ResponsiveRow(
            [
                ft.Column([btn_programa], col={"xs": 12, "sm": 6, "md": 4}),
                ft.Column([btn_videos], col={"xs": 12, "sm": 6, "md": 4}),
                ft.Column([btn_analisador], col={"xs": 12, "sm": 6, "md": 4}),
                ft.Column([btn_cursos], col={"xs": 12, "sm": 6, "md": 4}),
                ft.Column([btn_social], col={"xs": 12, "sm": 6, "md": 4}),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            run_spacing=10,
            spacing=10,
        )

        return ft.View(
            "/dashboard",
            [
                ft.Column(
                    [
                        header,
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


def main(page: ft.Page):
    """Função principal que inicia a aplicação Flet."""
    logger.info("Iniciando a aplicação AppFBKMKLN.")
    AppFBKMKLN(page)


if __name__ == "__main__":
    logger.info("Executando a aplicação Flet via __main__.")
    ft.app(target=main, assets_dir="assets")
