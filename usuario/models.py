from django.db import models
from django.utils import timezone


class Pessoa(models.Model):
    nome = models.CharField(
        max_length=250
    )
    sobrenome = models.CharField(
        max_length=250
    )
    data_nascimento = models.DateField()
    data_cadastro = models.DateField(
        default=timezone.now
    )

    def __str__(self) -> str:
        return f'{self.nome} {self.sobrenome}'

# FAZER UM TESTE PARA MELHORAR O ENCAPSULAMENTO


class Usuario(models.Model):
    usuario = models.CharField(
        max_length=250,
        unique=True
    )
    email = models.EmailField(
        max_length=250,
        unique=True
    )
    senha = models.CharField(
        max_length=250
    )
    img_usuario = models.ImageField(
        default='img_perfis/comum.png',
        upload_to='img_perfis/%Y/%m',
        null=True,
        blank=True)
    pessoa = models.ForeignKey(
        Pessoa,
        on_delete=models.CASCADE
    )
    is_admin = models.BooleanField(
        default=False
    )
    is_licenced = models.BooleanField(
        default=False
    )

    def __str__(self) -> str:
        return f'{self.pessoa.nome} {self.pessoa.sobrenome}'
