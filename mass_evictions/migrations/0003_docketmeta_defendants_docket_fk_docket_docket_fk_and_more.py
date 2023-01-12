from django.db import migrations, models
import django.db.models.deletion

def get_or_create_docketmeta(apps, docket, log=False, model=""):
    DocketMeta = apps.get_model("mass_evictions", "DocketMeta")
    Docket = apps.get_model("mass_evictions", "Docket")
    DocketOrphans = apps.get_model("mass_evictions", "DocketOrphans")

    docketmeta, created = DocketMeta.objects.get_or_create(docket=docket)
   
    if created and log:
        if model != "Docket":
            try:
                Docket.objects.get(docket=docket)
            except:
                DocketOrphans.objects.create(docket=docket, originator_model=model)
    return docketmeta

def forwards_func(apps, schema_editor):
    Docket = apps.get_model("mass_evictions", "Docket")
    DocketMeta = apps.get_model("mass_evictions", "DocketMeta")
    Defendants = apps.get_model("mass_evictions", "Defendants")
    Events = apps.get_model("mass_evictions", "Events")
    Filings = apps.get_model("mass_evictions", "Filings")
    Judgments = apps.get_model("mass_evictions", "Judgments")
    Plaintiffs = apps.get_model("mass_evictions", "Plaintiffs")
    
    for docket in Docket.objects.all():
        try:
            docketmeta, _ = DocketMeta.objects.get_or_create(docket=docket.docket)
            docket.docket_fk = docketmeta
            docket.save()
        except Exception as err:
            breakpoint()

    print("Setting dockets for Defendants")
    for defendant in Defendants.objects.all():
        docketmeta = get_or_create_docketmeta(apps, defendant.docket, log=True, model="Defendants")
        defendant.docket_fk = docketmeta
        defendant.save()

    print("Setting dockets for Events")
    for event in Events.objects.all():
        docketmeta = get_or_create_docketmeta(apps, event.docket, log=True, model="Events")
        event.docket_fk = docketmeta
        event.save()

    print("Setting dockets for Filings")
    for filing in Filings.objects.all():
        docketmeta = get_or_create_docketmeta(apps, filing.docket, log=True, model="Filings")
        filing.docket_fk = docketmeta
        filing.save()  

    print("Setting dockets for Judgments")
    for judgment in Judgments.objects.all():
        docketmeta = get_or_create_docketmeta(apps, judgment.docket, log=True, model="Judgments")
        judgment.docket_fk = docketmeta
        judgment.save() 

    print("Setting dockets for Plaintiffs")
    for plaintiff in Plaintiffs.objects.all():
        docketmeta = get_or_create_docketmeta(apps, plaintiff.docket, log=True, model="Plaintiffs")
        plaintiff.docket_fk = docketmeta
        plaintiff.save()     

def reverse_func(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('mass_evictions', '0002_unique_together'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocketOrphans',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('docket', models.CharField(blank=True, null=True, max_length=500)),
                ('originator_model', models.CharField(blank=True, null=True, max_length=500)),
            ]
        ),
        migrations.CreateModel(
            name='DocketMeta',
            fields=[
                ('docket', models.TextField(db_index=True, primary_key=True, serialize=False)),
            ],
        ),
        migrations.AddField(
            model_name='defendants',
            name='docket_fk',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='defendant_docket', to='mass_evictions.docketmeta'),
        ),
        migrations.AddField(
            model_name='docket',
            name='docket_fk',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='docket_meta', to='mass_evictions.docketmeta'),
        ),
        migrations.AddField(
            model_name='events',
            name='docket_fk',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='event_docket', to='mass_evictions.docketmeta'),
        ),
        migrations.AddField(
            model_name='filings',
            name='docket_fk',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='filing_docket', to='mass_evictions.docketmeta'),
        ),
        migrations.AddField(
            model_name='judgments',
            name='docket_fk',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='judgment_docket', to='mass_evictions.docketmeta'),
        ),
        migrations.AddField(
            model_name='plaintiffs',
            name='docket_fk',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='plaintiff_docket', to='mass_evictions.docketmeta'),
        ),
        migrations.RunPython(forwards_func, reverse_func)
    ]
