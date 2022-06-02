from django.contrib import messages
from django.core.files.storage import default_storage
from django.conf import settings
from django.core.files.base import ContentFile
from datetime import date
import os
from .models import *
from ensino.models import *
from forum.models import Noticia
from forum.models import Conversa, ConversaUsuario, Mensagem, Postagem, Comentario
from forum.forms import MensagemForms
from .forms import *
from django.http import HttpResponseRedirect
from django.views import View
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
import bcrypt


class HomeView(ListView):
    """
    View de entrada; mostrara as noticias cadastradas
    """
    template_name = 'usuario/home.html'
    model = Noticia
    context_object_name = 'noticias'

    def get(self, *args, **kwargs):

        return super().get(self.request, *args, **kwargs)


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
        }
        self.usuario_cadastro = self.context['usuario_cadastro']
        self.pessoa_cadastro = self.context['pessoa_cadastro']

        self.renderizar = render(
            self.request, self.template_name, self.context
        )

    def get(self, *args, **kwargs):
        if 'usuario_logado' in self.request.session:
            return redirect('usuario:home')

        return self.renderizar

    def post(self, *args, **kwargs):
        if not self.pessoa_cadastro.is_valid():
            return self.renderizar

        # person
        pessoa = self.pessoa_cadastro.save()
        # user
        usuario = self.usuario_cadastro.save(commit=False)
        usuario.pessoa = pessoa
        usuario.save()

        for lingua in Lingua.objects.all():
            UsuarioLingua(
                usuario=usuario,
                lingua=lingua,
                nivel=NivelLingua.objects.filter(
                    valor_nivel=0,
                ).first()
            ).save()

        # aqui tem que redirecionar para a tela de login
        return redirect('usuario:home')


