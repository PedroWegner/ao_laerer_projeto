# Generated by Django 4.0.4 on 2022-06-02 19:23

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0009_postagem_ultima_atualizacao'),
    ]

    operations = [
        migrations.AlterField(
            model_name='postagem',
            name='ultima_atualizacao',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]
