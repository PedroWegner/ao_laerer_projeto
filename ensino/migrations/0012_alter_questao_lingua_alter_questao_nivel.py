# Generated by Django 4.0.4 on 2022-05-02 19:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ensino', '0011_questao_autor_questao_lingua_questao_nivel'),
    ]

    operations = [
        migrations.AlterField(
            model_name='questao',
            name='lingua',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='ensino.lingua'),
        ),
        migrations.AlterField(
            model_name='questao',
            name='nivel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='ensino.nivellingua'),
        ),
    ]
