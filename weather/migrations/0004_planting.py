from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('weather', '0003_region_soil_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gardenplot',
            name='cultures',
        ),
        migrations.CreateModel(
            name='Planting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('planned', 'Планируется'), ('planted', 'Посажено')], default='planned', max_length=20, verbose_name='Статус')),
                ('planted_date', models.DateField(blank=True, null=True, verbose_name='Дата посадки')),
                ('culture', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='plantings', to='weather.culture')),
                ('plot', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='plantings', to='weather.gardenplot')),
            ],
            options={
                'verbose_name': 'Посадка',
                'verbose_name_plural': 'Посадки',
                'unique_together': {('plot', 'culture')},
            },
        ),
        migrations.AddField(
            model_name='gardenplot',
            name='cultures',
            field=models.ManyToManyField(blank=True, related_name='plots', through='weather.Planting', to='weather.culture'),
        ),
    ]