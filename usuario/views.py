from ensino.models import *
from ensino.models import UsuarioLingua
from forum.models import Noticia
from django.http import HttpResponseRedirect
from django.views import View
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView
from django.views.generic import FormView
from django.views.generic.detail import DetailView
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
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

    def get(self, *args, **kwargs):
        if not 'usuario_logado' in self.request.session:
            print('usuario deslogado')
            return redirect('usuario:login')
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

        # PRECISO TESTAR ISSO
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


class LoginView(FormView):
    """
    View de login geral
    """
    template_name = 'usuario/login.html'
    form_class = UsuarioLogin

    def get(self, *args, **kwargs):
        """
        Metodo subscrito para impedir que usarios nao logados tenham acesso
        aa plataforma
        """
        if 'usuario_logado' in self.request.session:
            return redirect('usuario:home')

        return super().get(*args, **kwargs)

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
                    return redirect('usuario:home')
                else:
                    print('não sei')  # I HAVE TO MAKE SOMETHING DIFFERENT HERE
            else:
                pass
                return super().post(*args, **kwargs)
        except Exception as e:
            print(f"Usuario não existe: {e}")

        return super().post(*args, **kwargs)


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

        return redirect('forum:forum')  # PRECISO ALTERAR AQUI!!!!


class DadosAtualizarView(View):
    template_name = 'usuario/atualizar_dados.html'

    def setup(self, *args, **kwargs):
        super().setup(*args, **kwargs)

        self.context = {
            'atualizar_pessoa': AtualizarPessoa(
                data=self.request.POST or None,
            ),
            'atualizar_endereco': AtualizarEndereco(
                data=self.request.POST or None,
            ),
        }

        self.atualizar_pessoa = self.context['atualizar_pessoa']
        self.atualizar_endereco = self.context['atualizar_endereco']
        self.renderizar = render(
            self.request, self.template_name, self.context
        )

    def get(self, *args, **kwargs):
        if not 'usuario_logado' in self.request.session:
            return redirect('usuario:login')
        return self.renderizar

    def post(self, *args, **kwargs):
        pessoa = Pessoa.objects.filter(
            id=self.request.session['usuario_logado']['pessoa_id']).first()
        Pessoa.objects.filter(
            id=self.request.session['usuario_logado']['pessoa_id']).update(
            nome=self.atualizar_pessoa.cleaned_data.get('nome') or pessoa.nome,
            sobrenome=self.atualizar_pessoa.cleaned_data.get(
                'sobrenome') or pessoa.sobrenome,
            celular=self.atualizar_pessoa.cleaned_data.get(
                'celular') or pessoa.celular,
            estado_civil=self.atualizar_pessoa.cleaned_data.get(
                'estado_civil') or pessoa.estado_civil,
            genero=self.atualizar_pessoa.cleaned_data.get(
                'genero') or pessoa.genero,
        )
        endereco = Endereco.objects.filter(
            id=pessoa.endereco.id
        ).first()
        Endereco.objects.filter(
            id=endereco.id).update(
                rua=self.atualizar_endereco.cleaned_data.get(
                    'rua') or endereco.rua,
                numero=self.atualizar_endereco.cleaned_data.get(
                    'numero') or endereco.numero,
                bairro=self.atualizar_endereco.cleaned_data.get(
                    'bairro') or endereco.bairro,
                cep=self.atualizar_endereco.cleaned_data.get(
                    'cep') or endereco.cep,
                cidade=self.atualizar_endereco.cleaned_data.get(
                    'cidade') or endereco.cidade,
                estado=self.atualizar_endereco.cleaned_data.get(
                    'estado') or endereco.estado,
                tipo_endereco=self.atualizar_endereco.cleaned_data.get(
                    'tipo_endereco') or endereco.tipo_endereco,
        )
        return self.renderizar


class SenhaAtualizarView(View):
    template_name = 'usuario/atualizar_senha.html'

    def setup(self, *args, **kwargs):
        super().setup(*args, **kwargs)

        self.renderizar = render(
            self.request, self.template_name)

    def get(self, *args, **kwargs):
        if not 'usuario_logado' in self.request.session:
            return redirect('usuario:login')
        return self.renderizar

    def post(self, *args, **kwargs):
        senha_antiga_1 = self.request.POST.get('senha_antiga_1')
        senha_antiga_2 = self.request.POST.get('senha_antiga_2')
        senha = self.request.POST.get('senha')

        if senha_antiga_1 != senha_antiga_2:
            print('Aqui preciso levantar algum chamado falando que não deu certo')
            return self.renderizar

        if bcrypt.checkpw(senha_antiga_1.encode('utf-8'), self.request.session['usuario_logado']['senha'].encode('utf-8')):

            Usuario.objects.filter(
                id=self.request.session['usuario_logado']['usuario_id']
            ).update(
                senha=str(bcrypt.hashpw(senha.encode(
                    'utf-8'), bcrypt.gensalt()))[2:-1]
            )
            return redirect('usuario:logout')
        return self.renderizar


class UsuarioAtualizarView(UpdateView):
    template_name = 'usuario/atualizar_usuario.html'
    model = Usuario
    form_class = AtualizarUsuario

    def get_success_url(self):
        return reverse('usuario:home')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)
