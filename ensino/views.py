import random
from django.views.generic import TemplateView
from .forms import *
from django.http import HttpResponseRedirect
from django.views import View
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView
from django.views.generic import FormView
from django.views.generic.detail import DetailView
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from usuario.models import Usuario
from .models import ClassePalavra, AtividadeAula, Alternativa, Contexto, Atividade, Lingua, AtividadeQuestao, Aula, NivelLingua, Palavra, PalavraContexto, EnvioAtividade, Questao


class LinguaCadastroView(FormView):
    template_name = 'ensino/cadastro/cadastro_lingua.html'
    form_class = LinguaCadastro

    def get_success_url(self):
        return reverse('usuario:home')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

#


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
        context['niveis'] = {}
        for i in context['range']['range']:
            context['niveis'].update(
                {
                    f'{i}': Aula.objects.filter(
                        lingua=self.get_object(),
                        nivel__valor_nivel=i,
                        is_licenced=False)
                }
            )

        # for i in range(1, 6):
        #     print(context[f'aulas_{i}'])

        return context


class MenuLinguaNivelView(DetailView):
    template_name = 'ensino/modulo_nivel.html'
    model = NivelLingua

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['aulas'] = Aula.objects.filter(
            lingua=get_object_or_404(
                Lingua, id=self.request.build_absolute_uri().split('/')[-2]
            ),
            nivel=self.get_object(),
            is_licenced=True
        )

        return context


class CadastraPalavraView(DetailView):
    template_name = 'ensino/cadastro/cadastro_palavra.html'
    model = Lingua

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PalavraForms(
            data=self.request.POST or None,
        )

        return context

    def get(self, *args, **kwargs):
        if not 'usuario_logado' in self.request.session:
            return redirect('usuario:login')
        return super().get(self, *args, **kwargs)

    def post(self, *args, **kwargs):
        palavra = Palavra.objects.filter(
            palavra=self.request.POST.get('palavra')
        ).first()
        if palavra:

            Contexto(
                contexto=self.request.POST.get('contexto')).save()
            contexto = Contexto.objects.filter(
                contexto=self.request.POST.get('contexto')
            ).first()
            palavra.contexto.add(contexto)
            return HttpResponseRedirect(self.request.path_info)
        else:
            Palavra(
                palavra=self.request.POST.get('palavra'),
                lingua=self.get_object(),
                classe=ClassePalavra.objects.filter(
                    id=self.request.POST.get('classe')
                ).first(),
                significado=self.request.POST.get('significado'),
                nivel=NivelLingua.objects.filter(
                    id=self.request.POST.get('nivel')
                ).first(),
                escrita_fonetica=self.request.POST.get('escrita_fonetica')
            ).save()
            Contexto(
                contexto=self.request.POST.get('contexto')).save()
            Palavra.objects.filter(
                palavra=self.request.POST.get('palavra')
            ).first().contexto.add(Contexto.objects.filter(
                contexto=self.request.POST.get('contexto')
            ).first())
            return HttpResponseRedirect(self.request.path_info)


class LinguaDicionarioView(DetailView):
    template_name = 'ensino/dicionario_lingua.html'
    model = Lingua

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['palavras'] = Palavra.objects.filter(
            lingua=self.get_object()
        )

        return context


class PalavraView(DetailView):
    template_name = 'ensino/palavra.html'
    model = Palavra

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['contextos'] = Contexto.objects.filter(
            id__in=PalavraContexto.objects.filter(
                palavra=self.get_object()
            ).values('contexto_id')
        )

        return context


class AulaCadastroView(View):
    """
    View com dois forms: de criar aula e de criar atividade
    """
    template_name = 'ensino/cadastro/cadastro_aula.html'

    def setup(self, *args, **kwargs):
        super().setup(*args, **kwargs)

        # contexto com os dois forms
        self.context = {
            'criar_aula': CriarAulaForms(
                data=self.request.POST or None,
                files=self.request.FILES or None,
            ),
            'criar_atividade': CriarAtividadeForms(
                data=self.request.POST or None,
                files=self.request.FILES or None,
            ),
        }

        # atribuidas variaveis para utilizar no post
        self.criar_aula = self.context['criar_aula']
        self.criar_atividade = self.context['criar_atividade']

        self.renderizar = render(
            self.request, self.template_name, self.context
        )

    def get(self, *args, **kwargs):
        if not 'usuario_logado' in self.request.session:
            return redirect('usuario:login')

        # if not self.request.session['usuario_logado']['tipo_usuario_id'] == 3:
        #     return redirect('departamento:home')
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
        print()
        if self.request.session['usuario_logado']['is_licenced']:
            aula.is_licenced = self.request.POST.get('is_licenced') == 'on'

        aula.save()

        # cadastra atividade
        atividade = self.criar_atividade.save(commit=False)
        atividade.autor = autor
        atividade.aula = aula
        atividade.save()

        return redirect('usuario:home')


class AtualizarAulaView(UpdateView):
    """
    View para atualizacao de aula
    """
    template_name = 'ensino/atualizar_aula.html'
    model = Aula
    form_class = AtualizarAulaForms

    def get_success_url(self):
        return reverse('usuario:home')

    def get_context_data(self, **kwargs):

        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        att_aula = form.save(commit=False)
        att_aula.aula = form.cleaned_data.get('aula') or self.get_object().aula
        att_aula.conteudo = form.cleaned_data.get(
            'conteudo') or self.get_object().conteudo
        form.save()

        return super().form_valid(form)


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

        context['atividade_ja_enviada'] = EnvioAtividade.objects.filter(
            autor__id=self.request.session['usuario_logado']['usuario_id'],
            atividade__aula__id=self.object.id,
        )
        context['teste_atividade_nova'] = AtividadeAula.objects.filter(
            aula=self.get_object()
        ).first()
        context['aulas'] = Aula.objects.filter(
            nivel=self.get_object().nivel,
            lingua=self.get_object().lingua
        )
        if self.get_object().is_licenced:
            context['aulas'] = context['aulas'].filter(
                is_licenced=True
            )
        else:
            context['aulas'] = context['aulas'].filter(
                is_licenced=False
            )[:10]

        return context


