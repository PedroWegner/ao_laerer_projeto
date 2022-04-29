from django.db import models
from usuario.models import Usuario, Pessoa
from django.utils import timezone
from PIL import Image  # para dar rezise (?)


class Lingua(models.Model):
    """
    Tabela de linguas disponiveis no curso
    """
    lingua = models.CharField(max_length=20)
    lingua_img = models.ImageField(
        upload_to='img_lingua', null=True, blank=True)

    def __str__(self) -> str:
        return f'{self.lingua}'


class NivelLingua(models.Model):
    """
    Tabela de niveis de lingua
    """
    nivel = models.CharField(max_length=2)
    valor_nivel = models.IntegerField(unique=True)

    def __str__(self) -> str:
        return f'{self.nivel}'

    class Meta:
        verbose_name = 'Nível de língua'
        verbose_name_plural = "Níveis de língua"


class Administrador(models.Model):
    pessoa = models.ForeignKey(Pessoa, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)


class UsuarioEnsino(models.Model):
    pessoa = models.ForeignKey(Pessoa, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)


# class Departamento(models.Model):
#     """
#     Tabela de departamentos do curso
#     """
#     cod_departamento = models.CharField(max_length=2)
#     lingua = models.ForeignKey(Lingua, on_delete=models.DO_NOTHING)

#     def __str__(self) -> str:
#         return f'Departamento de {self.lingua}'


# revisar construcao de classe
# class Modulo(models.Model):
#     """
#     Tabela de modulos disponiveis no curso
#     """
#     modulo = models.CharField(max_length=50)
#     cod_modulo = models.CharField(max_length=3)
#     lingua = models.ForeignKey(Lingua, on_delete=models.DO_NOTHING)
#     nivel = models.ForeignKey(NivelLingua, on_delete=models.DO_NOTHING)
#     '''
#     usar funcao splits 'dep de x'(split, ' ')[2]
#     '''
#     departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE)
#     img_modulo = models.ImageField(
#         upload_to='img_modulo/%Y/%m', null=True, blank=True)

#     def __str__(self) -> str:
#         return f'{self.cod_modulo} - {self.modulo}'


# class Professor(models.Model):
#     """
#     Tabela de professores
#     """
#     pessoa = models.ForeignKey(Pessoa, on_delete=models.DO_NOTHING)
#     usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
#     departamento = models.ForeignKey(Departamento, on_delete=models.DO_NOTHING)
#     lingua = models.ForeignKey(Lingua, on_delete=models.DO_NOTHING)
#     nivel = models.ForeignKey(NivelLingua, on_delete=models.DO_NOTHING)
#     # TENTAR CRIAR A TERCEIRA TABELA A MAO
#     modulo = models.ManyToManyField(
#         Modulo, blank=True, through='ModuloVinculoProfessor')

#     def __str__(self) -> str:
#         return f'{self.pessoa.nome} {self.pessoa.sobrenome}'


# class ModuloVinculoProfessor(models.Model):
#     """
#     Tabela de muitos para muitos, facilita alguns registros e querys assim.
#     """
#     professor = models.ForeignKey(Professor, on_delete=models.CASCADE)
#     modulo = models.ForeignKey(Modulo, on_delete=models.CASCADE)
#     data_vinculo = models.DateField(default=timezone.now)
#     ativo = models.BooleanField(default=True)

#     def __str__(self) -> str:
#         return f'{self.professor} vinculado a {self.modulo}'

#     class Meta:
#         verbose_name = 'Professor vinculado a módulo'
#         verbose_name_plural = 'Professores vinculados a módulos'


class ClassePalavra(models.Model):
    classe = models.CharField(max_length=40)
    lingua = models.ForeignKey(
        Lingua, blank=True, null=True, on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.classe


class Contexto(models.Model):
    contexto = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.contexto[:20]}[...]"


class Palavra(models.Model):
    palavra = models.CharField(max_length=40)
    lingua = models.ForeignKey(
        Lingua, null=True, blank=True, on_delete=models.CASCADE)
    classe = models.ForeignKey(ClassePalavra, on_delete=models.DO_NOTHING)
    significado = models.CharField(max_length=255)
    nivel = models.ForeignKey(NivelLingua, blank=True,
                              null=True, on_delete=models.DO_NOTHING)
    escrita_fonetica = models.CharField(max_length=50, blank=True, null=True)
    contexto = models.ManyToManyField(
        Contexto, related_name='palavras', through='PalavraContexto')

    def __str__(self):
        return self.palavra


