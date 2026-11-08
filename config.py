"""Constantes de layout, cores e horário do aplicativo."""
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
# Contraste da grade: faixas de meia hora e divisões de horas cheias.
COR_LINHA_MEIA_HORA = "#CBD5E4"
COR_LINHA_HORA_CHEIA = "#9CAEC6"
COR_DIVISAO_DIAS = "#CFD8E6"
