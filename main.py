"""Organizador semanal - Flet + SQLite. Execute com: python main.py"""
from __future__ import annotations

import os
import sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path

import flet as ft

APP_DIR = Path(os.environ.get("FLET_APP_STORAGE_DATA") or (Path.home() / ".organizador_semanal"))
APP_DIR.mkdir(parents=True, exist_ok=True)
DB_FILE = APP_DIR / "tarefas.db"
DIAS = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
# (fundo da atividade, texto, borda); nomes antigos preservados no banco.
CORES = {
    "Azul": ("#E6F0FF", "#2456A6", "#4A83DF"),
    "Verde": ("#E3F5E9", "#217447", "#40A773"),
    "Roxo": ("#EEE8FF", "#6241A2", "#8D6AD3"),
    "Laranja": ("#FFF0DC", "#9B5A12", "#E5A34B"),
    "Rosa": ("#FFE8F0", "#A83E68", "#E77CA2"),
    "Lavanda": ("#F3ECFF", "#6C4B92", "#A88BE2"),
    "Lilás": ("#F5E8FA", "#864795", "#C183D1"),
    "Violeta": ("#EDE6FB", "#59358D", "#8961CB"),
    "Coral": ("#FFEAE5", "#A7473B", "#EB8270"),
    "Pêssego": ("#FFF0E8", "#A4673C", "#F2A57F"),
    "Salmão": ("#FCE9E7", "#984C57", "#D9838A"),
    "Vermelho": ("#FFE6E6", "#A32B39", "#DD5D67"),
    "Amarelo": ("#FFF8D9", "#806118", "#DAB949"),
    "Mostarda": ("#FFF1CE", "#876111", "#CA9D30"),
    "Menta": ("#E4F8F1", "#246D59", "#64BDA1"),
    "Turquesa": ("#DFF7F5", "#1C7175", "#42B2B7"),
    "Ciano": ("#E1F6FC", "#246B81", "#54AFCE"),
    "Azul-marinho": ("#E6ECF6", "#344E76", "#6985B4"),
    "Oliva": ("#EDF1DE", "#5C6A33", "#9BAC5A"),
    "Cinza": ("#EDF0F4", "#526072", "#8B98A9"),
}
PRIMEIRO_HORARIO = 7 * 60
ULTIMO_HORARIO = 24 * 60
INTERVALO = 30
SLOT_HEIGHT = 44
DAY_WIDTH = 165
TIME_WIDTH = 62


def conectar():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("""CREATE TABLE IF NOT EXISTS tarefas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dia TEXT NOT NULL,
        inicio INTEGER NOT NULL,
        fim INTEGER NOT NULL,
        titulo TEXT NOT NULL,
        descricao TEXT NOT NULL DEFAULT '',
        cor TEXT NOT NULL DEFAULT 'Azul',
        concluida INTEGER NOT NULL DEFAULT 0,
        CHECK (inicio >= 0 AND fim <= 1440 AND inicio < fim)
    )""")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_tarefas_dia ON tarefas(dia, inicio)")
    conn.commit()
    return conn


def horario(minutos):
    return f"{minutos // 60:02d}:{minutos % 60:02d}"


def segunda(d):
    return d - timedelta(days=d.weekday())


def opcoes_horario(incluir_24=False):
    fim = ULTIMO_HORARIO + (INTERVALO if incluir_24 else 0)
    inicio = PRIMEIRO_HORARIO + (INTERVALO if incluir_24 else 0)
    return [ft.DropdownOption(key=str(m), text=horario(m)) for m in range(inicio, fim, INTERVALO)]