class PalavraContexto(models.Model):
    palavra = models.ForeignKey(Palavra, on_delete=models.CASCADE)
    contexto = models.ForeignKey(Contexto, on_delete=models.DO_NOTHING)

    def __str__(self):
        return f'{self.palavra} - {self.contexto}'


class Aula(models.Model):
    """
    Tabela de aulas disponiveis no curso
    """
    aula = models.CharField(max_length=250)
    conteudo = models.TextField()
    conteudo_download = models.FileField(
        upload_to='conteudo_aula/%Y/%m', blank=True, null=True
    )
    data_post = models.DateField(default=timezone.now)
    nivel = models.ForeignKey(NivelLingua, default=1,
                              on_delete=models.DO_NOTHING)
    lingua = models.ForeignKey(
        Lingua, blank=True, null=True, on_delete=models.CASCADE)
    # modulo = models.ManyToManyField(
    #     Modulo, blank=True, through='AulaVinculaModulo')
    autor_aula = models.ForeignKey(Usuario, on_delete=models.DO_NOTHING)
    aula_gravada = models.FileField(upload_to='aula/%Y/%m')
    img_aula = models.ImageField(
        upload_to='img_aula/%Y/%m', null=True, blank=True)
    palavra = models.ManyToManyField(
        Palavra, related_name='aulas', through="AulaPalavra")

    def __str__(self) -> str:
        return self.aula


class AulaPalavra(models.Model):
    aula = models.ForeignKey(Aula, on_delete=models.CASCADE)
    palavra = models.ForeignKey(Palavra, on_delete=models.DO_NOTHING)


# class AulaVinculaModulo(models.Model):
#     """
#     Tabela de muitos para muitos de aula com modulo
#     """
#     aula = models.ForeignKey(
#         Aula, on_delete=models.CASCADE, related_name='modulos')
#     modulo = models.ForeignKey(
#         Modulo, on_delete=models.CASCADE, related_name='aulas')

#     def __str__(self) -> str:
#         return f'{self.modulo.modulo} - {self.aula}'

#     class Meta:
#         verbose_name = 'Módulo e aula'
#         verbose_name_plural = 'Módulos e aulas'


class Atividade(models.Model):
    """
    Tabela para registrar atividades de aulas
    """
    aula = models.ForeignKey(
        Aula, on_delete=models.CASCADE, related_name='atividade')
    data_post = models.DateField(default=timezone.now)
    usuario = models.ForeignKey(
        UsuarioEnsino, on_delete=models.DO_NOTHING)
    atividade_doc = models.FileField(
        upload_to='atividade_postada/%Y/%m', verbose_name='Atividade')
    comentario = models.TextField(blank=True, null=True)

    def __str__(self) -> str:
        return f'Atividade da aula {self.aula.aula}'


# class Aluno(models.Model):
#     """
#     Tabela para registro de alunos
#     """
#     pessoa = models.ForeignKey(Pessoa, on_delete=models.DO_NOTHING)
#     usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
#     modulo = models.ManyToManyField(
#         Modulo, blank=True, related_name='alunos', through='ModuloMatriculaAluno')  # THROUGH

#     def __str__(self) -> str:
#         return f'{self.pessoa.nome} {self.pessoa.sobrenome}'


# class ModuloMatriculaAluno(models.Model):
#     """
#     Tabela de muitos para muitos, de aluno com modulo; criada para ter mais
#     atribuos na tabela
#     """
#     aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE) # ALTERAR PARA USUARIO
#     modulo = models.ForeignKey(Modulo, on_delete=models.CASCADE)
#     data_matricula = models.DateField(default=timezone.now)
#     aprovado = models.BooleanField(default=False)

#     def __str__(self):
#         return f'{self.aluno} > {self.modulo}({self.modulo.nivel})'

#     class Meta:
#         verbose_name = 'Aluno matriculado'
#         verbose_name_plural = 'Alunos matriculados'


class EnvioAtividade(models.Model):
    """
    Tabela para registrar envios de atividade
    """
    data_entrega = models.DateField(
        default=timezone.now)  # I HAVE TO CHANGE IT
    usuario = models.ForeignKey(UsuarioEnsino, on_delete=models.DO_NOTHING)
    atividade = models.ForeignKey(
        Atividade, on_delete=models.DO_NOTHING, related_name='atividades_enviadas')
    envio_atividade_doc = models.FileField(
        upload_to='atividade_enviada/%Y/%m')
    nota = models.FloatField(blank=True, null=True)
    comentario = models.TextField(blank=True, null=True)
    envio_definitivo = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f'{self.atividade} enviada por {self.aluno.pessoa}'

    class Meta:
        verbose_name = 'Atividade enviada'
        verbose_name_plural = 'Atividades enviadas'
