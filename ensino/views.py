from ast import AugAssign
from calendar import c
from re import M
from .models import EnvioAtividadeAula
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
from .models import ClassePalavra, AtividadeAula, Alternativa, Contexto, Atividade, UsuarioLingua
from .models import Lingua, AtividadeQuestao, Aula, NivelLingua, Palavra, AulaPalavra
from .models import PalavraContexto, EnvioAtividade, Questao


class LinguaCadastroView(FormView):
    template_name = 'ensino/cadastro/cadastro_lingua.html'
    form_class = LinguaCadastro

    def get(self, *args, **kwargs):
        if not "usuario_logado" in self.request.session:
            return redirect('usuario:login')

        if not self.request.session["usuario_logado"]["is_admin"]:
            return redirect('usuario:home')

        return super().get(*args, **kwargs)

    def get_success_url(self):
        return reverse('usuario:home')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class MenuLinguasView(ListView):
    template_name = 'ensino/menu.html'
    model = Lingua
    context_object_name = 'linguas'


class MenuLinguaView(DetailView):
    template_name = 'ensino/menu_lingua.html'
    model = Lingua

    def get(self, *args, **kwargs):
        if not 'usuario_logado' in self.request.session:
            return redirect('usuario:login')

        return super().get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        niveis = NivelLingua.objects.all().exclude(valor_nivel=0)
        context['niveis'] = {}
        for nivel in niveis:
            context['niveis'].update(
                {
                    nivel: Aula.objects.filter(
                        lingua=self.get_object(),
                        nivel=nivel,
                        is_licenced=False
                    )
                }
            )
        print(context['niveis'])
        # para restringir aulas nas quais usuario podera acessar no template
        nivel_usuario = NivelLingua.objects.filter(
            id__in=UsuarioLingua.objects.filter(
                usuario_id=self.request.session['usuario_logado']['usuario_id'],
                lingua=self.get_object()
            ).values('nivel_id')
        ).first()
        context['nivel_usuario'] = int(nivel_usuario.valor_nivel) + 1

        return context


class MenuLinguaNivelView(DetailView):
    template_name = 'ensino/modulo_nivel.html'
    model = NivelLingua
    context_object_name = 'nivel'

    def get(self, *args, **kwargs):
        self.lingua = get_object_or_404(
            Lingua, id=self.request.build_absolute_uri().split('/')[-2]
        )
        if not checa_nivel_aula_user(self.get_object(), self.request.session, self.lingua):
            return redirect('usuario:home')

        return super().get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['aulas'] = Aula.objects.filter(
            lingua=self.lingua,
            nivel=self.get_object(),
            is_licenced=True
        )
        context['lingua'] = self.lingua

        return context


