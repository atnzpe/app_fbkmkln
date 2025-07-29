# main.py

import flet as ft
import logging

# Tenta importar o AuthService. Se falhar, ajusta o path e tenta novamente.
# Isso garante que o código funcione tanto se executado da raiz quanto de dentro de 'src'.
try:
    from src.auth import AuthService
    from src.utils import setup_logging
except ImportError:
    import sys
    import os

    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    from src.auth import AuthService
    from src.utils import setup_logging

# URL da sua planilha publicada como CSV
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ3u0Mnny-vm3aZkbYoXQo85IwbfkI6FtD7T_uNhnSLMTzZZarFgRJJTmONncFo8U7cUGlsYTj17aMM/pub?gid=0&single=true&output=csv"

# Configura o sistema de logging para gerar o arquivo logs/app.log
setup_logging()
logger = logging.getLogger(__name__)


class AppFBKMKLN:
    """
    Classe principal que gerencia as telas e a lógica do aplicativo da Federação.
    """

    def __init__(self, page: ft.Page):
        self.page = page
        self.auth_service = AuthService(sheet_url=SHEET_URL)
        self.setup_page()
        self.show_login_view()

    def setup_page(self):
        """Configura as propriedades globais da página/janela."""
        self.page.title = "FBKMKLN - Leão do Norte"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.padding = 0  # Remove o padding da página para a imagem ocupar tudo
        self.page.window_maximizable = False
        self.page.window_resizable = False

    def _create_background_container(self, content: ft.Control) -> ft.Container:
        """
        Cria um container que serve como base para as telas, com imagem de fundo e gradiente.
        Esta é a implementação que usa a técnica da documentação para criar o efeito de opacidade.
        """
        return ft.Container(
            expand=True,
            image_src="/background_img.jpeg",  # Nome do seu arquivo de imagem em /assets
            image_fit=ft.ImageFit.COVER,
            content=ft.Container(
                # Gradiente semi-transparente para escurecer o fundo e melhorar a legibilidade
                gradient=ft.LinearGradient(
                    begin=ft.alignment.top_center,
                    end=ft.alignment.bottom_center,
                    Colors=[
                        ft.Colors.with_opacity(0.6, "black"),
                        ft.Colors.with_opacity(0.8, "black"),
                    ],
                ),
                padding=ft.padding.symmetric(horizontal=20, vertical=30),
                content=content,
                alignment=ft.alignment.center,
            ),
        )

    def show_login_view(self, e=None):
        """Limpa a página e desenha a tela de login."""
        self.auth_service.load_users()
        self.page.clean()

        self.cpf_field = ft.TextField(label="CPF", width=300, autofocus=True)
        self.password_field = ft.TextField(
            label="Senha", password=True, can_reveal_password=True, width=300
        )
        self.login_status = ft.Text(value="", color=ft.Colors.RED_ACCENT)
        login_button = ft.ElevatedButton(text="Entrar", width=300, on_click=self.login)

        # Conteúdo da tela de login, sem o logo, com um título de texto
        login_content = ft.Column(
            [
                ft.Text("Federação Leão do Norte", size=32, weight=ft.FontWeight.BOLD),
                ft.Text("Krav Maga & Kapap", size=18, color=ft.Colors.WHITE70),
                ft.Divider(height=30, color=ft.Colors.TRANSPARENT),
                self.cpf_field,
                self.password_field,
                self.login_status,
                login_button,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15,
        )

        self.page.add(self._create_background_container(login_content))
        self.page.update()

    def login(self, e):
        """Valida as credenciais usando o AuthService."""
        cpf = self.cpf_field.value
        senha = self.password_field.value
        user_data = self.auth_service.login(cpf, senha)

        if user_data:
            self.show_dashboard_view(user_data)
        else:
            self.login_status.value = "CPF, senha inválidos ou usuário inativo."
            self.page.update()

    def show_dashboard_view(self, user: dict):
        """Desenha o dashboard principal."""
        self.page.clean()

        user_name = user.get("NOME", "Usuário").split(" ")[0]

        welcome_message = ft.Text(
            f"Seja bem-vindo, {user_name}!",
            size=24,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER,
        )
        btn_logout = ft.IconButton(
            icon=ft.icons.LOGOUT, on_click=self.show_login_view, tooltip="Sair"
        )

        header = ft.Row(
            [
                ft.Container(
                    content=welcome_message,
                    expand=True,
                    alignment=ft.alignment.center_left,
                    padding=ft.padding.only(left=20),
                ),
                btn_logout,
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        btn_programa = ft.ElevatedButton(
            "Programa Técnico",
            icon=ft.icons.DESCRIPTION,
            on_click=lambda e: print("Programa Técnico clicado"),
            height=50,
        )
        btn_videos = ft.ElevatedButton(
            "Vídeos de Movimentos",
            icon=ft.icons.VIDEO_LIBRARY,
            on_click=lambda e: print("Vídeos clicado"),
            height=50,
        )
        btn_analisador = ft.ElevatedButton(
            "Analisador de Movimentos",
            icon=ft.icons.ANALYTICS,
            on_click=lambda e: print("Analisador clicado"),
            height=50,
        )
        btn_cursos = ft.ElevatedButton(
            "Cursos",
            icon=ft.icons.SCHOOL,
            on_click=lambda e: print("Cursos clicado"),
            height=50,
            disabled=True,
        )
        btn_social = ft.ElevatedButton(
            "Mídias Sociais",
            icon=ft.icons.GROUP,
            on_click=lambda e: print("Mídias clicado"),
            height=50,
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

        dashboard_content = ft.Column(
            [header, ft.Divider(height=20, color=ft.Colors.WHITE24), dashboard_buttons],
            spacing=25,
        )

        self.page.add(self._create_background_container(dashboard_content))
        self.page.update()


def main(page: ft.Page):
    """Função principal que inicia a aplicação Flet."""
    AppFBKMKLN(page)


if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")
