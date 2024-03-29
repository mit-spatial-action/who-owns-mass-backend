# Generated by Django 4.1.5 on 2024-02-19 20:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mass_evictions', '0009_address_metacorp_role_person_company'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='metacorp',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='company_meta', to='mass_evictions.metacorp'),
        ),
        migrations.AlterField(
            model_name='address',
            name='add1',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='address',
            name='add2',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='address',
            name='city',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='address',
            name='state',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='address',
            name='street',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='address',
            name='zip',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
