from email.policy import default
from django.db import models
from django.utils import timezone
import bcrypt
import re


class Estado(models.Model):
    estado = models.CharField(max_length=250)

    def __str__(self) -> str:
        return self.estado


class TipoEndereco(models.Model):
    tipo_endereco = models.CharField(max_length=250)

    def __str__(self) -> str:
        return self.tipo_endereco


class Genero(models.Model):
    genero = models.CharField(max_length=250)

    def __str__(self) -> str:
        return self.genero


# class TipoUsuario(models.Model):
#     tipo_usuario = models.CharField(max_length=250)

#     def __str__(self) -> str:
#         return self.tipo_usuario


class EstadoCivil(models.Model):
    estado_civil = models.CharField(max_length=250)

    def __str__(self) -> str:
        return self.estado_civil


class Endereco(models.Model):
    rua = models.CharField(max_length=250)
    numero = models.CharField(max_length=250)
    bairro = models.CharField(max_length=250)
    cep = models.CharField(max_length=9)
    cidade = models.CharField(max_length=50)
    tipo_endereco = models.ForeignKey(
        TipoEndereco, on_delete=models.DO_NOTHING)
    estado = models.ForeignKey(Estado, on_delete=models.DO_NOTHING)

    def __str__(self) -> str:
        return f'{self.rua}, {self.numero} - {self.bairro}'


class Pessoa(models.Model):
    nome = models.CharField(max_length=250)
    sobrenome = models.CharField(max_length=250)
    data_nascimento = models.DateField()
    cpf = models.CharField(max_length=11, unique=True)
    data_cadastro = models.DateField(default=timezone.now)
    celular = models.CharField(max_length=15, blank=True)
    genero = models.ForeignKey(Genero, on_delete=models.DO_NOTHING)
    estado_civil = models.ForeignKey(
        EstadoCivil, on_delete=models.DO_NOTHING)
    endereco = models.ForeignKey(
        Endereco, on_delete=models.DO_NOTHING)

    def __str__(self) -> str:
        return f'{self.nome} {self.sobrenome}'

    # def clean(self):
    #     pass
        ''' cpf = re.sub(r'[^0-9]', '', self.cpf)
        nascimento = re.sub(r'[^0-9]', '', self.data_nascimento)
        if not cpf.isnumeric():
            raise ValidationError('cpf inválido')

        if not nascimento.isnumeric():
            raise ValidationError('data inválida')'''


# FAZER UM TESTE PARA MELHORAR O ENCAPSULAMENTO
class Usuario(models.Model):
    usuario = models.CharField(max_length=250, unique=True)
    email = models.EmailField(max_length=250, unique=True)
    senha = models.CharField(max_length=250)
    img_usuario = models.ImageField(default='img_perfis/comum.png',
                                    upload_to='img_perfis/%Y/%m', null=True, blank=True)
    # tipo_usuario = models.ForeignKey(TipoUsuario, on_delete=models.DO_NOTHING)
    pessoa = models.ForeignKey(Pessoa, on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f'{self.pessoa.nome} {self.pessoa.sobrenome}'

    def save(self, *args, **kwargs):
        """
        Funcao save para alterar a senha do usuario toda vez que ele for criado

        """
        # abaixo unidecode tira acentos
        # self.usuario = f'{unidecode(self.pessoa.nome)}{unidecode(self.pessoa.sobrenome)}'.lower(
        # )
        # self.senha = f'{unidecode(self.pessoa.nome)}@{self.pessoa.cpf}'.lower()
        # print(self.senha)
        # self.email = f'{unidecode(self.pessoa.nome)}{unidecode(self.pessoa.sobrenome)}@eduamais.com'.lower()
        senha_criptografada = bcrypt.hashpw(
            (self.senha).encode('utf-8'), bcrypt.gensalt()
        )
        self.senha = str(senha_criptografada)[2:-1]
        super().save(*args, **kwargs)
