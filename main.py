"""Ponto de entrada do Minha Semana (Flet). Execute: python main.py"""
from datetime import date, timedelta
import flet as ft

from database import conectar, carregar_semana
from horarios import segunda
from editor import criar_editor
from agenda import criar_tabela
from visao_completa import criar_visao_completa
from cabecalho import criar_cabecalho


def main(page: ft.Page):
    db = conectar()
    page.title = "Minha Semana | Organizador"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#F6F8FC"
    page.padding = 0
    page.window.min_width = 350
    page.window.min_height = 500
    page.theme = ft.Theme(color_scheme_seed="#5277D8")

    hoje = date.today()
    semana_atual = [segunda(hoje)]
    modo_resumo = [False]
    titulo_periodo = ft.Text(size=17, weight=ft.FontWeight.BOLD, color="#26334D")
    resumo = ft.Text(size=12, color="#6D7890")
    grade = ft.Column(spacing=0, expand=True)
    raiz = ft.Column(expand=True, spacing=0)

    def mudar_semana(delta):
        semana_atual[0] += timedelta(days=7 * delta)
        desenhar()

    def ir_hoje(e):
        semana_atual[0] = segunda(date.today())
        desenhar()

    def abrir_visao_completa(e):
        modo_resumo[0] = True
        desenhar()

    def voltar_agenda(e):
        modo_resumo[0] = False
        topo_recolhido[0] = False
        desenhar()

    editar = criar_editor(page, db, semana_atual, hoje, lambda: desenhar())
    desenhar_visao_completa = criar_visao_completa(
        page, semana_atual, raiz, mudar_semana, voltar_agenda
    )
    cab, faixa_topo, barra_compacta, topo_recolhido = criar_cabecalho(
        semana_atual, hoje, editar, mudar_semana, ir_hoje,
        abrir_visao_completa, titulo_periodo, resumo
    )

    def desenhar():
        tarefas = carregar_semana(db, semana_atual[0])
        ultima = semana_atual[0] + timedelta(days=6)
        titulo_periodo.value = f"{semana_atual[0]:%d/%m/%Y}  —  {ultima:%d/%m/%Y}"
        horas = sum(t["fim"] - t["inicio"] for t in tarefas) / 60
        resumo.value = (
            f"{len(tarefas)} atividades nesta semana  ·  {horas:g} h planejadas"
            "  ·  toque num espaço livre para adicionar"
        )

        if modo_resumo[0]:
            desenhar_visao_completa(tarefas)
            page.update()
            return

        tabela = criar_tabela(tarefas, semana_atual, editar)
        faixa_topo.height = 0 if topo_recolhido[0] else None
        cab.opacity = 0 if topo_recolhido[0] else 1
        grade.controls = [tabela]
        raiz.controls = [faixa_topo, barra_compacta, grade]
        page.update()

    page.add(ft.SafeArea(
        content=raiz,
        expand=True,
        minimum_padding=ft.Padding.only(top=10, bottom=3),
    ))

    def ao_redimensionar(e):
        if modo_resumo[0]:
            desenhar()

    page.on_resize = ao_redimensionar
    desenhar()


if __name__ == "__main__":
    ft.run(main)
