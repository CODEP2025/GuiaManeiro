# guia/views.py
from django.db.models import Q, Max
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.contrib.staticfiles import finders

from .models import Eixo, Procedimento

# -------- HOME --------
def home(request):
    q = (request.GET.get("q") or "").strip()
    eixo_id = request.GET.get("eixo") or ""
    searched = ("eixo" in request.GET) or ("q" in request.GET)

    base_qs = (
        Procedimento.objects.filter(ativo=True)
        .select_related("eixo", "eixo__macro")
        .order_by("eixo__ordem", "titulo")
    )

    procedimentos = base_qs
    if q:
        procedimentos = procedimentos.filter(
            Q(titulo__icontains=q)
            | Q(gerencia__icontains=q)
            | Q(setor_responsavel__icontains=q)
            | Q(o_que_e__icontains=q)
            | Q(para_quem__icontains=q)
            | Q(documentos_necessarios__icontains=q)
            | Q(como_solicitar__icontains=q)
            | Q(prazos__icontains=q)
            | Q(base_legal__icontains=q)
            | Q(observacoes__icontains=q)
        )

    show_results = False
    if searched and (q or eixo_id.isdigit()):
        show_results = True
        if eixo_id.isdigit():
            procedimentos = procedimentos.filter(eixo_id=int(eixo_id))
    else:
        procedimentos = procedimentos.none()

    eixos = Eixo.objects.order_by("ordem", "nome")
    last_updated = base_qs.aggregate(m=Max("atualizado_em"))["m"]

    return render(request, "guia/home.html", {
        "q": q,
        "eixo_id": eixo_id,
        "eixos": eixos,
        "procedimentos": procedimentos,
        "total": procedimentos.count(),
        "show_results": show_results,
        "last_updated": last_updated,
    })

# -------- DETALHE --------
def procedimento_detail(request, slug):
    obj = get_object_or_404(
        Procedimento.objects.select_related("eixo", "eixo__macro"),
        slug=slug, ativo=True
    )
    faqs = obj.faqs.filter(ativo=True).order_by("ordem") if hasattr(obj, "faqs") else []
    return render(request, "guia/procedimento_detail.html", {"object": obj, "faqs": faqs})

# -------- PDF (import preguiçoso) --------
def _link_callback(uri, rel):
    result = finders.find(uri)
    if result:
        if isinstance(result, (list, tuple)):
            result = result[0]
        return result
    return uri

def procedimento_pdf(request, slug):
    try:
        from xhtml2pdf import pisa  # só importa se a rota for chamada
    except ImportError:
        return HttpResponse("Geração de PDF indisponível (instale xhtml2pdf==0.2.13).", status=503)

    obj = get_object_or_404(
        Procedimento.objects.select_related("eixo", "eixo__macro"),
        slug=slug, ativo=True
    )
    faqs = obj.faqs.filter(ativo=True).order_by("ordem") if hasattr(obj, "faqs") else []
    html = render_to_string("guia/procedimento_pdf.html", {"object": obj, "faqs": faqs})

    resp = HttpResponse(content_type="application/pdf")
    resp["Content-Disposition"] = f'inline; filename="{obj.slug}.pdf"'
    pisa.CreatePDF(src=html, dest=resp, link_callback=_link_callback)
    return resp