class LoginView(View):
    """
    View de login geral
    """
    template_name = 'usuario/login.html'

    def setup(self, *args, **kwargs):
        super().setup(*args, **kwargs)
        self.context = {
            'form': UsuarioLogin(
                data=self.request.POST or None
            )
        }
        self.renderizar = render(
            self.request, self.template_name, self.context)

    def get(self, *args, **kwargs):
        """
        Metodo subscrito para impedir que usarios nao logados tenham acesso
        aa plataforma
        """
        if 'usuario_logado' in self.request.session:
            return redirect('usuario:home')

        return self.renderizar

    def get_success_url(self):
        return reverse('usuario:home')

    def post(self, *args, **kwargs):
        """
        POST subscrito para receber usuario e senha.
        Neste metodo eh feita a verificacao se a senha do usuario entrada eh
        compativel com o que esta no banco de dados
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
                self.request.session['usuario_logado'].update(
                    {
                        'nome': pessoa.nome,
                        'sobrenome': pessoa.sobrenome,
                        'is_admin': usuario.is_admin,
                        'is_licenced': usuario.is_licenced,
                    }
                )
                self.request.session.save()

                if usuario:
                    print('dada')
                    return redirect('usuario:home')
            else:
                messages.add_message(
                    self.request, messages.ERROR, 'Senha inválida')
                self.renderizar = render(
                    self.request, self.template_name, self.context)
                return self.renderizar
        except Exception as e:
            messages.add_message(
                self.request, messages.ERROR, 'Usuário não existe')
            self.renderizar = render(
                self.request, self.template_name, self.context)

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
    template_name = 'usuario/perfil_usuario.html'
    model = Usuario
    object_context_name = 'usuario'

    def get(self, *args, **kwargs):
        if not 'usuario_logado' in self.request.session:
            return redirect('usuario:login')

        return super().get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['aulas_concluidas'] = {}
        for lingua in Lingua.objects.all():
            context['aulas_concluidas'][f'{lingua}'] = {}
            for nivel in NivelLingua.objects.all().exclude(valor_nivel=0):
                context['aulas_concluidas'][f'{lingua}'].update(
                    {
                        f'{nivel}': Aula.objects.filter(
                            id__in=EnvioAtividadeAula.objects.filter(
                                autor=self.get_object(),
                                aprovado=True,
                                atividade__aula__lingua=lingua,
                                atividade__aula__nivel=nivel,
                            ).values('atividade__aula_id')).count()
                    }
                )

        print(context['aulas_concluidas'])
        context['postagens'] = Postagem.objects.filter(
            autor=self.get_object()
        )[:5]
        context['comentarios'] = Comentario.objects.filter(
            autor=self.get_object()
        )[:5]

        if self.get_object().id == self.request.session['usuario_logado']['usuario_id']:
            pass
        else:
            # TESTAR ISSO MELHOR
            context['conversa'] = Conversa.objects.filter(
                id__in=ConversaUsuario.objects.filter(
                    usuario_id=self.get_object().id,
                ).values('conversa_id'),
            ).filter(
                id__in=ConversaUsuario.objects.filter(
                    usuario_id=self.request.session['usuario_logado']['usuario_id'],
                ).values('conversa_id'),
            ).first()
        return context


class ConversaView(DetailView):
    template_name = 'usuario/conversa.html'
    model = Conversa
    object_context_name = 'conversa'

    def get(self, *args, **kwargs):
        if not "usuario_logado" in self.request.session:
            return redirect('usuario:login')

        checagem = ConversaUsuario.objects.filter(
            usuario_id=self.request.session['usuario_logado']['usuario_id'],
            conversa_id=self.get_object(),
        )
        if not checagem:
            return redirect('usuario:home')
        return super().get(*args, **kwargs)

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


class IniciaConversa(DetailView):
    model = Usuario

    def get(self, *args, **kwargs):
        # AQUI COLOCAR ALGO QUE IMPEÇA CRIAR UMA NOVA COISA
        conversa = Conversa.objects.create()
        conversa.usuario.add(self.get_object())
        conversa.usuario.add(get_object_or_404(
            Usuario, id=self.request.session['usuario_logado']['usuario_id']
        ))

        return redirect(reverse('usuario:conversa', kwargs={'pk': conversa.id}))


class UpdateInformacoesView(View):
    template_name = 'usuario/update_infos.html'

    def setup(self, *args, **kwargs):
        super().setup(*args, **kwargs)
        self.context = {}

        self.renderizar = render(
            self.request, self.template_name, self.context)

    def get(self, *args, **kwargs):

        return self.renderizar

    def post(self, *args, **kwargs):
        # password update
        pass_1 = self.request.POST.get('senha_antiga_1')
        pass_2 = self.request.POST.get('senha_antiga_2')
        new_pass = self.request.POST.get('senha')
        password_update = update_password(
            self.request.session, pass_1, pass_2, new_pass)

        if not password_update:
            messages.add_message(
                self.request,
                messages.ERROR,
                'Senhas não conferem'
            )
            self.renderizar = render(
                self.request,
                self.template_name,
                self.context
            )
            return self.renderizar
        # Person update
        nome = self.request.POST.get('nome')
        sobrenome = self.request.POST.get('sobrenome')
        id_pessoa = self.request.session['usuario_logado']['pessoa_id']
        person_update = update_person(
            self.request.session, nome, sobrenome, id_pessoa)
        # Img update
        img = self.request.FILES.get('asgnmnt_file')
        img_update = update_img(self.request.session, img)

        if password_update:
            messages.add_message(
                self.request,
                messages.SUCCESS,
                "Senha atualizada."
            )
            return redirect('usuario:logout')
        if img_update or person_update:
            messages.add_message(
                self.request,
                messages.SUCCESS,
                "Dados atualizados"
            )
            return redirect('usuario:home')
        return self.renderizar


# SERVICES
def update_password(request, pass_1, pass_2, new_pass):
    if not pass_1 or not pass_2:
        return False
    if pass_1 == pass_2 and new_pass:
        if bcrypt.checkpw(pass_1.encode('utf-8'), request['usuario_logado']['senha'].encode('utf-8')):

            Usuario.objects.filter(
                id=request['usuario_logado']['usuario_id']
            ).update(
                senha=str(bcrypt.hashpw(new_pass.encode(
                    'utf-8'), bcrypt.gensalt()))[2:-1]
            )
            return True
        return False


def update_person(request, nome, sobrenome, id_pessoa):
    pessoa = Pessoa.objects.filter(
        id=id_pessoa).first()
    Pessoa.objects.filter(
        id=id_pessoa).update(
        nome=nome or pessoa.nome,
        sobrenome=sobrenome or pessoa.sobrenome,
    )
    if sobrenome:
        request['usuario_logado']['sobrenome'] = sobrenome
    if nome:
        request['usuario_logado']['nome'] = nome

    if nome or sobrenome:
        request.save()
        return True
    return False


def update_img(request, img):
    ano = date.today().strftime("%Y")
    mes = date.today().strftime("%m")
    if img:
        path = default_storage.save(
            rf"img_perfis\{ano}\{mes}\{img}", ContentFile(img.read()))
        os.path.join(settings.MEDIA_ROOT, path)

        usuario = Usuario.objects.filter(
            id=request['usuario_logado']['usuario_id']
        ).update(
            img_usuario=path
        )
        usuario = get_object_or_404(Usuario,
                                    id=request['usuario_logado']['usuario_id'])
        request['usuario_logado']['img_usuario'] = usuario.img_usuario.url
        request.save()
        return True
    return False
