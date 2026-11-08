"""Funções utilitárias de datas e horários."""
from datetime import timedelta
import flet as ft
from config import PRIMEIRO_HORARIO, ULTIMO_HORARIO, INTERVALO

def horario(minutos):
    return f"{minutos // 60:02d}:{minutos % 60:02d}"

def segunda(d):
    return d - timedelta(days=d.weekday())

def opcoes_horario(incluir_24=False):
    fim = ULTIMO_HORARIO + (INTERVALO if incluir_24 else 0)
    inicio = PRIMEIRO_HORARIO + (INTERVALO if incluir_24 else 0)
    return [ft.DropdownOption(key=str(m), text=horario(m)) for m in range(inicio, fim, INTERVALO)]

