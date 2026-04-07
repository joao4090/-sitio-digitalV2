import flet as ft
import sqlite3
import os

# --- 1. FUNÇÕES DE BANCO DE DADOS ---
# Esta função garante que o banco de dados seja salvo na pasta correta do celular
def obter_caminho_banco(page: ft.Page):
    # No Android, usamos o client_storage_path para permanência de dados
    if page.client_storage_path:
        return os.path.join(page.client_storage_path, "meu_sitio.db")
    return "meu_sitio.db"

def configurar_banco(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS lotes 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       nome TEXT, quantidade INTEGER, peso REAL)''')
    conn.commit()
    conn.close()

def salvar_lote(db_path, nome, qtd, peso):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO lotes (nome, quantidade, peso) VALUES (?, ?, ?)", (nome, qtd, peso))
    conn.commit()
    conn.close()

def excluir_lote(db_path, id_lote):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM lotes WHERE id = ?", (id_lote,))
    conn.commit()
    conn.close()

def buscar_dados(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, quantidade, peso FROM lotes")
    dados = cursor.fetchall()
    conn.close()
    return dados

# --- 2. INTERFACE DO APLICATIVO ---
def main(page: ft.Page):
    page.title = "Sítio Digital"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    page.scroll = "auto"
    
    # Configuração de layout para preencher a tela do celular
    page.horizontal_alignment = ft.CrossAxisAlignment.STRETCH

    # Inicializa o banco de dados no local correto
    db_path = obter_caminho_banco(page)
    configurar_banco(db_path)

    lista_exibicao = ft.Column(spacing=10)

    # Função para atualizar a lista na tela
    def atualizar_lista():
        lista_exibicao.controls.clear()
        dados = buscar_dados(db_path)
        for id_lote, nome, qtd, peso in dados:
            lista_exibicao.controls.append(
                ft.Card(
                    content=ft.Container(
                        padding=15,
                        content=ft.Row([
                            ft.Column([
                                ft.Text(nome, size=18, weight="bold", color="blue800"),
                                ft.Text(f"{qtd} aves | {peso}kg médios"),
                            ], expand=True),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE,
                                icon_color="red",
                                on_click=lambda e, i=id_lote: deletar_item(i)
                            )
                        ])
                    )
                )
            )
        page.update()

    def deletar_item(id_lote):
        excluir_lote(db_path, id_lote)
        atualizar_lista()

    # Campos de entrada com teclado numérico para celular
    txt_nome = ft.TextField(label="Nome do Lote", border_radius=10)
    txt_qtd = ft.TextField(label="Qtd", keyboard_type=ft.KeyboardType.NUMBER, expand=1, border_radius=10)
    txt_peso = ft.TextField(label="Peso", keyboard_type=ft.KeyboardType.NUMBER, expand=1, border_radius=10)

    def adicionar_clicado(e):
        if txt_nome.value and txt_qtd.value:
            salvar_lote(db_path, txt_nome.value, int(txt_qtd.value), float(txt_peso.value))
            txt_nome.value = ""
            txt_qtd.value = ""
            txt_peso.value = ""
            atualizar_lista()
            txt_nome.focus()

    # Estrutura visual
    page.add(
        ft.Text("Sítio Digital 🐤", size=28, weight="bold", text_align="center"),
        ft.Text("Cadastrar Lote:", weight="bold"),
        txt_nome,
        ft.Row([txt_qtd, txt_peso], spacing=10),
        ft.ElevatedButton(
            "SALVAR NO SISTEMA", 
            on_click=adicionar_clicado,
            height=50,
            bgcolor="blue700",
            color="white"
        ),
        ft.Divider(height=40),
        ft.Text("LOTES ATIVOS:", weight="bold", size=18),
        lista_exibicao
    )

    # Carregamento inicial
    atualizar_lista()

# Comando para rodar o app
if __name__ == "__main__":
    ft.app(target=main)