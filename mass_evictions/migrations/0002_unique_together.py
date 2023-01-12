from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mass_evictions', '0001_initial'),
    ]

    operations = [
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
    ]
