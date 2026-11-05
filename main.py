"""Organizador semanal - Flet + SQLite. Execute com: python main.py"""
from __future__ import annotations

import sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path

import flet as ft

APP_DIR = Path.home() / ".organizador_semanal"
APP_DIR.mkdir(parents=True, exist_ok=True)
DB_FILE = APP_DIR / "tarefas.db"
DIAS = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
CORES = {
    "Azul": ("#E6F0FF", "#2456A6", "#4A83DF"),
    "Verde": ("#E3F5E9", "#217447", "#40A773"),
    "Roxo": ("#EEE8FF", "#6241A2", "#8D6AD3"),
    "Laranja": ("#FFF0DC", "#9B5A12", "#E5A34B"),
    "Rosa": ("#FFE8F0", "#A83E68", "#E77CA2"),
}
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
    limite = 49 if incluir_24 else 48
    return [ft.DropdownOption(key=str(i * 30), text=horario(i * 30)) for i in range(limite)]


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
    grade = ft.Column(spacing=0, scroll=ft.ScrollMode.AUTO, expand=True)
    hoje = date.today()

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
        comeco = tarefa["inicio"] if tarefa else inicio
        termino = tarefa["fim"] if tarefa else min(1440, inicio + 30)
        titulo = ft.TextField(label="Nome da atividade *", value=tarefa["titulo"] if tarefa else "", autofocus=True)
        descricao = ft.TextField(label="Observações (opcional)", value=tarefa["descricao"] if tarefa else "", multiline=True, min_lines=2, max_lines=3)
        campo_dia = ft.Dropdown(label="Dia", value=d.isoformat(), options=[
            ft.DropdownOption(key=(semana_atual[0] + timedelta(days=i)).isoformat(),
                              text=f"{DIAS[i]} · {(semana_atual[0] + timedelta(days=i)):%d/%m}")
            for i in range(7)
        ])
        campo_inicio = ft.Dropdown(label="Início", value=str(comeco), options=opcoes_horario())
        campo_fim = ft.Dropdown(label="Fim", value=str(termino), options=opcoes_horario(True))
        campo_cor = ft.Dropdown(label="Cor", value=tarefa["cor"] if tarefa else "Azul", options=[
            ft.DropdownOption(key=k, text=k) for k in CORES
        ])
        concluida = ft.Checkbox(label="Atividade concluída", value=bool(tarefa["concluida"]) if tarefa else False)
        erro = ft.Text(color="#BA3341", size=12)

        def salvar(e):
            nome = (titulo.value or "").strip()
            a, b = int(campo_inicio.value), int(campo_fim.value)
            if not nome:
                erro.value = "Informe o nome da atividade."
            elif b <= a:
                erro.value = "O horário final precisa ser posterior ao inicial."
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
                          campo_cor, descricao, concluida, erro],
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

    def bloco_tarefa(t):
        bg, cor_texto, detalhe = CORES.get(t["cor"], CORES["Azul"])
        altura = ((t["fim"] - t["inicio"]) // 30) * SLOT_HEIGHT
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

    def coluna_dia(indice, tarefas):
        d = semana_atual[0] + timedelta(days=indice)
        do_dia = sorted((x for x in tarefas if x["dia"] == d.isoformat()), key=lambda x: x["inicio"])
        por_inicio = {x["inicio"]: x for x in do_dia}
        conteudo = []
        slot = 0
        while slot < 48:
            minuto = slot * 30
            if minuto in por_inicio:
                t = por_inicio[minuto]
                conteudo.append(bloco_tarefa(t))
                slot += (t["fim"] - t["inicio"]) // 30
            else:
                conteudo.append(celula_vazia(d, minuto))
                slot += 1
        destaque = d == date.today()
        cabecalho = ft.Container(
            height=65, width=DAY_WIDTH, alignment=ft.Alignment.CENTER,
            bgcolor="#E6EEFF" if destaque else "#FFFFFF",
            border=ft.Border(bottom=ft.BorderSide(1, "#E8EDF5")),
            content=ft.Column(
                spacing=2, alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[ft.Text(DIAS[indice], size=12, weight=ft.FontWeight.W_500, color="#64718C"),
                          ft.Text(f"{d:%d/%m}", size=16, weight=ft.FontWeight.BOLD, color="#315FC2" if destaque else "#25334E")]
            ),
        )
        return ft.Column(spacing=0, controls=[cabecalho, *conteudo])

    def desenhar():
        tarefas = carregar()
        ultima = semana_atual[0] + timedelta(days=6)
        titulo_periodo.value = f"{semana_atual[0]:%d/%m/%Y}  —  {ultima:%d/%m/%Y}"
        horas = sum(t["fim"] - t["inicio"] for t in tarefas) / 60
        resumo.value = f"{len(tarefas)} atividades nesta semana  ·  {horas:g} h planejadas  ·  clique num espaço livre para adicionar"
        regua = ft.Column(spacing=0, controls=[
            ft.Container(height=65, width=TIME_WIDTH, bgcolor="#F6F8FC"),
            *[ft.Container(height=SLOT_HEIGHT, width=TIME_WIDTH,
                           alignment=ft.Alignment.TOP_CENTER,
                           content=ft.Text(horario(i * 30), size=11, color="#748099" if i % 2 else "#44516D"))
              for i in range(48)]
        ])
        calendario = ft.Row(spacing=1, vertical_alignment=ft.CrossAxisAlignment.START,
                           controls=[regua] + [coluna_dia(i, tarefas) for i in range(7)],
                           scroll=ft.ScrollMode.AUTO)
        grade.controls = [calendario]
        page.update()

    cab = ft.Container(
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
                titulo_periodo,
            ]),
            resumo,
        ]),
    )
    page.add(ft.Column(expand=True, spacing=0, controls=[cab, grade]))
    desenhar()


if __name__ == "__main__":
    ft.run(main)
