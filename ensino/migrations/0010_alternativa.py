# Generated by Django 4.0.4 on 2022-05-01 23:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ensino', '0009_delete_alternativa'),
    ]

    operations = [
        migrations.CreateModel(
            name='Alternativa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('alternativa', models.CharField(max_length=60)),
                ('is_correct', models.BooleanField(default=False)),
                ('questao', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='ensino.questao')),
            ],
        ),
    ]
