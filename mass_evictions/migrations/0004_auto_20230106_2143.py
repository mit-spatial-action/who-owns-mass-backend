from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('mass_evictions', '0003_filings_def_bar_fk_filings_ptf_bar_fk_and_more'),
    ]

    operations = [
        migrations.RemoveField('filings', 'ptf_bar'),
        migrations.RemoveField('filings', 'def_bar'),
        migrations.RenameField(
            model_name='filings',
            old_name='ptf_bar_fk',
            new_name='ptf_bar',
        ),
        migrations.RenameField(
            model_name='filings',
            old_name='def_bar_fk',
            new_name='def_bar',
        )
    ]
