from .forms import *
from typing import List
from django.http import HttpResponseRedirect
from django.views import View
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView
from django.views.generic import FormView
from django.views.generic.detail import SingleObjectMixin, DetailView
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from usuario.models import Usuario
from .models import ClassePalavra, Contexto, Administrador, Atividade, Lingua, Aula
# from .forms import *
# from pessoa.models import Endereco, Pessoa, TipoUsuario, Usuario
# from pessoa.forms import PessoaCadastro, EnderecoCadastro, AtualizarPessoa, AtualizarEndereco, AtualizarSenha
import bcrypt


class MenuLinguasView(ListView):
    template_name = 'ensino/menu.html'
    model = Lingua
    context_object_name = 'linguas'


class MenuLinguaView(DetailView):
    template_name = 'ensino/menu_lingua.html'
    model = Lingua

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['range'] = {'range': range(1, 6)}
        for i in context['range']['range']:
            context[f"aulas_{i}"] = Aula.objects.filter(
                lingua=self.get_object(),
                nivel__valor_nivel=i
            )

        for i in range(1, 6):
            print(context[f'aulas_{i}'])

        return context


class AulaCadastroView(DetailView):
    """
    View com dois forms: de criar aula e de criar atividade
    """
    template_name = 'ensino/cadastro/cadastro_aula.html'
    model = Lingua

    def setup(self, *args, **kwargs):
        super().setup(*args, **kwargs)

        # contexto com os dois forms
        self.context = {
            'criar_aula': CriarAulaForms(
                data=self.request.POST or None,
                files=self.request.FILES or None,
            ),
            # 'criar_atividade': CriarAtividadeForms(
            #     data=self.request.POST or None,
            #     files=self.request.FILES or None,
            # ),
        }

        # atribuidas variaveis para utilizar no post
        self.criar_aula = self.context['criar_aula']
        # self.criar_atividade = self.context['criar_atividade']

        self.renderizar = render(
            self.request, self.template_name, self.context
        )

    def get(self, *args, **kwargs):
        # if not 'usuario_logado' in self.request.session:
        #     print('usuario deslogado')
        #     return redirect('departamento:login')

        # if not self.request.session['usuario_logado']['tipo_usuario_id'] == 3:
        #     return redirect('departamento:home')
        print(self.get_object())
        return self.renderizar

    def post(self, *args, **kwargs):
        if not self.criar_aula.is_valid():
            return self.renderizar

        # cadastra professor
        autor = get_object_or_404(
            Usuario, id=self.request.session['usuario_logado']['usuario_id']
        )
        aula = self.criar_aula.save(commit=False)
        aula.autor_aula = autor
        aula.lingua = self.get_object()
        aula.save()

        # cadastra atividade
        # atividade = self.criar_atividade.save(commit=False)
        # atividade.professor = professor
        # atividade.aula = aula
        # atividade.save()

        return redirect('usuario:home')


class AulaView(DetailView):
    """
    View que sera utilizada em metodo get de view principal
    criada para juntar informacoes de uma aula em especifico junto de um forms
    Em seu metodo get_context_data eh envaido um formulario diferente para cada
    tipo de usuario
    """
    template_name = 'ensino/aula.html'
    model = Aula
    context_object_name = 'aula'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # if self.request.session['usuario_logado']['tipo_usuario_id'] == 3:

        #     context['professor_responsavel'] = Professor.objects.filter(
        #         id=self.object.aula.professor_id).first()
        #     context['form'] = AtividadePostagemForms  # VERIFICAR ISSO DEPOIS
        #     context['alunos_matriculados'] = Aluno.objects.filter(
        #         modulo__id=self.object.modulo.id
        #     )
        # elif self.request.session['usuario_logado']['tipo_usuario_id'] == 1:

        #     context['atividade_ja_enviada'] = EnvioAtividade.objects.filter(
        #         aluno__id=self.request.session['usuario_logado']['aluno_id'],
        #         atividade__aula__id=self.object.aula.id,
        #     )
        # context['aulas_modulo'] = get_object_or_404(
        #     Modulo, id=self.get_object().modulo.id
        # ).aulas.all()
        return context


# class MeuPainelView(View):
#     """
#     Classe da view de entrada.
#     Nesta view eh separado os modulos que determinado usuario pode ter acesso.
#     Caso ele seja aluno, os modulos matriculados, caso seja professor, os modulos
#     vinculados a ele.
#     """
#     template_name = 'departamento/meu_painel.html'

#     def setup(self, *args, **kwargs):
#         super().setup(*args, **kwargs)

#         self.renderizar = render(
#             self.request, self.template_name
#         )

#     def get(self, *args, **kwargs):
#         if not 'usuario_logado' in self.request.session:
#             print('usuario deslogado')
#             return redirect('departamento:login')

