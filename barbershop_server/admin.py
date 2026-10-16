from django.contrib import admin
from barbershop_server.models import Agendamento  # Importa a tabela que criamos


# 🔑 CONFIGURAÇÃO LUXUOSA DO PAINEL DA RAINHA
class AgendamentoAdmin(admin.ModelAdmin):
    # Organiza o que vai aparecer listado em colunas chiques na tela
    list_display = ('id', 'cliente', 'servico', 'barbeiro', 'data', 'horario', 'pago')

    # Adiciona uma barra lateral de filtros rápidos para você clicar e filtrar por barbeiro ou se está pago!
    list_filter = ('barbeiro', 'pago', 'data')

    # Adiciona um campo de busca para você digitar o nome do cliente e achar o agendamento dele na hora!
    search_fields = ('cliente__username', 'servico')


# 🚀 Registra a tabela aplicando todo esse visual de mercado de alta tecnologia!
admin.site.register(Agendamento, AgendamentoAdmin)
