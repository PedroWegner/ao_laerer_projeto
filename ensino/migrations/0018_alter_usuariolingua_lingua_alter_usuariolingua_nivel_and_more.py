# Generated by Django 4.0.4 on 2022-05-15 22:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('usuario', '0004_usuario_is_licenced'),
        ('ensino', '0017_alter_usuariolingua_lingua_alter_usuariolingua_nivel_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuariolingua',
            name='lingua',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='ensino.lingua'),
        ),
        migrations.AlterField(
            model_name='usuariolingua',
            name='nivel',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='ensino.nivellingua'),
        ),
        migrations.AlterField(
            model_name='usuariolingua',
            name='usuario',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='usuario.usuario'),
        ),
    ]
