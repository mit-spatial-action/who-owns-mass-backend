# Generated by Django 4.1.5 on 2024-10-31 17:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('who_owns_mass', '0002_remove_address_muni_id_address_muni'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='muni',
            field=models.CharField(blank=True, help_text='Municipality name.', max_length=100, null=True),
        ),
    ]
