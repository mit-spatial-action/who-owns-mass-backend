# Generated by Django 4.1.5 on 2023-08-05 19:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mass_evictions', '0010_alter_attorneys_geometry_alter_filings_geometry'),
    ]

    operations = [
        migrations.CreateModel(
            name='Owner',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prop_id', models.CharField(max_length=200)),
                ('loc_id', models.CharField(max_length=200)),
                ('fy', models.IntegerField()),
                ('use_code', models.IntegerField()),
                ('city', models.CharField(max_length=200)),
                ('owner1', models.CharField(max_length=500)),
                ('own_addr', models.TextField()),
                ('own_city', models.CharField(max_length=200)),
                ('own_state', models.CharField(max_length=100)),
                ('own_zip', models.CharField(max_length=200)),
                ('co', models.CharField(max_length=200)),
                ('zip', models.CharField(max_length=200)),
                ('name_address', models.TextField()),
                ('id_corp', models.CharField(max_length=200)),
                ('count', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='OwnerGroup',
            fields=[
                ('id', models.CharField(max_length=200, primary_key=True, serialize=False)),
            ],
        ),
        migrations.AddIndex(
            model_name='ownergroup',
            index=models.Index(fields=['id'], name='mass_evicti_id_6a81f1_idx'),
        ),
        migrations.AddField(
            model_name='owner',
            name='group',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='group', to='mass_evictions.ownergroup'),
        ),
    ]