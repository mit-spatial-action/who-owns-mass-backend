from django.db import migrations, models
import django.db.models.deletion

def forwards_func(apps, schema_editor):
    Filings = apps.get_model("mass_evictions", "Filings")
    Attorneys = apps.get_model("mass_evictions", "Attorneys")
    for filing in Filings.objects.all():
        if filing.ptf_bar:
            attorney, _ = Attorneys.objects.get_or_create(bar=filing.ptf_bar)
            filing.ptf_bar_fk = attorney
        if filing.def_bar:
            attorney, _ = Attorneys.objects.get_or_create(bar=filing.def_bar)
            filing.def_bar_fk = attorney
        filing.save()

def reverse_func(apps, schema_editor):
    Filings = apps.get_model("mass_evictions", "Filings")
    for filing in Filings.objects.all():
        filing.ptf_bar_fk = None
        filing.def_bar_fk = None
        filing.save()

class Migration(migrations.Migration):

    dependencies = [
        ('mass_evictions', '0002_delete_spatialrefsys_alter_attorneys_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='filings',
            name='def_bar_fk',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='defendant_attorney', to='mass_evictions.attorneys'),
        ),
        migrations.AddField(
            model_name='filings',
            name='ptf_bar_fk',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='plaintiff_attorney', to='mass_evictions.attorneys'),
        ),
        migrations.AlterUniqueTogether(
            name='defendants',
            unique_together={('docket', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='docket',
            unique_together={('docket', 'date', 'text')},
        ),
        migrations.AlterUniqueTogether(
            name='events',
            unique_together={('docket', 'date', 'locality', 'location', 'result', 'session', 'type')},
        ),
        migrations.AlterUniqueTogether(
            name='judgments',
            unique_together={('docket', 'date', 'type', 'method', 'for_field', 'against')},
        ),
        migrations.AlterUniqueTogether(
            name='plaintiffs',
            unique_together={('docket', 'name')},
        ),
        migrations.RunPython(forwards_func, reverse_func)
    ]
