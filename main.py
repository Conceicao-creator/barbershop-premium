import flet as ft


def main(page: ft.Page):
    # Configuração da paleta Ultra Moderna do app
    page.title = "BarberShop Premium"
    page.bgcolor = "#121214"  # Cinza Grafite Profundo
    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"

    # Texto principal em Neon Verde/Ciano Futurista
    texto_neon = ft.Text(
        value="BarberShop Imperial 1.0 💈",
        size=40,
        weight=ft.FontWeight.BOLD,
        color="#00F5D4"  # Verde Neon
    )

    # Botão moderno elegante com relevo tradicional
    botao_entrar = ft.ElevatedButton(
        text="Acessar Sistema",
        bgcolor="#FFFFFF",
        color="#121214"
    )

    # Juntar os elementos na janela
    page.add(texto_neon, ft.Container(height=20), botao_entrar)


if __name__ == "__main__":
    # 🔑 O GRANDE XEQUEMATE DE 2026: O comando de largada definitivo e direto!
    ft.run_app(main)
