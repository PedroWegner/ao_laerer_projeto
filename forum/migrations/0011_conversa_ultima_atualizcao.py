# Generated by Django 4.0.4 on 2022-06-04 15:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0010_alter_postagem_ultima_atualizacao'),
    ]

    operations = [
        migrations.AddField(
            model_name='conversa',
            name='ultima_atualizcao',
            field=models.DateField(default='2002-02-02'),
        ),
    ]
