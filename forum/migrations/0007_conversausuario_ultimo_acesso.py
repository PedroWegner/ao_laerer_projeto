# Generated by Django 4.0.4 on 2022-06-02 17:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0006_remove_conversausuario_ultimo_acesso'),
    ]

    operations = [
        migrations.AddField(
            model_name='conversausuario',
            name='ultimo_acesso',
            field=models.DateField(default='2002-02-02'),
        ),
    ]