from django.contrib import admin
from .models import MacroEixo, Eixo, Procedimento, PerguntaFrequente

@admin.register(MacroEixo)
class MacroEixoAdmin(admin.ModelAdmin):
    list_display = ("nome", "ordem")
    ordering = ("ordem", "nome")

@admin.register(Eixo)
class EixoAdmin(admin.ModelAdmin):
    list_display = ("nome", "macro", "ordem")
    list_filter = ("macro",)
    ordering = ("macro__ordem", "ordem", "nome")

class FAQInline(admin.TabularInline):
    model = PerguntaFrequente
    extra = 1
    fields = ("pergunta", "resposta", "ordem", "ativo")
    show_change_link = True

@admin.register(Procedimento)
class ProcedimentoAdmin(admin.ModelAdmin):
    list_display = ("titulo", "eixo", "ativo")
    list_filter = ("ativo", "eixo__macro", "eixo")
    search_fields = ("titulo", "gerencia", "setor_responsavel", "o_que_e")
    prepopulated_fields = {"slug": ("titulo",)}
    inlines = [FAQInline]

@admin.register(PerguntaFrequente)
class PerguntaFrequenteAdmin(admin.ModelAdmin):
    list_display = ("pergunta", "procedimento", "ordem", "ativo")
    list_filter = ("ativo", "procedimento__eixo")
    search_fields = ("pergunta", "resposta")
    ordering = ("procedimento", "ordem")
