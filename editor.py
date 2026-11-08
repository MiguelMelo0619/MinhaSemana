"""Diálogo de criação, edição, exclusão e validações de tarefas."""
from datetime import date, timedelta
import flet as ft
from config import CORES, DIAS, PRIMEIRO_HORARIO, ULTIMO_HORARIO, INTERVALO
from horarios import horario, opcoes_horario

def criar_editor(page, db, semana_atual, hoje, redesenhar):
    """Cria a função de edição usando o estado compartilhado da tela."""
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
                    redesenhar()
                    return
            erro.update()

        def confirmar_exclusao(e):
            fechar(dialogo)
            def excluir(e):
                with db:
                    db.execute("DELETE FROM tarefas WHERE id=?", (tarefa["id"],))
                fechar(confirma)
                redesenhar()
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

    return editar
