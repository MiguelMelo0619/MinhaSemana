"""Grade interativa da semana: DataTable2 com dias e horários fixos."""
from datetime import date, timedelta
import flet as ft
import flet_datatable2 as fdt
from config import (DIAS, CORES, PRIMEIRO_HORARIO, ULTIMO_HORARIO, INTERVALO, SLOT_HEIGHT, DAY_WIDTH, TIME_WIDTH, COR_LINHA_MEIA_HORA, COR_LINHA_HORA_CHEIA, COR_DIVISAO_DIAS)
from horarios import horario

def criar_tabela(tarefas, semana_atual, editar):
    atividades_por_dia = {}
    for indice in range(7):
        dia = (semana_atual[0] + timedelta(days=indice)).isoformat()
        atividades_por_dia[dia] = [
            t for t in tarefas if t["dia"] == dia
            and t["fim"] > PRIMEIRO_HORARIO
            and t["inicio"] < ULTIMO_HORARIO
        ]

    colunas = [
        fdt.DataColumn2(
            label=ft.Text("Hora", size=11, color="#64718C"),
            fixed_width=TIME_WIDTH,
        )
    ]
    for indice in range(7):
        dia = semana_atual[0] + timedelta(days=indice)
        destaque = dia == date.today()
        colunas.append(fdt.DataColumn2(
            fixed_width=DAY_WIDTH,
            label=ft.Column(
                spacing=2,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text(DIAS[indice], size=12, color="#315FC2" if destaque else "#64718C"),
                    ft.Text(f"{dia:%d/%m}", size=15, weight=ft.FontWeight.BOLD,
                            color="#315FC2" if destaque else "#25334E"),
                ],
            ),
        ))

    linhas = []
    for minuto in range(PRIMEIRO_HORARIO, ULTIMO_HORARIO, INTERVALO):
        # A linha que termina uma hora é mais forte que a de meia hora.
        fim_de_hora = (minuto + INTERVALO) % 60 == 0
        cor_linha = COR_LINHA_HORA_CHEIA if fim_de_hora else COR_LINHA_MEIA_HORA
        espessura = 1.6 if fim_de_hora else 1.0
        divisao_inferior = ft.BorderSide(espessura, cor_linha)
        divisao_vertical = ft.BorderSide(1.0, COR_DIVISAO_DIAS)
        celulas = [ft.DataCell(ft.Container(
            height=SLOT_HEIGHT,
            bgcolor="#EAF0F9" if minuto % 60 == 0 else "#F4F7FC",
            border=ft.Border(bottom=divisao_inferior, right=divisao_vertical),
            alignment=ft.Alignment.TOP_CENTER,
            content=ft.Text(horario(minuto), size=11,
                            weight=ft.FontWeight.BOLD if minuto % 60 == 0 else ft.FontWeight.NORMAL,
                            color="#334867" if minuto % 60 == 0 else "#65758E"),
        ))]
        for indice in range(7):
            dia = semana_atual[0] + timedelta(days=indice)
            atividade = next((
                t for t in atividades_por_dia[dia.isoformat()]
                if t["inicio"] <= minuto < t["fim"]
            ), None)
            if atividade:
                fundo, cor_texto, borda = CORES.get(atividade["cor"], CORES["Azul"])
                # O bloco continua clicável em toda a sua duração.
                # Nas linhas seguintes, o fundo mantém a mesma cor.
                inicio_visual = max(atividade["inicio"], PRIMEIRO_HORARIO)
                texto = (("✓ " if atividade["concluida"] else "") + atividade["titulo"])
                if minuto != inicio_visual:
                    texto = ""
                celulas.append(ft.DataCell(ft.Container(
                    height=SLOT_HEIGHT,
                    bgcolor=fundo,
                    border=ft.Border(
                        left=ft.BorderSide(4, borda),
                        right=divisao_vertical,
                        bottom=divisao_inferior,
                    ),
                    padding=ft.Padding.symmetric(horizontal=5, vertical=4),
                    ink=True,
                    on_click=lambda e, t=atividade: editar(tarefa=t),
                    tooltip=f"{atividade['titulo']} · {horario(atividade['inicio'])}–{horario(atividade['fim'])}",
                    content=ft.Text(texto, size=11, color=cor_texto,
                                    max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
                )))
            else:
                celulas.append(ft.DataCell(ft.Container(
                    height=SLOT_HEIGHT,
                    bgcolor="#F5F8FD" if minuto % 60 == 0 else "#FFFFFF",
                    border=ft.Border(right=divisao_vertical, bottom=divisao_inferior),
                    alignment=ft.Alignment.CENTER,
                    ink=True,
                    on_click=lambda e, d=dia, m=minuto: editar(dia=d, inicio=m),
                    content=ft.Icon(ft.Icons.ADD, size=13, color="#CBD3E1"),
                )))
        linhas.append(ft.DataRow(cells=celulas))

    tabela = fdt.DataTable2(
        expand=True,
        columns=colunas,
        rows=linhas,
        heading_row_height=65,
        data_row_height=SLOT_HEIGHT,
        fixed_left_columns=1,
        fixed_top_rows=1,
        min_width=TIME_WIDTH + 7 * DAY_WIDTH,
        horizontal_margin=0,
        column_spacing=0,
        show_checkbox_column=False,
        fixed_corner_color="#EAF0F9",
        fixed_columns_color="#F1F5FB",
        visible_horizontal_scroll_bar=False,
    )
    return tabela
