# Generated by Django 4.1.5 on 2024-10-31 17:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('who_owns_mass', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='address',
            name='muni_id',
        ),
        migrations.AddField(
            model_name='address',
            name='muni',
            field=models.CharField(blank=True, help_text='Street name and address type.', max_length=100, null=True),
        ),
    ]