class TesteAtividadeAulaView(DetailView):
    template_name = 'ensino/teste_atividade_aula.html'
    model = AtividadeAula

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['atividade'] = self.get_object()
        context['questoes'] = Questao.objects.filter(
            id__in=AtividadeQuestao.objects.filter(
                atividade=self.get_object()
            ).values('questao_id')
        )
        return context


class MeuPainelAulasView(ListView):
    """
    View de exibicao de aulas, usuario com permissao eh professor
    Iguala o modulo aberto a None para para restrigir telas posteriores
    """
    template_name = 'ensino/meu_painel_aulas.html'
    model = Aula
    context_object_name = 'aulas'

    def get(self, *args, **kwargs):
        if not 'usuario_logado' in self.request.session:
            print('usuario deslogado')
            return redirect('usuario:login')

        return super().get(self, *args, **kwargs)

    def get_queryset(self):
        queryset = Aula.objects.filter(
            autor_aula=self.request.session['usuario_logado']['usuario_id']
        )
        return queryset


class AtividadeUsuarioCadastroView(DetailView, FormView):
    template_name = 'ensino/cadastro/cadastro_atividade_usuario.html'
    model = Atividade
    form_class = AtividadeEnviadaForms

    def get(self, *args, **kwargs):
        if not 'usuario_logado' in self.request.session:
            return redirect('usuario:login')

        return super().get(*args, **kwargs)

    def get_success_url(self):
        return reverse('ensino:menu_linguas')

    def post(self, request, *args, **kwargs):
        if not self.request.session['usuario_logado']:
            return HttpResponseForbidden()
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        # cadastra envio de atividade
        enviar_atividade = form.save(commit=False)
        enviar_atividade.autor = get_object_or_404(
            Usuario, id=self.request.session['usuario_logado']['usuario_id']
        )
        enviar_atividade.atividade = self.get_object()
        enviar_atividade.save()
        return super().form_valid(form)


class AtividadeAlunoAtualizarView(UpdateView):
    template_name = 'ensino/atualizar_atividade.html'
    model = EnvioAtividade
    form_class = AtualizarAtividadeAluno

    def get(self, *args, **kwargs):
        if not 'usuario_logado' in self.request.session:
            return redirect('usuario:login')

        return super().get(*args, **kwargs)

    def get_success_url(self):
        return reverse('usuario:home')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class TesteAdicionaPalavraAula(TemplateView, DetailView):
    template_name = 'ensino/teste_add_palavra.html'
    model = Aula

    def get(self, *args, **kwargs):
        formset = PalavraAulaForms(
            queryset=Palavra.objects.none(),
        )
        return self.render_to_response(
            {
                'add_palavra': formset,
                'aula': self.get_object(),
            },
        )

    def post(self, *args, **kwargs):
        formset = PalavraAulaForms(
            data=self.request.POST,
        )
        if formset.is_valid():
            forms = formset.save(commit=False)
            for form in forms:
                form.aula = self.get_object()
                form.save()
            return redirect(reverse_lazy('usuario:home'))

        return self.render_to_response({'add_palavra': formset})


class TesteCriaQuestao(TemplateView):
    template_name = 'ensino/teste_questao.html'

    def get(self, *args, **kwargs):
        formset = AlternativasQuestaoFormset(
            queryset=Palavra.objects.none(),
        )
        form = QuestaoForms()
        return self.render_to_response(
            {
                'add_questao': form,
                'add_alternativa': formset,
            },
        )

    def post(self, *args, **kwargs):
        formset = AlternativasQuestaoFormset(
            data=self.request.POST,
        )
        form = QuestaoForms(
            data=self.request.POST,
        )
        if formset.is_valid() and form.is_valid():
            print('está valido')
            questao = form.save(commit=False)
            questao.autor = get_object_or_404(
                Usuario, id=self.request.session['usuario_logado']['usuario_id']
            )
            questao.save()
            alternativas = formset.save(commit=False)
            for alternativa in alternativas:
                alternativa.questao = questao
                alternativa.save()
            return redirect(reverse_lazy('usuario:home'))

        return self.render_to_response(
            {
                'add_questao': form,
                'add_alternativa': formset,
            },
        )


class TesteResolucaoQuestao(DetailView):
    template_name = 'ensino/teste_resolucao.html'
    model = Questao

    def get_context_data(self, **kwargs):
        context = super(TesteResolucaoQuestao, self).get_context_data(**kwargs)
        context['questao'] = self.get_object()
        correta = Alternativa.objects.filter(
            questao=self.get_object(),
            is_correct=True,
        ).all().order_by('?').first()
        erradas = Alternativa.objects.filter(
            questao=self.get_object(),
            is_correct=False,
        ).all().order_by('?')[:4]
        alternativas = list()
        for errada in erradas:
            alternativas.append(errada)
        alternativas.append(correta)
        random.shuffle(alternativas)
        context['alternativas'] = alternativas

        return context

    def post(self, *args, **kwargs):
        alternativa_entrada = self.request.POST.get('alternativa')
        certo = Alternativa.objects.filter(
            alternativa=alternativa_entrada,
            questao=self.get_object(),
            is_correct=True,
        ).first()
        if not certo:
            print('errado')
        else:
            print('certo')

        return redirect('usuario:home')

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
