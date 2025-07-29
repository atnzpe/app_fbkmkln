# main.py

import flet as ft
import logging
import os
import cv2
import base64
import threading
import time
import sys
import numpy as np
from datetime import datetime

# Importa os módulos customizados da pasta 'src'.
from src.utils import setup_logging, get_logger
from src.video_analyzer import VideoAnalyzer
from src.report_generator import ReportGenerator
from src.renderer_3d import render_3d_skeleton

# Configura o sistema de logging.
setup_logging()
logger = get_logger(__name__)


# Simulação de dados do usuário até termos a planilha
LOGGED_IN_USER = "Gleyson"


class AppFBKMKLN:
    """
    Classe principal que gerencia as telas e a lógica do aplicativo da Federação.
    """

    def __init__(self, page: ft.Page):
        """
        Construtor da aplicação.
        Args:
            page (ft.Page): A página Flet principal.
        """
        self.page = page
        self.setup_page()
        self.show_login_view()

    def setup_page(self):
        """Configura as propriedades globais da página/janela."""
        self.page.title = "FBKMKLN - Leão do Norte"
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.bgcolor = ft.Colors.BLACK

    def show_login_view(self, e=None):
        """Limpa a página e desenha a tela de login."""
        self.page.clean()
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.page.padding = ft.padding.all(10)

        logo = ft.Image(src="/icon.png", width=200, height=200)
        cpf_field = ft.TextField(label="CPF", width=300)
        password_field = ft.TextField(
            label="Senha", password=True, can_reveal_password=True, width=300
        )
        login_button = ft.ElevatedButton(text="Entrar", width=300, on_click=self.login)

        self.page.add(
            ft.Column(
                [
                    logo,
                    cpf_field,
                    password_field,
                    login_button,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
            )
        )
        self.page.update()

    def login(self, e):
        """
        Função de login simulada. Avança para o dashboard.
        """
        self.show_dashboard_view()

    def show_dashboard_view(self):
        """Limpa a página e desenha o dashboard principal."""
        self.page.clean()
        self.page.vertical_alignment = ft.MainAxisAlignment.START
        self.page.padding = ft.padding.all(20)

        logo_header = ft.Image(src="/icon.png", width=70, height=70)
        welcome_message = ft.Text(
            f"Seja bem-vindo, {LOGGED_IN_USER}!", size=24, weight=ft.FontWeight.BOLD
        )

        header = ft.Row(
            [logo_header, welcome_message],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20,
        )

        btn_programa = ft.ElevatedButton(
            "Programa Técnico",
            icon=ft.Icons.DESCRIPTION,
            on_click=lambda e: print("Programa Técnico clicado"),
            height=50,
        )
        btn_videos = ft.ElevatedButton(
            "Vídeos de Movimentos",
            icon=ft.Icons.VIDEO_LIBRARY,
            on_click=lambda e: print("Vídeos clicado"),
            height=50,
        )
        btn_analisador = ft.ElevatedButton(
            "Analisador de Movimentos",
            icon=ft.Icons.ANALYTICS,
            on_click=self.show_analyzer_view,
            height=50,
        )
        btn_cursos = ft.ElevatedButton(
            "Cursos",
            icon=ft.Icons.SCHOOL,
            on_click=lambda e: print("Cursos clicado"),
            height=50,
            disabled=True,
        )
        btn_social = ft.ElevatedButton(
            "Mídias Sociais",
            icon=ft.Icons.GROUP,
            on_click=lambda e: print("Mídias clicado"),
            height=50,
        )
        btn_logout = ft.IconButton(
            icon=ft.Icons.LOGOUT, on_click=self.show_login_view, tooltip="Sair"
        )

        dashboard_buttons = ft.ResponsiveRow(
            [
                ft.Column([btn_programa], col={"xs": 12, "md": 4}),
                ft.Column([btn_videos], col={"xs": 12, "md": 4}),
                ft.Column([btn_analisador], col={"xs": 12, "md": 4}),
                ft.Column([btn_cursos], col={"xs": 12, "md": 4}),
                ft.Column([btn_social], col={"xs": 12, "md": 4}),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            run_spacing=10,
        )

        self.page.add(
            ft.Column(
                [
                    ft.Row([ft.Container(expand=True), btn_logout]),
                    header,
                    ft.Divider(),
                    dashboard_buttons,
                ],
                expand=True,
                spacing=25,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        )
        self.page.update()

    def show_analyzer_view(self, e=None):
        """
        Limpa a página e mostra a interface do Analisador de Movimentos.
        (Esta parte será o nosso antigo `main.py` do Projeto 1, adaptado)
        """
        # Por enquanto, apenas uma mensagem de placeholder.
        self.page.clean()
        back_button = ft.IconButton(
            icon=ft.Icons.ARROW_BACK, on_click=lambda e: self.show_dashboard_view()
        )
        self.page.add(
            ft.Column(
                [
                    back_button,
                    ft.Text("Módulo Analisador de Movimentos", size=24),
                    ft.Text("Esta tela conterá a funcionalidade do Projeto 1."),
                ]
            )
        )
        self.page.update()


def main(page: ft.Page):
    """Função principal que inicia a aplicação Flet."""
    AppFBKMKLN(page)


if __name__ == "__main__":
    # O `assets_dir` continua sendo crucial.
    ft.app(target=main, assets_dir="assets")
