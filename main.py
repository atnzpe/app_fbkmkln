# main.py

import flet as ft
import logging
import sys
try:
    from src.auth import AuthService
    from src.utils import setup_logging
except ImportError:
    
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
        self.page.go("/")

    def setup_page_and_routes(self):
        """Configura as propriedades globais da página e o sistema de rotas."""
        logger.debug("Configurando propriedades da página Flet e rotas.")
        self.page.title = "FBKMKLN - Leão do Norte"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.bgcolor = ft.Colors.BLACK
        self.page.on_route_change = self.on_route_change
        self.page.on_view_pop = self.on_view_pop

    def on_route_change(self, route):
        """Função chamada sempre que a rota (URL) da página muda."""
        logger.info(f"Navegando para a rota: {self.page.route}")
        self.page.views.clear()

        if self.page.route == "/":
            self.page.views.append(self.create_login_view())
        elif self.page.route == "/dashboard" and self.page.client_storage.contains_key(
            "user_data"
        ):
            user_data = self.page.client_storage.get("user_data")
            self.page.views.append(self.create_dashboard_view(user=user_data))
        else:
            self.page.views.append(self.create_login_view())

        self.page.update()

    def on_view_pop(self, view):
        """Função chamada quando o usuário volta uma tela."""
        self.page.views.pop()
        top_view = self.page.views[-1]
        self.page.go(top_view.route)

    def login(self, e):
        """Valida as credenciais e navega para o dashboard."""
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
        """Limpa os dados da sessão e volta para a tela de login."""
        logger.info("Usuário fazendo logout.")
        self.page.client_storage.remove("user_data")
        self.page.go("/")

    def create_login_view(self) -> ft.View:
        """Cria e retorna a View (página) de Login."""
        self.auth_service.load_users()

        logo = ft.Image(
            src="/icon.jpg",
            width=150,
            height=150,
            fit=ft.ImageFit.CONTAIN,
        )

        text_field_style = {
            "label_style": ft.TextStyle(color=ft.Colors.WHITE),
            "border_color": ft.Colors.with_opacity(0.5, ft.Colors.WHITE),
            "width": 300,
        }

        self.cpf_field = ft.TextField(label="CPF", autofocus=True, **text_field_style)
        self.password_field = ft.TextField(
            label="Senha", password=True, can_reveal_password=True, **text_field_style
        )
        self.login_status = ft.Text(value="", color=ft.Colors.RED_ACCENT)
        login_button = ft.ElevatedButton(text="Entrar", width=300, on_click=self.login)

        # **CORREÇÃO APLICADA:** O método correto para fechar a janela é `window_destroy()`.
        exit_button = ft.OutlinedButton(
            text="Encerrar Aplicativo",
            width=300,
            on_click=lambda _: self.page.window.destroy(),
        )

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
                        exit_button,
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
        user_login_name = user.get("LOGIN", "Usuário").split(" ")[0]
        logger.info(f"Exibindo dashboard para o usuário: {user_login_name}")

        logo_header = ft.Image(
            src="/icon.jpg", width=120, height=120, border_radius=ft.border_radius.all(40)
        )
        welcome_message = ft.Text(
            f"Kidá (קידה),{user_login_name}!", size=24, weight=ft.FontWeight.BOLD
        )

        header_content = ft.Column(
            [logo_header, welcome_message],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )

        btn_logout = ft.IconButton(
            icon=ft.Icons.LOGOUT, on_click=self.logout, tooltip="Sair"
        )

        header_row = ft.Row([ft.Container(expand=True), btn_logout])

        button_style = ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.WHITE24)

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


def main(page: ft.Page):
    """Função principal que inicia a aplicação Flet."""
    logger.info("Iniciando a aplicação AppFBKMKLN.")
    AppFBKMKLN(page)


if __name__ == "__main__":
    logger.info("Executando a aplicação Flet via __main__.")
    ft.app(target=main, assets_dir="assets")