#         if self.request.session['usuario_logado']['tipo_usuario_id'] == 1:
#             aluno = get_object_or_404(
#                 Aluno, id=self.request.session['usuario_logado']['aluno_id']
#             )
#             self.modulo_list = {
#                 'modulos_ingles': aluno.modulo.filter(
#                     lingua=1
#                 ),
#                 'modulos_alemão': aluno.modulo.filter(
#                     lingua=2
#                 ),
#                 'modulos_noruegues': aluno.modulo.filter(
#                     lingua=3
#                 )
#             }

#             self.renderizar = render(
#                 self.request, self.template_name, self.modulo_list
#             )
#             return self.renderizar

#         elif self.request.session['usuario_logado']['tipo_usuario_id'] == 3:
#             # VIEW DO PROFESSOR
#             # separa os modulos ao qual usuario esta vinculado
#             professor = get_object_or_404(
#                 Professor, pessoa_id=self.request.session['usuario_logado']['pessoa_id']
#             )

#             # modulos vinculado
#             modulos = professor.modulo.all()
#             self.modulo_list = {
#                 'modulos': modulos
#             }
#             # sobrescreve self.renderizar
#             self.renderizar = render(
#                 self.request, self.template_name, self.modulo_list
#             )
#             return self.renderizar

#         return self.renderizar

#     def post(self, *args, **kwargs):
#         return self.renderizar

# # VIEW DA AULA #


# class AulaCadastroView(View):
#     """
#     View com dois forms: de criar aula e de criar atividade
#     """
#     template_name = 'departamento/cadastro/cadastro_aula.html'

#     def setup(self, *args, **kwargs):
#         super().setup(*args, **kwargs)

#         # contexto com os dois forms
#         self.context = {
#             'criar_aula': CriarAulaForms(
#                 data=self.request.POST or None,
#                 files=self.request.FILES or None,
#             ),
#             'criar_atividade': CriarAtividadeForms(
#                 data=self.request.POST or None,
#                 files=self.request.FILES or None,
#             ),
#         }

#         # atribuidas variaveis para utilizar no post
#         self.criar_aula = self.context['criar_aula']
#         self.criar_atividade = self.context['criar_atividade']
#         self.renderizar = render(
#             self.request, self.template_name, self.context
#         )

#     def get(self, *args, **kwargs):
#         if not 'usuario_logado' in self.request.session:
#             print('usuario deslogado')
#             return redirect('departamento:login')

#         if not self.request.session['usuario_logado']['tipo_usuario_id'] == 3:
#             return redirect('departamento:home')
#         return self.renderizar

#     def post(self, *args, **kwargs):
#         if not self.criar_aula.is_valid() or not self.criar_atividade.is_valid():
#             return self.renderizar

#         # cadastra professor
#         professor = get_object_or_404(
#             Professor, id=self.request.session['usuario_logado']['professor_id']
#         )
#         aula = self.criar_aula.save(commit=False)
#         aula.professor = professor
#         aula.save()

#         # cadastra atividade
#         atividade = self.criar_atividade.save(commit=False)
#         atividade.professor = professor
#         atividade.aula = aula
#         atividade.save()

#         return redirect('departamento:home')

# # atualizar aqui


# class AulaProfessorView(DetailView):
#     template_name = 'departamento/aula_professor.html'
#     model = Aula
#     context_object_name = 'aula'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['form'] = AtualizarAulaForms
#         return context


# class AtualizarAulaView(UpdateView):
#     """
#     View para atualizacao de aula
#     """
#     template_name = 'departamento/aula_professor.html'
#     model = Aula
#     form_class = AtualizarAulaForms

#     def get_success_url(self):
#         return reverse('departamento:home')

#     def get_context_data(self, **kwargs):

#         return super().get_context_data(**kwargs)

#     def form_valid(self, form):
#         att_aula = form.save(commit=False)
#         att_aula.aula = form.cleaned_data.get('aula') or self.get_object().aula
#         att_aula.conteudo = form.cleaned_data.get(
#             'conteudo') or self.get_object().conteudo
#         form.save()

#         return super().form_valid(form)


# class ProfessorAulaView(View):
#     model = Aula

#     def get(self, request, *args, **kwargs):
#         if not 'usuario_logado' in self.request.session:
#             print('usuario deslogado')
#             return redirect('departamento:login')

#         if not self.request.session['usuario_logado']['tipo_usuario_id'] == 3:
#             return redirect('departamento:home')

#         view = AulaProfessorView.as_view()
#         return view(request, *args, **kwargs)

#     def post(self, request, *args, **kwargs):
#         if self.request.session['usuario_logado']['tipo_usuario_id'] == 3:
#             view = AtualizarAulaView.as_view()
#         return view(request, *args, **kwargs)


