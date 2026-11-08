"""Cabeçalho da agenda e animação para expandir/recolher controles."""
import flet as ft
from horarios import segunda

def criar_cabecalho(semana_atual, hoje, editar, mudar_semana, ir_hoje, abrir_visao_completa, titulo_periodo, resumo):
    topo_recolhido = [False]
    cab = ft.Container(
        animate_opacity=ft.Animation(duration=220, curve=ft.AnimationCurve.EASE_IN_OUT),
        bgcolor="#FFFFFF", padding=ft.Padding.symmetric(horizontal=20, vertical=16),
        border=ft.Border(bottom=ft.BorderSide(1, "#E7ECF4")),
        content=ft.Column(spacing=12, controls=[
            ft.Row(wrap=True, spacing=12, alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                ft.Row(spacing=10, controls=[
                    ft.Icon(ft.Icons.EVENT_NOTE, color="#4B71D0", size=28),
                    ft.Column(spacing=0, controls=[
                        ft.Text("Minha Semana", size=23, weight=ft.FontWeight.BOLD, color="#25334E"),
                        ft.Text("Seu tempo, organizado do seu jeito", size=12, color="#79849A")
                    ])
                ]),
                ft.Button("Nova atividade", icon=ft.Icons.ADD,
                          on_click=lambda e: editar(dia=hoje if segunda(hoje) == semana_atual[0] else semana_atual[0])),
            ]),
            ft.Row(wrap=True, spacing=7, controls=[
                ft.IconButton(icon=ft.Icons.CHEVRON_LEFT, tooltip="Semana anterior", on_click=lambda e: mudar_semana(-1)),
                ft.IconButton(icon=ft.Icons.CHEVRON_RIGHT, tooltip="Próxima semana", on_click=lambda e: mudar_semana(1)),
                ft.TextButton("Hoje", on_click=ir_hoje),
                ft.Button("Visão completa", icon=ft.Icons.GRID_VIEW, on_click=abrir_visao_completa),
                titulo_periodo,
            ]),
            resumo,
        ]),
    )
    # O invólucro anima a altura, sem remover o cabeçalho da árvore.
    # Isso mantém os controles intactos e evita o salto visual do visible=False.
    faixa_topo = ft.Container(
        content=cab,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        animate_size=ft.Animation(duration=280, curve=ft.AnimationCurve.EASE_IN_OUT),
    )

    def alternar_cabecalho(e):
        topo_recolhido[0] = not topo_recolhido[0]
        faixa_topo.height = 0 if topo_recolhido[0] else None
        cab.opacity = 0 if topo_recolhido[0] else 1
        faixa_topo.update()
        botao_cabecalho.icon = (
            ft.Icons.KEYBOARD_ARROW_DOWN if topo_recolhido[0]
            else ft.Icons.KEYBOARD_ARROW_UP
        )
        botao_cabecalho.update()

    botao_cabecalho = ft.IconButton(
        icon=ft.Icons.KEYBOARD_ARROW_UP,
        tooltip="Recolher ou expandir controles",
        on_click=alternar_cabecalho,
    )
    # O botão fica fora do bloco que se recolhe.
    barra_compacta = ft.Container(
        bgcolor="#FFFFFF", height=35,
        content=ft.Row(spacing=0, controls=[botao_cabecalho]),
    )
    return cab, faixa_topo, barra_compacta, topo_recolhido
