# Generated by Django 4.0.4 on 2022-06-02 17:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0002_alter_postagem_imagem_postagem'),
    ]

    operations = [
        migrations.AddField(
            model_name='conversausuario',
            name='ultimo_acesso',
            field=models.DateField(default='2002-02-02'),
        ),
    ]
