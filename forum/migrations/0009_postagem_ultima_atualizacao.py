# Generated by Django 4.0.4 on 2022-06-02 18:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0008_alter_conversausuario_ultimo_acesso'),
    ]

    operations = [
        migrations.AddField(
            model_name='postagem',
            name='ultima_atualizacao',
            field=models.DateField(default='2002-02-02'),
        ),
    ]