# class AulaRegistraModuloView(FormView):
#     """
#     View para vincular uma ou mais aulas a um modulo
#     """
#     template_name = 'departamento/registra_aula_modulo.html'
#     # model = AulaVinculaModulo
#     form_class = VinculaAulaModulo

#     def get(self, *args, **kwargs):
#         if not 'usuario_logado' in self.request.session:
#             print('usuario deslogado')
#             return redirect('departamento:login')

#         if not self.request.session['usuario_logado']['tipo_usuario_id'] == 3:
#             return redirect('departamento:home')

#         return super().get(*args, **kwargs)

#     def get_success_url(self):
#         return reverse('departamento:home')

#     def get_form_kwargs(self, *args, **kwargs):
#         kwargs = super(AulaRegistraModuloView,
#                        self).get_form_kwargs(*args, **kwargs)
#         kwargs['request'] = self.request.session['usuario_logado']
#         return kwargs

#     def form_valid(self, form):  # AQUI PRECISO ARRUMAR.
#         """
#         Funcao para cadastrar varias aulas a um modulo, caso o usuario solicite
#         """
#         # parte da regra de negocio (um professor pode ter apenas 5 atividades em modulo)
#         aula_total = Aula.objects.filter(
#             professor__id=self.request.session['usuario_logado']['professor_id'],
#             modulo=form.cleaned_data.get('modulo')
#         )
#         aulas_lista = Aula.objects.filter(
#             pk__in=form.cleaned_data.get('aulas')
#         )
#         if len(aula_total) >= 5 or len(aula_total) + len(aulas_lista) > 5:
#             return super().form_valid(form)
#         # # # #
#         qtd_aula_modulo = AulaVinculaModulo.objects.filter(
#             modulo=form.cleaned_data.get('modulo')
#         ).count()

#         # RN
#         if qtd_aula_modulo >= 20:
#             return super().form_valid(form)
#         #
#         # loop para cadastrar as aulas em um modulo
#         for aula in aulas_lista:
#             instancia = AulaVinculaModulo(
#                 modulo=form.cleaned_data.get('modulo'),
#                 aula=aula
#             )
#             instancia.save()
#         return super().form_valid(form)


# class MeuPainelAulasView(ListView):
#     """
#     View de exibicao de aulas, usuario com permissao eh professor
#     Iguala o modulo aberto a None para para restrigir telas posteriores
#     """
#     template_name = 'departamento/meu_painel_aulas.html'
#     model = Aula
#     context_object_name = 'aulas'

#     def get(self, *args, **kwargs):
#         if not 'usuario_logado' in self.request.session:
#             print('usuario deslogado')
#             return redirect('departamento:login')

#         # ANALSIAR ESSA POSSIBILDIADE
#         if not 'professor_id' in self.request.session['usuario_logado']:
#             return redirect('departamento:home')

#         return super().get(self, *args, **kwargs)

#     def get_queryset(self):
#         queryset = Aula.objects.filter(
#             professor_id=self.request.session['usuario_logado']['professor_id'])
#         return queryset

#         # PRECISO ATRIBUIR RESTRICOES AINDA


# class ModuloView(DetailView):
#     """
#     Tela que exibe modulos do usuario
#     """
#     template_name = 'departamento/modulo.html'
#     model = Modulo
#     context_object_name = 'modulo'

#     def get(self, *args, **kwargs):
#         if not 'usuario_logado' in self.request.session:
#             print('usuario deslogado')
#             return redirect('departamento:login')

#         if not 'aluno_id' in self.request.session['usuario_logado'] and not 'professor_id' in self.request.session['usuario_logado']:
#             return redirect('departamento:home')

#         return super().get(*args, **kwargs)

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         # query para selecionar alunos matriculados em determinado modulo
#         if self.request.session['usuario_logado']['tipo_usuario_id'] == 3:
#             context['alunos_matriculados'] = Aluno.objects.filter(
#                 modulo=self.get_object())

#         # query com todas as aulas do modulo selecionado
#         context['aulas_modulo'] = self.get_object().aulas.all()  # rever aqui
#         return context


# # ACIMA É O NOVO #

# class ModuloAulaView(DetailView):
#     """
#     View que sera utilizada em metodo get de view principal
#     criada para juntar informacoes de uma aula em especifico junto de um forms
#     Em seu metodo get_context_data eh envaido um formulario diferente para cada
#     tipo de usuario
#     """
#     template_name = 'departamento/modulo_aula.html'
#     model = AulaVinculaModulo
#     context_object_name = 'aula'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         if self.request.session['usuario_logado']['tipo_usuario_id'] == 3:

#             context['professor_responsavel'] = Professor.objects.filter(
#                 id=self.object.aula.professor_id).first()
#             context['form'] = AtividadePostagemForms  # VERIFICAR ISSO DEPOIS
#             context['alunos_matriculados'] = Aluno.objects.filter(
#                 modulo__id=self.object.modulo.id
#             )
#         elif self.request.session['usuario_logado']['tipo_usuario_id'] == 1:

