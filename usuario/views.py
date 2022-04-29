from dataclasses import is_dataclass
from ensino.models import UsuarioEnsino
from forum.models import Noticia
from django.http import HttpResponseRedirect
from re import X
from django.views import View
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView
from django.views.generic import FormView
from django.views.generic.detail import SingleObjectMixin, DetailView
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
# from .models import ClassePalavra, Contexto, Administrador, Aluno, Atividade, Lingua, ModuloMatriculaAluno, ModuloVinculoProfessor, NivelLingua, Noticia, Palavra, PalavraContexto, Professor, Modulo, Aula, EnvioAtividade, AulaVinculaModulo
from .forms import *
from .models import *
from forum.models import Conversa, ConversaUsuario, Mensagem, Postagem, Comentario
from forum.forms import MensagemForms
import bcrypt


class HomeView(ListView):
    """
    View de entrada; mostrara as noticias cadastradas
    """
    template_name = 'usuario/home.html'
    model = Noticia
    context_object_name = 'noticias'

    # def get(self, *args, **kwargs):
    #     if not 'usuario_logado' in self.request.session:
    #         print('usuario deslogado')
    #         return redirect('departamento:login')
    #     return super().get(self.request, *args, **kwargs)


class UsuarioCadastroView(View):
    template_name = 'usuario/cadastro/cadastro_usuario.html'

    def setup(self, *args, **kwargs):
        super().setup(*args, **kwargs)

        self.context = {
            'usuario_cadastro': UsuarioCadastro(
                data=self.request.POST or None,
            ),
            'pessoa_cadastro': PessoaCadastro(
                data=self.request.POST or None,
            ),
            'endereco_cadastro': EnderecoCadastro(
                data=self.request.POST or None,
            ),
        }
        self.usuario_cadastro = self.context['usuario_cadastro']
        self.pessoa_cadastro = self.context['pessoa_cadastro']
        self.endereco_cadastro = self.context['endereco_cadastro']

        self.renderizar = render(
            self.request, self.template_name, self.context
        )

    def get(self, *args, **kwargs):
        if 'usuario_logado' in self.request.session:
            print('não pode estar aqui')

        return self.renderizar

    def post(self, *args, **kwargs):
        if not self.pessoa_cadastro.is_valid() or not self.endereco_cadastro.is_valid():
            return self.renderizar

        # cadastra endereco
        endereco = self.endereco_cadastro.save()
        # cadastra pessoa
        pessoa = self.pessoa_cadastro.save(commit=False)
        pessoa.endereco = endereco
        pessoa.save()
        # cadastra usuario
        usuario = self.usuario_cadastro.save(commit=False)
        usuario.pessoa = pessoa
        usuario.save()

        usuario_ensino = UsuarioEnsino()
        usuario_ensino.usuario = usuario
        usuario_ensino.pessoa = pessoa

        return redirect('usuario:home')


