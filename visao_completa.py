"""Visualização compacta com todos os horários da semana na mesma tela."""
from datetime import date, timedelta
import flet as ft
from config import PRIMEIRO_HORARIO, ULTIMO_HORARIO, INTERVALO, CORES
from horarios import horario

def criar_visao_completa(page, semana_atual, raiz, mudar_semana, voltar_agenda):
    def desenhar_visao_completa(tarefas):
        """Mostra a semana inteira em uma única tela, sem rolagem de horários.

        A escala é calculada para a tela atual. Em telas estreitas as palavras
        são abreviadas para preservar os sete dias lado a lado.
        """
        largura = page.width or 390
        altura = page.height or 780
        # Apenas uma pequena barra superior permanece nesta tela.
        # 34 faixas de meia hora precisam caber integralmente sem rolagem vertical.
        # Considera a área reservada para a barra de status / navegação do Android.
        altura_slot = max(8.0, min(25.0, (altura - 164) / 34))
        largura_horas = 43
        largura_dia = max(30, (largura - largura_horas - 12) / 7)
        largura_texto = max(6.5, min(10.0, largura_dia / 7.7))
        dias_curtos = ["SEG", "TER", "QUA", "QUI", "SEX", "SÁB", "DOM"]

        cabecalhos = ft.Row(spacing=0, controls=[
            ft.Container(width=largura_horas, height=37, bgcolor="#EDF1F8"),
            *[
                ft.Container(
                    width=largura_dia, height=37, bgcolor="#E6EEFF" if
                    semana_atual[0] + timedelta(days=i) == date.today() else "#F5F7FC",
                    alignment=ft.Alignment.CENTER,
                    border=ft.Border(right=ft.BorderSide(1, "#DDE4F0")),
                    content=ft.Column(spacing=0,
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Text(dias_curtos[i], size=9, weight=ft.FontWeight.BOLD, color="#405274"),
                            ft.Text(f"{(semana_atual[0] + timedelta(days=i)):%d/%m}", size=9,
                                    color="#405274"),
                        ]),
                ) for i in range(7)
            ],
        ])

        regua = ft.Column(spacing=0, controls=[
            ft.Container(
                width=largura_horas, height=altura_slot,
                bgcolor="#F6F8FC" if m % 60 == 0 else "#FFFFFF",
                alignment=ft.Alignment.TOP_CENTER,
                border=ft.Border(bottom=ft.BorderSide(0.5, "#EDF0F6")),
                content=ft.Text(horario(m), size=8, color="#64718C"),
            ) for m in range(PRIMEIRO_HORARIO, ULTIMO_HORARIO, INTERVALO)
        ])

        colunas = []
        for i in range(7):
            d = (semana_atual[0] + timedelta(days=i)).isoformat()
            atividades = sorted(
                (t for t in tarefas if t["dia"] == d and
                 t["fim"] > PRIMEIRO_HORARIO and t["inicio"] < ULTIMO_HORARIO),
                key=lambda t: t["inicio"],
            )
            atividades_inicio = {max(PRIMEIRO_HORARIO, t["inicio"]): t for t in atividades}
            celulas = []
            minuto = PRIMEIRO_HORARIO
            while minuto < ULTIMO_HORARIO:
                t = atividades_inicio.get(minuto)
                if t:
                    fim = min(t["fim"], ULTIMO_HORARIO)
                    num_slots = (fim - minuto) // INTERVALO
                    cor_fundo, cor_letra, cor_borda = CORES.get(t["cor"], CORES["Azul"])
                    h = num_slots * altura_slot
                    # O nome aparece em cada bloco e não é editado nesta tela:
                    # a visão normal permanece responsável pela edição.
                    rotulo = ("✓ " if t["concluida"] else "") + t["titulo"]
                    celulas.append(ft.Container(
                        height=h, width=largura_dia, bgcolor=cor_fundo,
                        border=ft.Border(left=ft.BorderSide(2, cor_borda),
                                         bottom=ft.BorderSide(1, "#FFFFFF")),
                        padding=ft.Padding.symmetric(horizontal=2, vertical=0),
                        tooltip=f"{t['titulo']} · {horario(t['inicio'])}–{horario(t['fim'])}",
                        content=ft.Text(rotulo, size=largura_texto,
                                        color=cor_letra, weight=ft.FontWeight.W_600,
                                        max_lines=max(1, int(h / (largura_texto + 2))),
                                        overflow=ft.TextOverflow.ELLIPSIS),
                    ))
                    minuto = fim
                else:
                    celulas.append(ft.Container(
                        width=largura_dia, height=altura_slot,
                        bgcolor="#FAFBFE" if minuto % 60 == 0 else "#FFFFFF",
                        border=ft.Border(right=ft.BorderSide(0.5, "#E6EAF3"),
                                         bottom=ft.BorderSide(0.5, "#EDF0F6")),
                    ))
                    minuto += INTERVALO
            colunas.append(ft.Column(spacing=0, controls=celulas))

        tabela = ft.Column(spacing=0, controls=[
            cabecalhos,
            ft.Row(spacing=0, vertical_alignment=ft.CrossAxisAlignment.START,
                   controls=[regua, *colunas]),
        ])
        # Tela exclusiva: não renderiza título, formulário ou barra de navegação
        # da agenda normal acima da tabela.
        barra = ft.Container(
            height=52, bgcolor="#FFFFFF", padding=ft.Padding.symmetric(horizontal=6),
            content=ft.Row(spacing=4, vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.IconButton(icon=ft.Icons.ARROW_BACK, tooltip="Voltar à agenda", on_click=voltar_agenda),
                    ft.Column(spacing=0, expand=True,
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            ft.Text("Semana inteira", size=15, weight=ft.FontWeight.BOLD, color="#25334E"),
                            ft.Text(f"{semana_atual[0]:%d/%m} – {(semana_atual[0] + timedelta(days=6)):%d/%m/%Y}",
                                    size=10, color="#738096"),
                        ]),
                    ft.IconButton(icon=ft.Icons.CHEVRON_LEFT, tooltip="Semana anterior",
                                  on_click=lambda e: mudar_semana(-1)),
                    ft.IconButton(icon=ft.Icons.CHEVRON_RIGHT, tooltip="Próxima semana",
                                  on_click=lambda e: mudar_semana(1)),
                ]),
        )
        raiz.controls = [ft.Container(
            expand=True, bgcolor="#FFFFFF",
            content=ft.Column(expand=True, spacing=0, controls=[
                barra,
                ft.Container(padding=ft.Padding.symmetric(horizontal=4, vertical=1),
                             content=tabela),
            ]),
        )]

    return desenhar_visao_completa
