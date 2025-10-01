from django.db import models
from django.utils.text import slugify

class MacroEixo(models.Model):
    """
    Quatro grandes eixos para navegação:
    - Benefícios e Direitos
    - Licenças e Afastamentos
    - Carreira
    - Movimentação Funcional
    """
    nome = models.CharField(max_length=120, unique=True)
    ordem = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["ordem", "nome"]

    def __str__(self):
        return self.nome


class Eixo(models.Model):
    """Eixo (opcionalmente subordinado a um MacroEixo)."""
    macro = models.ForeignKey(MacroEixo, on_delete=models.PROTECT, related_name="eixos")
    nome = models.CharField(max_length=150, unique=True)
    ordem = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["macro__ordem", "ordem", "nome"]

    def __str__(self):
        return self.nome


class Procedimento(models.Model):
    eixo = models.ForeignKey(Eixo, on_delete=models.PROTECT, related_name="procedimentos")
    titulo = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=220, unique=True, blank=True)

    # Novos campos pedidos:
    gerencia = models.CharField(max_length=150, blank=True)            # ex.: GGP, GDP, CODEP, etc. (vide Guia)  # :contentReference[oaicite:2]{index=2}
    setor_responsavel = models.CharField(max_length=200, blank=True)    # ex.: SUREF, SUAPO, SUPEN, COICP...       # :contentReference[oaicite:3]{index=3}

    # Blocos de conteúdo (Manual 2017):
    o_que_e = models.TextField(blank=True)                              # :contentReference[oaicite:4]{index=4}
    para_quem = models.TextField(blank=True)                            # :contentReference[oaicite:5]{index=5}
    documentos_necessarios = models.TextField(blank=True)               # :contentReference[oaicite:6]{index=6}
    como_solicitar = models.TextField(blank=True)                       # Procedimentos (passo a passo)            # :contentReference[oaicite:7]{index=7}
    prazos = models.TextField(blank=True)
    base_legal = models.TextField(blank=True)                           # :contentReference[oaicite:8]{index=8}
    observacoes = models.TextField(blank=True)                          # :contentReference[oaicite:9]{index=9}

    link_sei = models.URLField(blank=True)
    ativo = models.BooleanField(default=True)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["eixo__macro__ordem", "eixo__ordem", "titulo"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titulo)[:220]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.titulo
from django.db import models

# ... seus modelos MacroEixo, Eixo, Procedimento já existentes acima ...

class PerguntaFrequente(models.Model):
    procedimento = models.ForeignKey(
        "Procedimento",
        on_delete=models.CASCADE,
        related_name="faqs"
    )
    pergunta = models.CharField("Pergunta", max_length=255)
    resposta = models.TextField("Resposta")
    ordem = models.PositiveIntegerField(default=0)
    ativo = models.BooleanField(default=True)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["ordem", "id"]
        verbose_name = "Pergunta frequente"
        verbose_name_plural = "Perguntas frequentes"

    def __str__(self):
        return self.pergunta
