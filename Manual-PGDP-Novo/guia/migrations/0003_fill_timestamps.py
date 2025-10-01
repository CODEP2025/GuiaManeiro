from django.db import migrations
from django.utils import timezone

def set_default_timestamps(apps, schema_editor):
    Procedimento = apps.get_model("guia", "Procedimento")
    now = timezone.now()
    for proc in Procedimento.objects.all():
        if not proc.criado_em:
            proc.criado_em = now
        if not proc.atualizado_em:
            proc.atualizado_em = now
        proc.save(update_fields=["criado_em", "atualizado_em"])

class Migration(migrations.Migration):

    dependencies = [
        ("guia", "0002_macroeixo_alter_eixo_options_and_more"),  # ajuste para a última migração antes desta
    ]

    operations = [
        migrations.RunPython(set_default_timestamps, reverse_code=migrations.RunPython.noop),
    ]
