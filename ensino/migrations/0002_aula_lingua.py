# Generated by Django 4.0.4 on 2022-04-29 19:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ensino', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='aula',
            name='lingua',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='ensino.lingua'),
        ),
    ]
