import flet as ft
from flet import Icons

def main(page: ft.Page):
    page.title = "Teste de Ícones Flet"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    page.add(
        ft.ElevatedButton(
            "Clique-me para Testar Ícone",
            icon=ft.Icons.CHECK, # Usando um ícone simples para teste
            on_click=lambda e: print("Botão de teste clicado!")
        )
    )
    page.update()

if __name__ == "__main__":
    ft.app(target=main)