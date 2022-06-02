from datetime import datetime
from django.db import models
from ensino.models import Lingua
from usuario.models import Usuario
from django.utils import timezone


class Noticia(models.Model):
    titulo_noticia = models.CharField(
        max_length=50
    )
    conteudo_noticia = models.TextField()
    data_post = models.DateField(
        default=timezone.now
    )
    administrador = models.ForeignKey(
        Usuario,
        on_delete=models.DO_NOTHING
    )
    imagem_noticia = models.ImageField(
        upload_to='img_noticia/%Y/%m'
    )

    def __str__(self) -> str:
        return f'{self.titulo_noticia} postado por {self.administrador}'


class Postagem(models.Model):
    titulo_postagem = models.CharField(
        max_length=60
    )
    conteudo_postagem = models.TextField()
    imagem_postagem = models.ImageField(
        upload_to='blog/postagem/%Y/%m',
        blank=True,
        null=True
    )
    data_postagem = models.DateField(
        default=timezone.now
    )
    autor = models.ForeignKey(
        Usuario,
        on_delete=models.DO_NOTHING)
    lingua = models.ForeignKey(
        Lingua,
        on_delete=models.DO_NOTHING
    )
    ultima_atualizacao = models.DateField(
        default=timezone.now
    )

    def __str__(self) -> str:
        return f'{self.titulo_postagem} por {self.autor}'


class Comentario(models.Model):
    conteudo_comentario = models.TextField()
    autor = models.ForeignKey(
        Usuario,
        on_delete=models.DO_NOTHING
    )
    data_comentario = models.DateField(
        default=timezone.now
    )
    imagem_comentario = models.ImageField(
        blank=True,
        null=True,
        upload_to='blog/comentario/%Y/%m'
    )
    postagem = models.ForeignKey(
        Postagem,
        on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        return f'Comentario de {self.autor}'


class Conversa(models.Model):
    usuario = models.ManyToManyField(
        Usuario,
        related_name='conversas',
        through='ConversaUsuario'
    )
    data_inicio = models.DateField(
        default=timezone.now
    )


class ConversaUsuario(models.Model):
    conversa = models.ForeignKey(
        Conversa,
        on_delete=models.CASCADE
    )
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.DO_NOTHING
    )
    ultimo_acesso = models.DateField(
        default=timezone.now
    )

    def __str__(self) -> str:
        return f'{self.conversa.id} - {self.usuario}'


class Mensagem(models.Model):
    conversa = models.ForeignKey(
        Conversa,
        on_delete=models.DO_NOTHING
    )
    texto = models.TextField()
    imagem_mensagem = models.ImageField(
        upload_to='chat/%Y/%m',
        blank=True,
        null=True
    )
    autor = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE
    )
    data_envio = models.DateField(
        default=timezone.now
    )