#             context['atividade_ja_enviada'] = EnvioAtividade.objects.filter(
#                 aluno__id=self.request.session['usuario_logado']['aluno_id'],
#                 atividade__aula__id=self.object.aula.id,
#             )
#         context['aulas_modulo'] = get_object_or_404(
#             Modulo, id=self.get_object().modulo.id
#         ).aulas.all()
#         return context


# class AtividadeAlunoCadastroView(DetailView, FormView):
#     template_name = 'departamento/cadastro/cadastro_atividade_aluno.html'
#     model = Atividade
#     form_class = AtividadeEnviadaForms

#     def get(self, *args, **kwargs):
#         if not 'usuario_logado' in self.request.session:
#             return redirect('departamento:login')

#         if not 'aluno_id' in self.request.session['usuario_logado']:
#             return redirect('departamento:home')

#         return super().get(*args, **kwargs)

#     def get_success_url(self):
#         return reverse('departamento:home')

#     def post(self, request, *args, **kwargs):
#         if not self.request.session['usuario_logado']:
#             return HttpResponseForbidden()
#         self.object = self.get_object()
#         return super().post(request, *args, **kwargs)

#     def form_valid(self, form):
#         # cadastra envio de atividade
#         enviar_atividade = form.save(commit=False)
#         enviar_atividade.aluno = get_object_or_404(
#             Aluno, id=self.request.session['usuario_logado']['aluno_id']
#         )
#         enviar_atividade.atividade = self.get_object()
#         enviar_atividade.save()
#         return super().form_valid(form)


# class AtividadeAlunoAtualizarView(UpdateView):
#     template_name = 'departamento/atualizar_atividade.html'
#     model = EnvioAtividade
#     form_class = AtualizarAtividadeAluno

#     def get(self, *args, **kwargs):
#         if not 'usuario_logado' in self.request.session:
#             return redirect('departamento:login')

#         if not 'aluno_id' in self.request.session['usuario_logado']:
#             return redirect('departamento:home')

#         return super().get(*args, **kwargs)

#     def get_success_url(self):
#         return reverse('departamento:home')

#     def form_valid(self, form):
#         form.save()
#         return super().form_valid(form)


# class AulaView(SingleObjectMixin, View):
#     """
#     View principal da aula, recebe duas views diferentes, a depender do metodo
#     get: view AulaModuloDetailView
#     post: a depender do usuario logado, AtualizaAula caso seja professor,
#     AtividadeEnviada caso seja aluno
#     """
#     model = AulaVinculaModulo

#     def get(self, request, *args, **kwargs):
#         if not 'usuario_logado' in self.request.session:
#             return redirect('departamento:login')

#         if not 'aluno_id' in self.request.session['usuario_logado'] and not 'professor_id' in self.request.session['usuario_logado']:
#             return redirect('departamento:home')

#         view = ModuloAulaView.as_view()
#         return view(request, *args, **kwargs)

#     def post(self, request, *args, **kwargs):
#         # REVER ISSO AQUI
#         if self.request.session['usuario_logado']['tipo_usuario_id'] == 3:
#             view = AtualizarAulaView.as_view()
#             return view(request, *args, **kwargs)
#             # esse aqui muda, ja que nao iremos mais passar um form de postagem de atv

#         return view(request, *args, **kwargs)


# class AtividadeRecebidaView(DetailView):
#     template_name = 'departamento/atividade.html'
#     model = Aula
#     context_object_name = 'aula'

#     def get(self, *args, **kwargs):
#         if not 'usuario_logado' in self.request.session:
#             print('aqui')
#             return redirect('departamento:login')

#         if not 'professor_id' in self.request.session['usuario_logado']:
#             return redirect('departamento:home')

#         return super().get(*args, **kwargs)

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['atividades_enviadas_n_ava'] = EnvioAtividade.objects.filter(
#             atividade__aula=self.get_object(),
#             atividade__aula__professor_id=self.request.session['usuario_logado']['professor_id'],
#             nota=None,
#             envio_definitivo=True,
#         )
#         return context


# class AtividadeNotaCadastroView(DetailView, UpdateView):
#     template_name = 'departamento/cadastro/cadastro_nota_atividade.html'
#     model = EnvioAtividade
#     context_object_name = 'atividade_enviada'
#     slug_url_kwarg = 'id'
#     form_class = AtribuiNotaAtividadeForms

#     def get(self, *args, **kwargs):
#         if not 'usuario_logado' in self.request.session:
#             print('aqui')
#             return redirect('departamento:login')

#         if not 'professor_id' in self.request.session['usuario_logado']:
#             return redirect('departamento:home')

#         return super().get(*args, **kwargs)

#     def get_success_url(self):
#         return reverse('departamento:home')
