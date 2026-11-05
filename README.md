# Minha Semana — organizador semanal (v1)

Aplicativo de planejamento semanal feito com Python, Flet e SQLite.

## Recursos
- Agenda de segunda-feira a domingo, das 00:00 às 24:00, em blocos de 30 minutos.
- Atividades de duração variável (ex.: 10:00 a 12:30).
- Clique em um horário vazio para criar a atividade.
- Clique numa atividade para editar título, dia, horários, observações, cor e status de conclusão ou excluí-la.
- Navegação entre semanas; os dados de cada data continuam salvos.
- Impede sobreposição de atividades no mesmo dia.
- Banco SQLite salvo automaticamente em `~/.organizador_semanal/tarefas.db`.
- Layout de 7 colunas com rolagem horizontal em telas pequenas.

## Rodar no Windows
Abra PowerShell na pasta do projeto:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

Se a ativação estiver bloqueada, use diretamente:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

## Dados
As tarefas são armazenadas no computador do usuário, independentemente da pasta do projeto. Fechar o programa não apaga o banco. Para fazer backup, copie `tarefas.db` com o aplicativo fechado.

## Limitações da v1
Não há recorrência automática, notificações nem sincronização entre aparelhos. Os dados permanecem locais ao dispositivo em que o aplicativo é executado.
