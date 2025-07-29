# main.py

import flet as ft
import logging

from src.auth import AuthService

# URL da sua planilha publicada como CSV
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ3u0Mnny-vm3aZkbYoXQo85IwbfkI6FtD7T_uNhnSLMTzZZarFgRJJTmONncFo8U7cUGlsYTj17aMM/pub?gid=0&single=true&output=csv"

# Configuração básica de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AppFBKMKLN:
    """
    Classe principal que gerencia as telas e a lógica do aplicativo da Federação.
    """
    def __init__(self, page: ft.Page):
        """
        Construtor da aplicação.
        """
        self.page = page
        self.auth_service = AuthService(sheet_url=SHEET_URL)
        
        self.setup_page()
        self.show_login_view()

    def setup_page(self):
        """Configura as propriedades globais da página/janela."""
        self.page.title = "FBKMKLN - Leão do Norte"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.bgcolor = ft.colors.BLACK
        self.page.padding = ft.padding.symmetric(horizontal=15, vertical=30)


    def show_login_view(self, e=None):
        """Limpa a página, recarrega os dados dos usuários e desenha a tela de login."""
        # **CORREÇÃO:** Força o recarregamento dos dados da planilha toda vez que
        # a tela de login é exibida (no início do app ou após um logout).
        self.auth_service.load_users()
        
        self.page.clean()
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

        logo = ft.Image(src="/icon.png", width=150, height=150)
        self.cpf_field = ft.TextField(label="CPF", width=300)
        self.password_field = ft.TextField(label="Senha", password=True, can_reveal_password=True, width=300)
        self.login_status = ft.Text(value="", color=ft.colors.RED_ACCENT)
        login_button = ft.ElevatedButton(text="Entrar", width=300, on_click=self.login)

        self.page.add(
            ft.Column(
                [
                    logo,
                    self.cpf_field,
                    self.password_field,
                    self.login_status,
                    login_button,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=15,
            )
        )
        self.page.update()

    def login(self, e):
        """
        Função de login que usa o AuthService para validar as credenciais.
        """
        cpf = self.cpf_field.value
        senha = self.password_field.value
        
        user_data = self.auth_service.login(cpf, senha)
        
        if user_data:
            self.login_status.value = ""
            self.show_dashboard_view(user_data)
        else:
            self.login_status.value = "CPF, senha inválidos ou usuário inativo."
            self.page.update()

    def show_dashboard_view(self, user: dict):
        """
        Limpa a página e desenha o dashboard principal com os dados do usuário logado.
        """
        self.page.clean()
        self.page.vertical_alignment = ft.MainAxisAlignment.START
        self.page.padding = ft.padding.all(20)

        user_name = user.get('NOME', 'Usuário').split(' ')[0]

        logo_header = ft.Image(src="/icon.png", width=70, height=70)
        welcome_message = ft.Text(f"Seja bem-vindo, {user_name}!", size=24, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)
        
        header = ft.Row([logo_header, welcome_message], alignment=ft.MainAxisAlignment.CENTER, spacing=20, wrap=True)

        btn_programa = ft.ElevatedButton("Programa Técnico", icon=ft.icons.DESCRIPTION, on_click=lambda e: print("Programa Técnico clicado"), height=50)
        btn_videos = ft.ElevatedButton("Vídeos de Movimentos", icon=ft.icons.VIDEO_LIBRARY, on_click=lambda e: print("Vídeos clicado"), height=50)
        btn_analisador = ft.ElevatedButton("Analisador de Movimentos", icon=ft.icons.ANALYTICS, on_click=lambda e: print("Analisador clicado"), height=50)
        btn_cursos = ft.ElevatedButton("Cursos", icon=ft.icons.SCHOOL, on_click=lambda e: print("Cursos clicado"), height=50, disabled=True)
        btn_social = ft.ElevatedButton("Mídias Sociais", icon=ft.icons.GROUP, on_click=lambda e: print("Mídias clicado"), height=50)
        btn_logout = ft.IconButton(icon=ft.icons.LOGOUT, on_click=self.show_login_view, tooltip="Sair")

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
            spacing=10
        )

        self.page.add(
            ft.Column(
                [
                    ft.Row([ft.Container(expand=True), btn_logout]),
                    header,
                    ft.Divider(height=20),
                    dashboard_buttons
                ],
                expand=True,
                spacing=25,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )
        self.page.update()

def main(page: ft.Page):
    """Função principal que inicia a aplicação Flet."""
    AppFBKMKLN(page)

if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")