def main(page: ft.Page):
    db = conectar()
    page.title = "Minha Semana | Organizador"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#F6F8FC"
    page.padding = 0
    page.window.min_width = 350
    page.window.min_height = 500
    page.theme = ft.Theme(color_scheme_seed="#5277D8")

    semana_atual = [segunda(date.today())]
    titulo_periodo = ft.Text(size=17, weight=ft.FontWeight.BOLD, color="#26334D")
    resumo = ft.Text(size=12, color="#6D7890")
    grade = ft.Column(spacing=0, expand=True)
    raiz = ft.Column(expand=True, spacing=0)
    hoje = date.today()
    modo_resumo = [False]
    # O topo da agenda é recolhido ao percorrer os horários e reaparece no início.
    topo_recolhido = [False]

    def carregar():
        inicio = semana_atual[0].isoformat()
        fim = (semana_atual[0] + timedelta(days=6)).isoformat()
        return [dict(x) for x in db.execute(
            "SELECT * FROM tarefas WHERE dia BETWEEN ? AND ? ORDER BY dia, inicio", (inicio, fim)
        ).fetchall()]

    def aviso(msg):
        page.show_dialog(ft.SnackBar(content=ft.Text(msg), duration=2600))

    def fechar(dialogo):
        page.pop_dialog()

    def editar(tarefa=None, dia=None, inicio=540):
        # A mesma janela atende inclusão e edição de qualquer tarefa.
        d = date.fromisoformat(tarefa["dia"]) if tarefa else (dia or hoje)
        comeco = tarefa["inicio"] if tarefa else max(PRIMEIRO_HORARIO, inicio)
        termino = tarefa["fim"] if tarefa else min(1440, inicio + 30)
        titulo = ft.TextField(label="Nome da atividade *", value=tarefa["titulo"] if tarefa else "", autofocus=True)
        descricao = ft.TextField(label="Observações (opcional)", value=tarefa["descricao"] if tarefa else "", multiline=True, min_lines=2, max_lines=3)
        campo_dia = ft.Dropdown(label="Dia", value=d.isoformat(), options=[
            ft.DropdownOption(key=(semana_atual[0] + timedelta(days=i)).isoformat(),
                              text=f"{DIAS[i]} · {(semana_atual[0] + timedelta(days=i)):%d/%m}")
            for i in range(7)
        ])
        op_inicio = opcoes_horario()
        op_fim = opcoes_horario(True)
        # Permite editar compromissos antigos criados antes das 07h, sem apagá-los.
        if comeco < PRIMEIRO_HORARIO:
            op_inicio.insert(0, ft.DropdownOption(key=str(comeco), text=horario(comeco) + " (antigo)"))
        if termino < PRIMEIRO_HORARIO + INTERVALO:
            op_fim.insert(0, ft.DropdownOption(key=str(termino), text=horario(termino) + " (antigo)"))
        campo_inicio = ft.Dropdown(label="Início", value=str(comeco), options=op_inicio)
        campo_fim = ft.Dropdown(label="Fim", value=str(termino), options=op_fim)
        campo_cor = ft.Dropdown(label="Cor (20 opções)", value=tarefa["cor"] if tarefa else "Azul", options=[
            ft.DropdownOption(key=k, text=k) for k in CORES
        ])
        amostra_cor = ft.Container(width=40, height=24, border_radius=7,
                                  bgcolor=CORES.get(campo_cor.value, CORES["Azul"])[2])

        def mudar_cor(e):
            amostra_cor.bgcolor = CORES.get(campo_cor.value, CORES["Azul"])[2]
            amostra_cor.update()

        campo_cor.on_select = mudar_cor
        concluida = ft.Checkbox(label="Atividade concluída", value=bool(tarefa["concluida"]) if tarefa else False)
        erro = ft.Text(color="#BA3341", size=12)

        def salvar(e):
            nome = (titulo.value or "").strip()
            a, b = int(campo_inicio.value), int(campo_fim.value)
            if not nome:
                erro.value = "Informe o nome da atividade."
            elif b <= a:
                erro.value = "O horário final precisa ser posterior ao inicial."
            elif (a < PRIMEIRO_HORARIO or b > ULTIMO_HORARIO) and not (tarefa and a == tarefa["inicio"] and b == tarefa["fim"]):
                erro.value = "Use horários entre 07:00 e 24:00."
            else:
                conflito = db.execute(
                    "SELECT id FROM tarefas WHERE dia=? AND inicio < ? AND fim > ? AND id != ? LIMIT 1",
                    (campo_dia.value, b, a, tarefa["id"] if tarefa else -1),
                ).fetchone()
                if conflito:
                    erro.value = "Já existe uma atividade nesse intervalo. Escolha outro horário."
                else:
                    dados = (campo_dia.value, a, b, nome, descricao.value or "", campo_cor.value, int(bool(concluida.value)))
                    with db:
                        if tarefa:
                            db.execute("""UPDATE tarefas SET dia=?, inicio=?, fim=?, titulo=?, descricao=?,
                                       cor=?, concluida=? WHERE id=?""", (*dados, tarefa["id"]))
                        else:
                            db.execute("""INSERT INTO tarefas (dia, inicio, fim, titulo, descricao, cor, concluida)
                                       VALUES (?, ?, ?, ?, ?, ?, ?)""", dados)
                    fechar(dialogo)
                    desenhar()
                    return
            erro.update()

        def confirmar_exclusao(e):
            fechar(dialogo)
            def excluir(e):
                with db:
                    db.execute("DELETE FROM tarefas WHERE id=?", (tarefa["id"],))
                fechar(confirma)
                desenhar()
            confirma = ft.AlertDialog(
                modal=True, title=ft.Text("Excluir atividade?"),
                content=ft.Text(f"“{tarefa['titulo']}” será excluída permanentemente."),
                actions=[ft.TextButton("Cancelar", on_click=lambda e: fechar(confirma)),
                         ft.Button("Excluir", on_click=excluir)],
            )
            page.show_dialog(confirma)

        botoes = [ft.TextButton("Cancelar", on_click=lambda e: fechar(dialogo))]
        if tarefa:
            botoes.append(ft.TextButton("Excluir", on_click=confirmar_exclusao))
        botoes.append(ft.Button("Salvar atividade", icon=ft.Icons.CHECK, on_click=salvar))
        dialogo = ft.AlertDialog(
            modal=True, title=ft.Text("Editar atividade" if tarefa else "Nova atividade", weight=ft.FontWeight.BOLD),
            content=ft.Container(width=410, content=ft.Column(
                controls=[titulo, campo_dia,
                          ft.Row([ft.Container(content=campo_inicio, expand=True), ft.Container(content=campo_fim, expand=True)]),
                          ft.Row([ft.Container(content=campo_cor, expand=True), amostra_cor]),
                          descricao, concluida, erro],
                tight=True, spacing=11, scroll=ft.ScrollMode.AUTO,
            )),
            actions=botoes,
        )
        page.show_dialog(dialogo)

    def mudar_semana(delta):
        semana_atual[0] += timedelta(days=7 * delta)
        desenhar()

    def ir_hoje(e):
        semana_atual[0] = segunda(date.today())
        desenhar()

    def celula_vazia(d, minuto):
        return ft.Container(
            height=SLOT_HEIGHT, width=DAY_WIDTH,
            bgcolor="#FFFFFF" if minuto % 60 else "#FBFCFF",
            border=ft.Border(bottom=ft.BorderSide(1, "#ECF0F6")),
            ink=True, on_click=lambda e, dd=d, mm=minuto: editar(dia=dd, inicio=mm),
            content=ft.Row(
                controls=[ft.Icon(ft.Icons.ADD, size=13, color="#CBD3E1")],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        )

    def bloco_tarefa(t, vis_inicio, vis_fim):
        bg, cor_texto, detalhe = CORES.get(t["cor"], CORES["Azul"])
        altura = ((vis_fim - vis_inicio) // INTERVALO) * SLOT_HEIGHT
        concluida = bool(t["concluida"])
        return ft.Container(
            width=DAY_WIDTH, height=altura,
            bgcolor=bg, border=ft.Border(
                left=ft.BorderSide(4, detalhe), bottom=ft.BorderSide(2, "#FFFFFF")
            ), border_radius=5, padding=ft.Padding.symmetric(horizontal=8, vertical=5),
            ink=True, on_click=lambda e, tarefa=t: editar(tarefa=tarefa),
            content=ft.Column(spacing=2, controls=[
                ft.Text(("✓ " if concluida else "") + t["titulo"], size=12, weight=ft.FontWeight.W_600,
                        color=cor_texto, max_lines=max(1, min(4, int(altura / 22) - 1)),
                        overflow=ft.TextOverflow.ELLIPSIS),
                ft.Text(f"{horario(t['inicio'])}–{horario(t['fim'])}", size=10, color=cor_texto),
            ]),
            tooltip="Clique para editar ou excluir",
        )

    def cabecalho_dia(indice):
        d = semana_atual[0] + timedelta(days=indice)
        destaque = d == date.today()
        return ft.Container(
            height=65, width=DAY_WIDTH, alignment=ft.Alignment.CENTER,
            bgcolor="#E6EEFF" if destaque else "#FFFFFF",
            border=ft.Border(bottom=ft.BorderSide(1, "#E8EDF5")),
            content=ft.Column(
                spacing=2, alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[ft.Text(DIAS[indice], size=12, weight=ft.FontWeight.W_500, color="#64718C"),
                          ft.Text(f"{d:%d/%m}", size=16, weight=ft.FontWeight.BOLD,
                                  color="#315FC2" if destaque else "#25334E")],
            ),
        )

    def coluna_dia(indice, tarefas):
        d = semana_atual[0] + timedelta(days=indice)
        do_dia = sorted(
            (x for x in tarefas if x["dia"] == d.isoformat()
             and x["fim"] > PRIMEIRO_HORARIO and x["inicio"] < ULTIMO_HORARIO),
            key=lambda x: x["inicio"],
        )
        # Tarefas antigas que atravessam as 07h permanecem visíveis, mas
        # apenas sua parte dentro da grade será desenhada.
        por_inicio = {max(PRIMEIRO_HORARIO, x["inicio"]): x for x in do_dia}
        conteudo = []
        minuto = PRIMEIRO_HORARIO
        while minuto < ULTIMO_HORARIO:
            t = por_inicio.get(minuto)
            if t:
                vis_fim = min(ULTIMO_HORARIO, t["fim"])
                conteudo.append(bloco_tarefa(t, minuto, vis_fim))
                minuto = vis_fim
            else:
                conteudo.append(celula_vazia(d, minuto))
                minuto += INTERVALO
        return ft.Column(spacing=0, width=DAY_WIDTH, controls=conteudo)

    def abrir_visao_completa(e):
        modo_resumo[0] = True
        desenhar()

    def voltar_agenda(e):
        modo_resumo[0] = False
        topo_recolhido[0] = False
        desenhar()

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

    def desenhar():
        tarefas = carregar()
        ultima = semana_atual[0] + timedelta(days=6)
        titulo_periodo.value = f"{semana_atual[0]:%d/%m/%Y}  —  {ultima:%d/%m/%Y}"
        horas = sum(t["fim"] - t["inicio"] for t in tarefas) / 60
        resumo.value = f"{len(tarefas)} atividades nesta semana  ·  {horas:g} h planejadas  ·  toque num espaço livre para adicionar"

        if modo_resumo[0]:
            desenhar_visao_completa(tarefas)
            page.update()
            return

        regua = ft.Column(spacing=0, width=TIME_WIDTH, controls=[
            ft.Container(height=SLOT_HEIGHT, width=TIME_WIDTH,
                         alignment=ft.Alignment.TOP_CENTER,
                         content=ft.Text(horario(m), size=11,
                                         color="#44516D" if (m // 30) % 2 == 0 else "#748099"))
            for m in range(PRIMEIRO_HORARIO, ULTIMO_HORARIO, INTERVALO)
        ])
        # V8: uma ÚNICA rolagem vertical para a régua e as atividades.
        # A régua continua fixa horizontalmente porque não participa da
        # rolagem horizontal dos dias, mas rola no mesmo fluxo vertical.
        # Isso elimina o atraso causado por scroll_to() a cada gesto.
        largura_dias = 7 * DAY_WIDTH + 6
        cabecalhos = ft.Row(spacing=1, controls=[cabecalho_dia(i) for i in range(7)])
        corpo = ft.Row(
            spacing=1, vertical_alignment=ft.CrossAxisAlignment.START,
            controls=[coluna_dia(i, tarefas) for i in range(7)],
        )

        # Somente a rolagem HORIZONTAL do corpo precisa atualizar o topo.
        # A rolagem VERTICAL, que precisa de alinhamento perfeito, é nativa
        # e compartilhada entre régua e células, sem callbacks de sincronização.
        topo_dias = ft.Row(
            expand=True, spacing=0, scroll=ft.ScrollMode.HIDDEN,
            controls=[ft.Container(width=largura_dias, content=cabecalhos)],
        )

        async def acompanhar_horizontal(e):
            try:
                pixels = float(e.pixels)
            except (ValueError, TypeError, AttributeError):
                return
            await topo_dias.scroll_to(offset=max(0, pixels), duration=0)

        corpo_dias = ft.Row(
            expand=True, spacing=0, scroll=ft.ScrollMode.AUTO,
            scroll_interval=5, on_scroll=acompanhar_horizontal,
            controls=[ft.Container(width=largura_dias, content=corpo)],
        )

        # Cabeçalho dos dias: fora da rolagem vertical, permanece no topo.
        topo_grade = ft.Row(spacing=0, controls=[
            ft.Container(
                width=TIME_WIDTH, height=65, bgcolor="#F6F8FC",
                alignment=ft.Alignment.CENTER,
                content=ft.Text("Hora", size=11, color="#64718C"),
            ),
            ft.Container(expand=True, height=65, content=topo_dias),
        ])

        async def acompanhar_rolagem(e):
            try:
                pixels = float(e.pixels)
            except (ValueError, TypeError, AttributeError):
                return
            recolher = pixels > 145 if not topo_recolhido[0] else pixels >= 55
            if recolher != topo_recolhido[0]:
                topo_recolhido[0] = recolher
                faixa_topo.height = 0 if recolher else None
                cab.opacity = 0 if recolher else 1
                faixa_topo.update()

        # RÉGUA E CORPO: filhos da mesma área de rolagem vertical.
        grade_vertical = ft.Column(
            expand=True, spacing=0, scroll=ft.ScrollMode.AUTO,
            scroll_interval=20, on_scroll=acompanhar_rolagem,
            controls=[ft.Row(
                spacing=0, vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    ft.Container(width=TIME_WIDTH, content=regua),
                    ft.Container(expand=True, content=corpo_dias),
                ],
            )],
        )
        grade.controls = [topo_grade, grade_vertical]
        faixa_topo.height = 0 if topo_recolhido[0] else None
        cab.opacity = 0 if topo_recolhido[0] else 1
        raiz.controls = [faixa_topo, grade]
        page.update()

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

    # SafeArea respeita automaticamente status bar, notch e barra de navegação.
    # A margem mínima adicional impede que botões encostem nesses elementos.
    page.add(ft.SafeArea(
        content=raiz,
        expand=True,
        minimum_padding=ft.Padding.only(top=10, bottom=3),
    ))
    # Recalcula a escala quando a orientação ou o tamanho da janela muda.
    def ao_redimensionar(e):
        if modo_resumo[0]:
            desenhar()
    page.on_resize = ao_redimensionar
    desenhar()


if __name__ == "__main__":
    ft.run(main)
