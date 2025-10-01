import csv
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.text import slugify
from guia.models import MacroEixo, Eixo, Procedimento

REQUIRED = ["macro_eixo", "eixo", "titulo"]

CSV_TO_MODEL_MAP = {
    "gerencia": "gerencia",
    "setor_responsavel": "setor_responsavel",
    "slug": "slug",
    "o_que_e": "o_que_e",
    "para_quem": "para_quem",
    "documentos_necessarios": "documentos_necessarios",
    "como_solicitar": "como_solicitar",
    "prazos": "prazos",
    "base_legal": "base_legal",
    "observacoes": "observacoes",
    "link_sei": "link_sei",
    "ativo": "ativo",
}

class Command(BaseCommand):
    help = "Importa/atualiza Procedimentos (cria MacroEixos/Eixos se necessário)."

    def add_arguments(self, parser):
        parser.add_argument("csv_path", type=str, help="Caminho do CSV")
        parser.add_argument("--update", action="store_true", help="Atualiza existentes (match por slug; senão por título)")
        parser.add_argument("--dry-run", action="store_true", help="Não grava, só mostra o que faria")

    def handle(self, *args, **opts):
        csv_path = Path(opts["csv_path"])
        if not csv_path.exists():
            raise CommandError(f"Arquivo não encontrado: {csv_path}")
        update = opts["update"]
        dry = opts["dry_run"]

        created_macro = created_eixo = created_proc = updated_proc = skipped = 0

        with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            miss = [c for c in REQUIRED if c not in reader.fieldnames]
            if miss:
                raise CommandError(f"CSV faltando colunas obrigatórias: {miss}")

            @transaction.atomic
            def process():
                nonlocal created_macro, created_eixo, created_proc, updated_proc, skipped
                for i, row in enumerate(reader, start=2):
                    macro_name = (row.get("macro_eixo") or "").strip()
                    eixo_name = (row.get("eixo") or "").strip()
                    titulo = (row.get("titulo") or "").strip()
                    if not (macro_name and eixo_name and titulo):
                        self.stdout.write(self.style.WARNING(f"[linha {i}] faltam macro_eixo/eixo/titulo → skip"))
                        skipped += 1
                        continue

                    macro, m_created = MacroEixo.objects.get_or_create(nome=macro_name)
                    if m_created: created_macro += 1

                    eixo, e_created = Eixo.objects.get_or_create(macro=macro, nome=eixo_name)
                    if e_created: created_eixo += 1

                    slug_val = (row.get("slug") or "").strip() or slugify(titulo)
                    proc_qs = Procedimento.objects.filter(slug=slug_val)
                    if not proc_qs.exists():
                        proc_qs = Procedimento.objects.filter(titulo=titulo)

                    if proc_qs.exists():
                        if update:
                            proc = proc_qs.first()
                            self._apply(proc, row, eixo)
                            proc.slug = slug_val or proc.slug or slugify(proc.titulo)
                            proc.save()
                            updated_proc += 1
                        else:
                            skipped += 1
                            self.stdout.write(self.style.WARNING(
                                f"[linha {i}] já existe '{titulo}' (slug={slug_val}) → use --update"))
                    else:
                        proc = Procedimento(eixo=eixo, titulo=titulo, slug=slug_val)
                        self._apply(proc, row, eixo)
                        proc.save()
                        created_proc += 1

            if dry:
                self.stdout.write(self.style.NOTICE("⚠️ DRY-RUN: nenhuma alteração será gravada."))
                try:
                    with transaction.atomic():
                        process()
                        raise RuntimeError("DRY-RUN rollback")
                except RuntimeError:
                    pass
            else:
                process()

        self.stdout.write(self.style.SUCCESS(
            f"OK: macro+{created_macro}, eixos+{created_eixo}, proc+{created_proc}, upd={updated_proc}, skip={skipped}"
        ))

    def _apply(self, proc, row, eixo):
        proc.eixo = eixo
        # campos simples
        for csv_key, model_attr in CSV_TO_MODEL_MAP.items():
            val = row.get(csv_key)
            if val is None:
                continue
            val = val.strip()
            if model_attr == "ativo":
                setattr(proc, model_attr, val.lower() in ("1", "true", "sim", "yes"))
            else:
                setattr(proc, model_attr, val)