class LoginView(View):
    """
    View de login geral
    """
    template_name = 'usuario/login.html'

    def setup(self, *args, **kwargs):
        """
        Metodo alterado para criar indices que serao usados durante a aplicacao
        """
        super().setup(*args, **kwargs)

        self.renderizar = render(
            self.request, self.template_name
        )

    def get(self, *args, **kwargs):
        """
        Metodo subscrito para impedir que usarios nao logados tenham acesso
        aa plataforma
        """
        if 'usuario_logado' in self.request.session:
            return redirect('usuario:home')

        return self.renderizar

    def post(self, *args, **kwargs):
        """
        POST subscrito para receber usuario e senha.
        Neste metodo eh feita a verificacao se a senha do usuario entrada eh
        compativel com o que esta no banco de dados
        Neste metodo, tambem, eh alterado o indice de usuario_logado da session.
        Eh tambem implemtanda verificacao do tipo de usuario logado, para restringir
        tela
        """

        try:
            usuario = get_object_or_404(
                Usuario, usuario=self.request.POST.get('usuario')
            )
            if bcrypt.checkpw(self.request.POST.get('senha').encode('utf-8'), usuario.senha.encode('utf-8')):
                self.request.session['usuario_logado'] = {
                    'usuario_id': usuario.id,
                    'usuario': usuario.usuario,
                    'email': usuario.email,
                    'senha': usuario.senha,
                    'pessoa_id': usuario.pessoa_id,
                }
                if usuario.img_usuario:
                    self.request.session['usuario_logado'].update(
                        {
                            'img_usuario': usuario.img_usuario.url
                        }
                    )

                pessoa = get_object_or_404(
                    Pessoa, id=self.request.session['usuario_logado']['pessoa_id']
                )

                if not usuario.is_admin:
                    self.request.session['usuario_logado'].update(
                        {
                            'nome': pessoa.nome,
                            'sobrenome': pessoa.sobrenome,
                            'is_admin': usuario.is_admin
                        }
                    )
                elif usuario.is_admin:
                    self.request.session['usuario_logado'].update(
                        {
                            'nome': pessoa.nome,
                            'sobrenome': pessoa.sobrenome,
                            'is_admin': usuario.is_admin
                        }
                    )
                else:
                    pass

                self.request.session.save()

                if usuario:
                    return redirect('usuario:home')
                else:
                    print('não sei')  # I HAVE TO MAKE SOMETHING DIFFERENT HERE
            else:
                pass
                return self.renderizar
        except Exception as e:
            print(f"Usuario não existe: {e}")

        return self.renderizar


class LogoutView(View):
    """
    Classe de logout, equipara o usuario_logado a None, para permitir a entrada
    de um novo usuario
    """

    def get(self, *args, **kwargs):
        del self.request.session['usuario_logado']
        return redirect('usuario:login')


class PerfilUsuarioView(DetailView):
    template_name = 'blog/perfil_usuario.html'
    model = Usuario
    object_context_name = 'usuario'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print(self.get_object())
        # if self.get_object().tipo_usuario.id == 1:
        #     context['cursos_vinculados'] = ModuloMatriculaAluno.objects.filter(
        #         aluno__usuario=self.get_object(),
        #         aprovado=True
        #     )
        # else:
        #     context['cursos_vinculados'] = ModuloVinculoProfessor.objects.filter(
        #         professor__usuario=self.get_object(),
        #     )
        context['postagens'] = Postagem.objects.filter(
            autor=self.get_object()
        )[:5]
        context['comentarios'] = Comentario.objects.filter(
            autor=self.get_object()
        )[:5]

        if self.get_object().id == self.request.session['usuario_logado']['usuario_id']:
            pass
        else:
            conversa = ConversaUsuario.objects.filter(
                usuario_id=self.get_object().id,
                conversa=get_object_or_404(
                    Conversa,
                    conversausuario__usuario_id=self.request.session['usuario_logado']['usuario_id']
                )
            ).values('conversa_id').first()
            if not conversa:
                context['conversa'] = None
            else:
                context['conversa'] = get_object_or_404(
                    Conversa, id=conversa['conversa_id']
                )
        return context


class ConversaView(DetailView):
    template_name = 'blog/conversa.html'
    model = Conversa
    object_context_name = 'conversa'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = MensagemForms(
            data=self.request.POST or None,
            files=self.request.FILES or None
        )
        context['mensagens'] = Mensagem.objects.filter(
            conversa=self.get_object()
        )

        return context

    def get(self, *args, **kwargs):
        # aqui precisa colocar a lógica para evtar que um outro usuario nao da conversa tenha acesso

        return super().get(*args, **kwargs)

    def post(self, *args, **kwargs):
        Mensagem(
            conversa=self.get_object(),
            autor=get_object_or_404(
                Usuario, id=self.request.session['usuario_logado']['usuario_id'],
            ),
            texto=self.request.POST.get('texto'),
            imagem_mensagem=self.request.FILES.get(
                'imagem_comentario') or None,
        ).save()
        return HttpResponseRedirect(self.request.path_info)
