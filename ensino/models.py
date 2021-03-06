from email.policy import default
from django.db import models
from usuario.models import Usuario, Pessoa
from django.utils import timezone
from PIL import Image  # para dar rezise (?)


class Lingua(models.Model):
    """
    Tabela de linguas disponiveis no curso
    """
    lingua = models.CharField(
        max_length=20
    )
    lingua_img = models.ImageField(
        upload_to='img_lingua',
        null=True,
        blank=True
    )

    def __str__(self) -> str:
        return f'{self.lingua}'


class NivelLingua(models.Model):
    """
    Tabela de niveis de lingua
    """
    nivel = models.CharField(
        max_length=2
    )
    valor_nivel = models.IntegerField(
        unique=True
    )

    def __str__(self) -> str:
        return f'{self.nivel}'

    class Meta:
        verbose_name = 'Nível de língua'
        verbose_name_plural = "Níveis de língua"


class UsuarioLingua(models.Model):
    lingua = models.ForeignKey(
        Lingua,
        null=True,
        on_delete=models.DO_NOTHING
    )
    usuario = models.ForeignKey(
        Usuario,
        null=True,
        on_delete=models.CASCADE
    )
    nivel = models.ForeignKey(
        NivelLingua,
        null=True,
        on_delete=models.DO_NOTHING
    )

    def __str__(self) -> str:
        return f'{self.usuario} - {self.lingua} - {self.nivel}'


class Administrador(models.Model):
    pessoa = models.ForeignKey(
        Pessoa,
        on_delete=models.CASCADE
    )
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE
    )


class ClassePalavra(models.Model):
    classe = models.CharField(
        max_length=40
    )
    lingua = models.ForeignKey(
        Lingua,
        blank=True,
        null=True,
        on_delete=models.DO_NOTHING
    )

    def __str__(self):
        return self.classe


class Contexto(models.Model):
    contexto = models.CharField(
        max_length=255
    )

    def __str__(self):
        return f"{self.contexto[:20]}[...]"


class Palavra(models.Model):
    palavra = models.CharField(
        max_length=40
    )
    lingua = models.ForeignKey(
        Lingua,
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )
    classe = models.ForeignKey(
        ClassePalavra,
        on_delete=models.DO_NOTHING
    )
    significado = models.CharField(
        max_length=255
    )
    nivel = models.ForeignKey(
        NivelLingua,
        blank=True,
        null=True,
        on_delete=models.DO_NOTHING
    )
    escrita_fonetica = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )
    data_cadastro = models.DateField(
        default=timezone.now
    )
    contexto = models.ManyToManyField(
        Contexto,
        related_name='palavras',
        through='PalavraContexto'
    )

    def __str__(self):
        return f'{self.palavra}'


class PalavraContexto(models.Model):
    palavra = models.ForeignKey(
        Palavra,
        on_delete=models.CASCADE
    )
    contexto = models.ForeignKey(
        Contexto,
        on_delete=models.DO_NOTHING
    )

    def __str__(self):
        return f'{self.palavra} - {self.contexto}'


class ModuloLinguaNivel(models.Model):
    lingua = models.ForeignKey(
        Lingua,
        on_delete=models.DO_NOTHING
    )
    nivel = models.ForeignKey(
        NivelLingua,
        on_delete=models.DO_NOTHING
    )
    descricao = models.TextField()
    img_modulo = models.ImageField(
        upload_to='img_modulo/%Y/%m',
        null=True,
        blank=True
    )

    def __str__(self) -> str:
        return f'Modulo {self.nivel}'


class Aula(models.Model):
    """
    Tabela de aulas disponiveis no curso
    """
    aula = models.CharField(
        max_length=250
    )
    conteudo = models.TextField()
    data_post = models.DateField(
        default=timezone.now
    )
    nivel = models.ForeignKey(
        NivelLingua,
        default=1,
        on_delete=models.DO_NOTHING
    )
    lingua = models.ForeignKey(
        Lingua,
        blank=True,
        null=True,
        on_delete=models.CASCADE
    )
    autor_aula = models.ForeignKey(
        Usuario,
        on_delete=models.DO_NOTHING
    )
    aula_gravada = models.FileField(
        upload_to='aula/%Y/%m'
    )
    img_aula = models.ImageField(
        default='img_aula/default.jpg',
        upload_to='img_aula/%Y/%m',
        null=True,
        blank=True)
    palavra = models.ManyToManyField(
        Palavra, related_name='aulas',
        through="AulaPalavra"
    )
    is_licenced = models.BooleanField(
        default=False
    )
    modulo = models.ForeignKey(
        ModuloLinguaNivel,
        null=True,
        blank=True,
        default=None,
        on_delete=models.DO_NOTHING
    )

    def __str__(self) -> str:
        return self.aula


class AulaPalavra(models.Model):
    aula = models.ForeignKey(
        Aula,
        on_delete=models.CASCADE
    )
    palavra = models.ForeignKey(
        Palavra,
        on_delete=models.DO_NOTHING
    )

# teste nova atividade


class Questao(models.Model):
    frase = models.CharField(
        max_length=255
    )
    autor = models.ForeignKey(
        Usuario,
        null=True,
        on_delete=models.DO_NOTHING
    )
    lingua = models.ForeignKey(
        Lingua,
        on_delete=models.DO_NOTHING,
    )
    nivel = models.ForeignKey(
        NivelLingua,
        on_delete=models.DO_NOTHING,
    )

    def __str__(self):
        return f'{self.frase[:10]}'


class Alternativa(models.Model):
    alternativa = models.CharField(
        max_length=60
    )
    is_correct = models.BooleanField(
        default=False
    )
    questao = models.ForeignKey(
        Questao,
        on_delete=models.DO_NOTHING
    )

    def __str__(self):
        return self.alternativa


class AtividadeAula(models.Model):
    aula = models.ForeignKey(
        Aula,
        on_delete=models.DO_NOTHING,
        related_name='atividade'
    )
    questao = models.ManyToManyField(
        Questao,
        related_name='atividade',
        through="AtividadeQuestao"
    )

    def __str__(self):
        return f'Atividade - {self.aula}'


class AtividadeQuestao(models.Model):
    atividade = models.ForeignKey(
        AtividadeAula,
        on_delete=models.DO_NOTHING
    )
    questao = models.ForeignKey(
        Questao,
        on_delete=models.DO_NOTHING
    )

    def __str__(self):
        return f'{self.atividade} - {self.questao}'


class EnvioAtividadeAula(models.Model):
    autor = models.ForeignKey(
        Usuario,
        on_delete=models.DO_NOTHING
    )
    atividade = models.ForeignKey(
        AtividadeAula,
        on_delete=models.DO_NOTHING
    )
    aprovado = models.BooleanField(
        default=False
    )
    nota = models.FloatField()
