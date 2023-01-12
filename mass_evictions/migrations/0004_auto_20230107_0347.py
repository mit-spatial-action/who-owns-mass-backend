from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mass_evictions', '0003_docketmeta_defendants_docket_fk_docket_docket_fk_and_more'),
    ]

    operations = [
        migrations.RemoveField('docket', 'docket'),
        migrations.RemoveField('defendants', 'docket'),
        migrations.RemoveField('events', 'docket'),
        migrations.RemoveField('filings', 'docket'),
        migrations.RemoveField('judgments', 'docket'),
        migrations.RemoveField('plaintiffs', 'docket'),
        migrations.RenameField(
            model_name='docket',
            old_name='docket_fk',
            new_name='docket',
        ),
        migrations.RenameField(
            model_name='defendants',
            old_name='docket_fk',
            new_name='docket',
        ),
        migrations.RenameField(
            model_name='events',
            old_name='docket_fk',
            new_name='docket',
        ),
        migrations.RenameField(
            model_name='filings',
            old_name='docket_fk',
            new_name='docket',
        ),
        migrations.RenameField(
            model_name='judgments',
            old_name='docket_fk',
            new_name='docket',
        ),
        migrations.RenameField(
            model_name='plaintiffs',
            old_name='docket_fk',
            new_name='docket',
        ),
    ]