class CadastraPalavraView(View):
    template_name = 'ensino/cadastro/cadastro_palavra.html'
    # model = Lingua

    def setup(self, *args, **kwargs):
        super().setup(*args, **kwargs)

        self.context = {
            'form': PalavraForms(
                data=self.request.POST or None,
            ),
        }

        self.renderizar = render(
            self.request, self.template_name, self.context)

    def get(self, *args, **kwargs):
        if not 'usuario_logado' in self.request.session:
            return redirect('usuario:login')
        return self.renderizar

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
                lingua=Lingua.objects.filter(
                    id=self.request.POST.get('lingua')
                ).first(),
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
                contexto=self.request.POST.get('contexto')
            ).save()
            Palavra.objects.filter(
                palavra=self.request.POST.get('palavra')
            ).first().contexto.add(
                Contexto.objects.filter(
                    contexto=self.request.POST.get('contexto')
                ).first()
            )
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

    def get(self, *args, **kwargs):
        if not 'usuario_logado' in self.request.session:
            return redirect('usuario:login')
        if not self.get_object().autor_aula.id == self.request.session['usuario_logado']['usuario_id']:
            return redirect('usuario:home')
        return super().get(*args, **kwargs)

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

    def get(self, *args, **kwargs):
        if not checa_nivel_aula_user(self.get_object().nivel, self.request.session, self.get_object().lingua):
            return redirect('usuario:home')
        return super().get(*args, **kwargs)

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

        # context['atividade_ja_enviada'] = EnvioAtividade.objects.filter(
        #     autor__id=self.request.session['usuario_logado']['usuario_id'],
        #     atividade__aula__id=self.object.id,
        # )
        context['atividade_aula'] = AtividadeAula.objects.filter(
            aula=self.get_object()
        ).first()
        context['atividade_concluida'] = EnvioAtividadeAula.objects.filter(
            autor__id=self.request.session['usuario_logado']['usuario_id'],
            atividade__aula=self.get_object(),
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
        palavras_aulas = Palavra.objects.filter(
            id__in=AulaPalavra.objects.filter(
                aula=self.get_object()
            ).values('palavra_id')
        )
        context['palavras_aula'] = {}
        for palavra in palavras_aulas:
            context['palavras_aula'].update(
                {
                    f'{palavra}': Contexto.objects.filter(
                        palavracontexto__palavra=palavra
                    ).order_by("?").first()
                }
            )
        return context


class TesteMeuPainelAulasView(View):
    template_name = 'ensino/meu_painel_aulas.html'

    def get(self, *args, **kwargs):
        if not "usuario_logado" in self.request.session:
            return redirect('usuario:login')

        context = {}
        linguas = Lingua.objects.filter(
            id__in=UsuarioLingua.objects.filter(
                usuario_id=self.request.session['usuario_logado']['usuario_id'],
            ).values('lingua_id')
        )
        niveis = NivelLingua.objects.all().exclude(valor_nivel=0)

        if self.request.session['usuario_logado']['is_licenced']:
            context['licenced_linguas'] = {}

        context['linguas'] = {}
        context['lista_questoes'] = {}
        # tentar fazer esse context ficar nulo caso nao tenha NENHUMA aula
        for lingua in linguas:
            context['linguas'].update(
                {
                    f'{lingua}': {}
                }
            )
            context['lista_questoes'].update(
                {
                    f'{lingua}': {}
                }
            )
            if 'licenced_linguas' in context:
                context['licenced_linguas'].update(
                    {
                        f'{lingua}': {}
                    }
                )
            for nivel in niveis:
                aulas = Aula.objects.filter(
                    lingua__lingua=lingua,
                    autor_aula__id=self.request.session['usuario_logado']['usuario_id'],
                    nivel=nivel,
                    is_licenced=False
                )
                if aulas:
                    context['linguas'][f'{lingua}'].update(
                        {
                            f'{nivel}': aulas
                        }
                    )
                if 'licenced_linguas' in context:
                    aulas = Aula.objects.filter(
                        lingua__lingua=lingua,
                        autor_aula__id=self.request.session['usuario_logado']['usuario_id'],
                        nivel=nivel,
                        is_licenced=True
                    )
                    if aulas:
                        context['licenced_linguas'][f'{lingua}'].update(
                            {
                                f'{nivel}': aulas
                            }
                        )
                questoes = Questao.objects.filter(
                    autor_id=self.request.session['usuario_logado']['usuario_id'],
                    nivel=nivel,
                    lingua=lingua,
                )
                if questoes:
                    context['lista_questoes'][f'{lingua}'].update(
                        {
                            f'{nivel}': questoes
                        }
                    )

            if not context['linguas'][f'{lingua}']:
                del context['linguas'][f'{lingua}']
            if not context['lista_questoes'][f'{lingua}']:
                del context['lista_questoes'][f'{lingua}']

            if 'licenced_linguas' in context:
                if not context['licenced_linguas'][f'{lingua}']:
                    del context['licenced_linguas'][f'{lingua}']

        return render(
            self.request, self.template_name, context
        )


class MeuPainelAulasView(ListView):
    """

    """
    template_name = 'ensino/meu_painel_aulas.html'
    model = Aula
    context_object_name = 'aulas'

    def get(self, *args, **kwargs):
        if not 'usuario_logado' in self.request.session:
            return redirect('usuario:login')
        print(Aula.objects.filter(
            autor_aula=self.request.session['usuario_logado']['usuario_id']
        ))
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
        formset = PalavraAulaForms()

        return self.render_to_response(
            {
                'add_palavra': formset,
                'aula': self.get_object(),
            },
        )

    def post(self, *args, **kwargs):
        formset = PalavraAulaForms(
            data=self.request.POST
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
        context['alternativas'] = seleciona_alternativas(self.get_object())

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


class TesteAdicionaAtividadeAula(DetailView):
    template_name = 'ensino/teste_adiciona_atividade.html'
    model = Aula

    def get_context_data(self, **kwargs):
        context = super(TesteAdicionaAtividadeAula,
                        self).get_context_data(**kwargs)
        context['aula'] = self.get_object()

        context['questoes_disponiveis'] = Questao.objects.filter(
            nivel=self.get_object().nivel,
            lingua=self.get_object().lingua
        )

        return context

    def post(self, *args, **kwargs):
        get_questoes = self.request.POST.getlist('questoes')
        atividade = AtividadeAula(
            aula=self.get_object()
        )
        atividade.save()
        for id_questao in get_questoes:
            questao = get_object_or_404(
                Questao, id=id_questao
            )
            AtividadeQuestao(
                atividade=atividade,
                questao=questao,
            ).save()
        return redirect('usuario:home')


class TesteResolucaoAtividade(DetailView):
    template_name = 'ensino/teste_atividade_aula.html'
    model = AtividadeAula

    def get_context_data(self, **kwargs):
        context = super(TesteResolucaoAtividade,
                        self).get_context_data(**kwargs)
        context['atividade'] = self.get_object()
        questoes = Questao.objects.filter(
            id__in=AtividadeQuestao.objects.filter(
                atividade=self.get_object(),
            ).values('questao_id')
        )
        context['lista_questoes'] = {}
        for questao in questoes:

            #  no template {questao.id} eh usado para name do input;
            # {questao.frase} para exibir a questao
            context['lista_questoes'].update(
                {
                    f'{questao.id}': {
                        f"{questao.frase}": seleciona_alternativas(questao),
                    }
                }
            )
        return context

    def post(self, *args, **kwargs):
        nota = checa_questoes(self.get_object(), self.request)
        cria_atividade(self.get_object(), nota, self.request.session)

        return redirect('usuario:home')


class TesteUpdateAtividadeConcluida(DetailView):
    template_name = 'ensino/teste_atividade_aula.html'
    model = EnvioAtividadeAula

    def get_context_data(self, **kwargs):
        context = super(TesteUpdateAtividadeConcluida,
                        self).get_context_data(**kwargs)
        context['atividade'] = self.get_object().atividade
        questoes = Questao.objects.filter(
            id__in=AtividadeQuestao.objects.filter(
                atividade=self.get_object().atividade,
            ).values('questao_id')
        )
        context['lista_questoes'] = {}
        for questao in questoes:

            #  no template {questao.id} eh usado para name do input;
            # {questao.frase} para exibir a questao
            context['lista_questoes'].update(
                {
                    f'{questao.id}': {
                        f"{questao.frase}": seleciona_alternativas(questao),
                    }
                }
            )
        return context

    def post(self, *args, **kwargs):

        nota = checa_questoes(self.get_object().atividade, self.request)
        print(nota)
        # abaixo eh regra de negocio
        if nota >= self.get_object().nota:
            EnvioAtividadeAula.objects.filter(
                pk=self.get_object().id).update(
                aprovado=True,
                nota=nota
            )
            if self.get_object().atividade.aula.is_licenced:
                checa_nivel_lingua(
                    self.get_object().atividade, self.request.session)
        else:
            print('deu errado =(')
            pass

        return redirect('usuario:home')


# SERVICES
def checa_nivel_aula_user(nivel, request, lingua):
    nivel_usuario = UsuarioLingua.objects.filter(
        lingua=lingua,
        usuario__id=request['usuario_logado']['usuario_id']
    ).first()
    if (nivel_usuario.nivel.valor_nivel + 1) < nivel.valor_nivel:
        return False
    return True


def seleciona_alternativas(questao):
    print(questao)
    correta = Alternativa.objects.filter(
        questao=questao,
        is_correct=True,
    ).all().order_by('?').first()
    erradas = Alternativa.objects.filter(
        questao=questao,
        is_correct=False,
    ).all().order_by('?')[:4]
    alternativas = list()
    for errada in erradas:
        alternativas.append(errada)
    alternativas.append(correta)
    random.shuffle(alternativas)
    return alternativas


def checa_nivel_lingua(atividade, request):
    print('checa nivel')
    qtd_licenced = AtividadeAula.objects.filter(
        aula__is_licenced=True,
        aula__nivel=atividade.aula.nivel,
        aula__lingua=atividade.aula.lingua,
    ).count()
    qtd_approved = EnvioAtividadeAula.objects.filter(
        autor_id=request['usuario_logado']['usuario_id'],
        aprovado=True,
        atividade__aula__is_licenced=True,
        atividade__aula__nivel=atividade.aula.nivel,
        atividade__aula__lingua=atividade.aula.lingua,
    ).count()
    if qtd_licenced == qtd_approved:
        nivel_usuario = UsuarioLingua.objects.filter(
            usuario__id=request['usuario_logado']['usuario_id'],
            lingua=atividade.aula.lingua
        )
        if nivel_usuario.first().nivel.valor_nivel < atividade.aula.nivel.valor_nivel:
            nivel_usuario.update(
                nivel=atividade.aula.nivel
            )


def cria_atividade(atividade, nota, request):
    if nota >= 70.0:
        EnvioAtividadeAula(
            autor_id=request['usuario_logado']['usuario_id'],
            atividade=atividade,
            aprovado=True,
            nota=nota,
        ).save()
        if atividade.aula.is_licenced:
            checa_nivel_lingua(atividade, request)
    else:
        EnvioAtividadeAula(
            autor_id=request['usuario_logado']['usuario_id'],
            atividade=atividade,
            aprovado=False,
            nota=nota,
        ).save()


def checa_questoes(atividade, request):
    questoes = Questao.objects.filter(
        id__in=AtividadeQuestao.objects.filter(
            atividade=atividade,
        ).values('questao_id')
    )
    certas = int(0)
    for questao in questoes:
        alternativa_entrada = request.POST.get(f'{questao.id}')
        certo = Alternativa.objects.filter(
            alternativa=alternativa_entrada,
            questao=questao,
            is_correct=True,
        ).first()
        if certo:
            certas += 1

    return round((certas * 100) / (questoes.count()), 2)


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
