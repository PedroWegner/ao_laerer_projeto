from django.forms.models import model_to_dict
import os
from django.core.files.base import ContentFile
from django.conf import settings
from django.core.files.storage import default_storage
from datetime import date
from utils.services_ensino import *
from utils.validate_form import form_html_validated
from utils.send_messages import send_message_success, send_message_error, send_message_info
from django.db.models import Q
from django.views.generic import TemplateView
from .forms import *
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.views import View
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView
from django.views.generic import FormView
from django.views.generic.detail import DetailView
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from usuario.models import Usuario
from .models import ClassePalavra, AtividadeAula, Alternativa, Contexto, ModuloLinguaNivel,\
    UsuarioLingua, Lingua, AtividadeQuestao, Aula, NivelLingua, Palavra, \
    AulaPalavra, PalavraContexto, Questao, EnvioAtividadeAula


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
        send_message_success(self.request, "Língua adicionada")
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
        context['modulos'] = ModuloLinguaNivel.objects.filter(
            lingua=self.get_object()
        )
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
        nivel_usuario = NivelLingua.objects.filter(
            id__in=UsuarioLingua.objects.filter(
                usuario_id=self.request.session['usuario_logado']['usuario_id'],
                lingua=self.get_object()
            ).values('nivel_id')
        ).first()
        context['nivel_usuario'] = int(nivel_usuario.valor_nivel) + 1

        return context


class ModuloView(DetailView):
    template_name = 'ensino/modulo.html'
    model = ModuloLinguaNivel
    context_object_name = 'modulo'

    def get(self, *args, **kwargs):
        if not checa_nivel_aula_user(self.get_object().nivel, self.request.session, self.get_object().lingua):
            send_message_info(self.request, 'Você não pode estar aqui!!')
            return redirect('usuario:home')

        return super().get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['aulas'] = Aula.objects.filter(
            lingua=self.get_object().lingua,
            nivel=self.get_object().nivel,
            is_licenced=True
        )
        palavras = Palavra.objects.filter(
            id__in=AulaPalavra.objects.filter(
                aula__id__in=Aula.objects.filter(
                    modulo=self.get_object()
                )
            ).values('palavra_id').distinct().order_by('?')[:10])
        context['palavras_modulo'] = get_palavracontexto(palavras)
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
        palavra_bd = Palavra.objects.filter(
            palavra=self.request.POST.get('palavra')
        ).first()
        palavra = self.request.POST.get('palavra')
        contexto = self.request.POST.get('contexto')
        lingua = self.request.POST.get('lingua')
        significado = self.request.POST.get('significado')
        classe_mor = self.request.POST.get('classe')
        nivel = self.request.POST.get('nivel')
        escrita_fonetica = self.request.POST.get('escrita_fonetica')
        if palavra_bd:
            Contexto(
                contexto=contexto).save()
            contexto = Contexto.objects.filter(
                contexto=contexto
            ).first()
            palavra_bd.contexto.add(contexto)
            send_message_success(self.request, "Contexto adicionado.")
            return HttpResponseRedirect(self.request.path_info)
        else:
            Palavra(
                palavra=palavra,
                lingua=Lingua.objects.filter(
                    id=lingua
                ).first(),
                classe=ClassePalavra.objects.filter(
                    id=classe_mor
                ).first(),
                significado=significado,
                nivel=NivelLingua.objects.filter(
                    id=nivel
                ).first(),
                escrita_fonetica=escrita_fonetica
            ).save()
            Contexto(
                contexto=contexto
            ).save()
            Palavra.objects.filter(
                palavra=palavra
            ).first().contexto.add(
                Contexto.objects.filter(
                    contexto=contexto
                ).first()
            )
            send_message_success(self.request, "Palavra adicionada")
            return HttpResponseRedirect(self.request.path_info)


class LinguaDicionarioView(DetailView):
    template_name = 'ensino/dicionario_lingua.html'
    model = Lingua

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recent_words'] = get_recent_word(self.get_object())
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
        context['recent_words'] = get_recent_word(self.get_object().lingua)

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
            'linguas': Lingua.objects.all(),
        }

        # atribuidas variaveis para utilizar no post
        self.criar_aula = self.context['criar_aula']

        self.renderizar = render(
            self.request, self.template_name, self.context
        )

    def get(self, *args, **kwargs):
        if not 'usuario_logado' in self.request.session:
            return redirect('usuario:login')

        return self.renderizar

    def post(self, *args, **kwargs):
        if not form_html_validated(self.request.POST):
            return self.renderizar
        class_image = self.request.FILES.get('class-image')
        class_video = self.request.FILES.get('class-video')
        ano = date.today().strftime("%Y")
        mes = date.today().strftime("%m")
        aula = Aula(
            aula=self.request.POST.get('class-name'),
            conteudo=self.request.POST.get('class-content'),
            nivel_id=self.request.POST.get('class-nivel'),
            lingua_id=self.request.POST.get('class-language'),
            img_aula=class_image,
            aula_gravada=class_video,
            autor_aula_id=self.request.session['usuario_logado']['usuario_id']
        )

        img_path = default_storage.save(
            rf"img_aula\{ano}\{mes}\{class_image}", ContentFile(
                class_image.read())
        )
        os.path.join(settings.MEDIA_ROOT, img_path)
        video_path = default_storage.save(
            rf'aula\{ano}\{mes}\{class_video}', ContentFile(
                class_video.read())
        )
        os.path.join(settings.MEDIA_ROOT, video_path)
        if self.request.session['usuario_logado']['is_licenced']:
            aula.is_licenced = self.request.POST.get('is_licenced') == 'on'

        aula.save()

        send_message_success(self.request, "Aula adicionada")
        return redirect(f'/ensino/meu_ensino/aula/{aula.id}/add_palavra')


# class AulaCadastroView(View):
#     """
#     View com dois forms: de criar aula e de criar atividade
#     """
#     template_name = 'ensino/cadastro/cadastro_aula.html'

#     def setup(self, *args, **kwargs):
#         super().setup(*args, **kwargs)

#         # contexto com os dois forms
#         self.context = {
#             'criar_aula': CriarAulaForms(
#                 data=self.request.POST or None,
#                 files=self.request.FILES or None,
#             ),
#         }

#         # atribuidas variaveis para utilizar no post
#         self.criar_aula = self.context['criar_aula']

#         self.renderizar = render(
#             self.request, self.template_name, self.context
#         )

#     def get(self, *args, **kwargs):
#         if not 'usuario_logado' in self.request.session:
#             return redirect('usuario:login')

#         return self.renderizar

#     def post(self, *args, **kwargs):
#         if not self.criar_aula.is_valid():
#             return self.renderizar

#         aula = self.criar_aula.save(commit=False)
#         aula.autor_aula = get_object_or_404(
#             Usuario, id=self.request.session['usuario_logado']['usuario_id']
#         )
#         if self.request.session['usuario_logado']['is_licenced']:
#             aula.is_licenced = self.request.POST.get('is_licenced') == 'on'

#         aula.save()
#         send_message_success(self.request, "Aula adicionada")
#         return redirect(f'/ensino/meu_ensino/aula/{aula.id}/add_palavra')


class AtualizarAulaView(DetailView):
    """
    View para atualizacao de aula
    """
    template_name = 'ensino/atualizar_aula.html'
    model = Aula

    def get(self, *args, **kwargs):
        if not 'usuario_logado' in self.request.session:
            return redirect('usuario:login')
        if not self.get_object().autor_aula.id == self.request.session['usuario_logado']['usuario_id']:
            return redirect('usuario:home')
        return super().get(*args, **kwargs)

    # def get_success_url(self):
    #     return reverse('usuario:home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['aula'] = self.get_object()
        context['palavras_aula'] = Palavra.objects.filter(
            id__in=AulaPalavra.objects.filter(
                aula=self.get_object()
            ).values('palavra_id')
        )
        context['tem_atividade'] = AtividadeAula.objects.filter(
            aula=self.get_object()
        ).first()
        context['questoes'] = Questao.objects.filter(
            id__in=AtividadeQuestao.objects.filter(
                atividade=context['tem_atividade']
            ).values('questao_id')
        )
        return context

    def post(self, *args, **kwargs):
        ano = date.today().strftime("%Y")
        mes = date.today().strftime("%m")
        class_img = self.request.FILES.get('class-image')
        class_video = self.request.FILES.get('class-video')
        img_path = None
        video_path = None
        if class_img:
            img_path = default_storage.save(
                rf"img_aula\{ano}\{mes}\{class_img}", ContentFile(
                    class_img.read())
            )
            os.path.join(settings.MEDIA_ROOT, img_path)
        if class_video:
            video_path = default_storage.save(
                rf'aula\{ano}\{mes}\{class_video}', ContentFile(
                    class_video.read())
            )
            os.path.join(settings.MEDIA_ROOT, video_path)
        Aula.objects.filter(
            id=self.get_object().id
        ).update(
            aula=self.request.POST.get('aula') or self.get_object().aula,
            conteudo=self.request.POST.get(
                'conteudo') or self.get_object().conteudo,
            aula_gravada=video_path or self.get_object().aula_gravada,
            img_aula=img_path or self.get_object().img_aula,
        )
        send_message_success(self.request, "Aula atualizada")
        return redirect('ensino:meu_ensino')

 # def form_valid(self, form):
#     return super().form_valid(form)
# class AtualizarAulaView(UpdateView):
#     """
#     View para atualizacao de aula
#     """
#     template_name = 'ensino/atualizar_aula.html'
#     model = Aula
#     form_class = AtualizarAulaForms

#     def get(self, *args, **kwargs):
#         if not 'usuario_logado' in self.request.session:
#             return redirect('usuario:login')
#         if not self.get_object().autor_aula.id == self.request.session['usuario_logado']['usuario_id']:
#             return redirect('usuario:home')
#         return super().get(*args, **kwargs)

#     def get_success_url(self):
#         return reverse('usuario:home')

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['aula'] = self.get_object()
#         context['palavras_aula'] = Palavra.objects.filter(
#             id__in=AulaPalavra.objects.filter(
#                 aula=self.get_object()
#             ).values('palavra_id')
#         )
#         context['tem_atividade'] = AtividadeAula.objects.filter(
#             aula=self.get_object()
#         ).first()
#         return context

#     def form_valid(self, form):
#         att_aula = form.save(commit=False)
#         att_aula.aula = form.cleaned_data.get('aula') or self.get_object().aula
#         att_aula.conteudo = form.cleaned_data.get(
#             'conteudo') or self.get_object().conteudo
#         form.save()
#         send_message_success(self.request, "Aula atualizada")
#         return super().form_valid(form)


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
            send_message_info(self.request, 'Você não pode estar aqui!!')
            return redirect('usuario:home')
        return super().get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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
        context['palavras_aula'] = get_palavracontexto(palavras_aulas)
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

        return super().get(self, *args, **kwargs)

    def get_queryset(self):
        queryset = Aula.objects.filter(
            autor_aula=self.request.session['usuario_logado']['usuario_id']
        )
        return queryset


class AddPalavra(DetailView):
    template_name = 'ensino/cadastro/cadastra_palavra_aula.html'
    model = Aula

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['palavras_ja_add'] = Palavra.objects.filter(
            id__in=AulaPalavra.objects.filter(
                aula=self.get_object()
            ).values('palavra_id')
        )
        context['palavras_disponiveis'] = Palavra.objects.filter(
            lingua=self.get_object().lingua,
            nivel=self.get_object().nivel,
        ).exclude(id__in=AulaPalavra.objects.filter(
            aula=self.get_object()
        ).values('palavra_id'))
        print(context['palavras_ja_add'])
        return context

    def post(self, *args, **kwargs):
        working = True
        word = 0

        while working:
            palavra = Palavra.objects.filter(
                id=self.request.POST.get(f'form-{word}-palavra')
            ).first()
            if not palavra:
                working = False
            AulaPalavra(
                palavra=palavra,
                aula=self.get_object(),
            ).save()
            word += 1

        send_message_success(self.request, "Palavras adicionadas à aula")
        if not self.get_object().atividade.first():
            return redirect(f'/ensino/meu_ensino/aula/{self.get_object().id}/adiciona_atividade')

        return redirect((f'/ensino/aula/{self.get_object().id}'))


class CriaQuestao(TemplateView):
    template_name = 'ensino/cadastro/cadastra_questao.html'

    def get(self, *args, **kwargs):
        formset = AlternativasQuestaoFormset()
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

            send_message_success(self.request, 'Questão cadastrada')
            return redirect(reverse_lazy('usuario:home'))

        return self.render_to_response(
            {
                'add_questao': form,
                'add_alternativa': formset,
            },
        )


class UpdateQuestao(DetailView):
    template_name = 'ensino/update_questao.html'
    model = Questao

    def setup(self, *args, **kwargs):
        super().setup(*args, **kwargs)
        self.context = {
            'questao': self.get_object(),
            'alternativas': Alternativa.objects.filter(
                questao=self.get_object(),
            ),
        }
        self.context.update(
            {
                'validated_form': False if self.context['alternativas'].count() >= 8 else True
            }
        )

        self.renderizar = render(
            self.request, self.template_name, self.context)

    def get(self, *args, **kwargs):
        print(self.context['alternativas'])
        print(self.context['alternativas'].count())
        print(self.context['validated_form'])
        return self.renderizar

    def post(self, *args, **kwargs):
        alternativas_salvas = Alternativa.objects.filter(
            questao=self.get_object()
        )

        frase = self.request.POST.get('id_frase')
        if not self.get_object().frase == frase:
            Questao.objects.filter(
                id=self.get_object().id
            ).update(
                frase=frase
            )

        for alternativa in alternativas_salvas:
            up_alternativa = self.request.POST.get(
                f'id_{alternativa.id}_alternativa')
            if not alternativa.alternativa == up_alternativa:
                Alternativa.objects.filter(
                    questao=self.get_object(),
                    id=alternativa.id,
                ).update(
                    alternativa=up_alternativa
                )

        # aqui sao as novas questoes
        id_nov = 0
        alt_nova = self.request.POST.get(
            f'id_alternativa_set-{id_nov}-alternativa')

        while alt_nova:
            if self.request.POST.get(f'id_alternativa_set-{id_nov}-is_correct') == 'on':
                Alternativa(
                    questao=self.get_object(),
                    alternativa=alt_nova,
                    is_correct=True
                ).save()
            else:
                Alternativa(
                    questao=self.get_object(),
                    alternativa=alt_nova,
                    is_correct=False
                ).save()
            id_nov += 1
            alt_nova = self.request.POST.get(
                f'id_alternativa_set-{id_nov}-alternativa')
        send_message_success(self.request, "Questão atualizada")
        # preciso mudar aqui em baixo
        return redirect(reverse_lazy('ensino:meu_ensino'))

# TENHO QUE MELHORAR ISSO


class ResolucaoQuestao(DetailView):
    template_name = 'ensino/resolucao.html'
    model = Questao

    def get_context_data(self, **kwargs):
        context = super(ResolucaoQuestao, self).get_context_data(**kwargs)
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


class AdicionaAtividadeAula(DetailView):
    template_name = 'ensino/cadastro/cadastra_atividade.html'
    model = Aula

    def get_context_data(self, **kwargs):
        context = super(AdicionaAtividadeAula,
                        self).get_context_data(**kwargs)
        context['aula'] = self.get_object()
        context['questoes_ja_add'] = Questao.objects.filter(
            id__in=AtividadeQuestao.objects.filter(
                atividade__aula=self.get_object()
            ).values('questao_id')
        )
        context['questoes_disponiveis'] = Questao.objects.filter(
            nivel=self.get_object().nivel,
            lingua=self.get_object().lingua
        ).exclude(id__in=AtividadeQuestao.objects.filter(
            atividade__aula=self.get_object()
        ).values('questao_id')
        )

        print(context['questoes_ja_add'])
        return context

    def post(self, *args, **kwargs):
        working = True
        question = 0

        while working:
            questao = Questao.objects.filter(
                id=self.request.POST.get(f'form-{question}-questao')
            ).first()
            print(questao)
            if not questao:
                working = False
            else:
                AtividadeQuestao(
                    atividade=AtividadeAula.objects.filter(
                        aula=self.get_object()
                    ).first(),
                    questao=questao
                ).save()
                question += 1
        # get_questoes = self.request.POST.getlist('questoes')
        # atividade = AtividadeAula(
        #     aula=self.get_object()
        # )
        # atividade.save()
        # for id_questao in get_questoes:
        #     questao = get_object_or_404(
        #         Questao, id=id_questao
        #     )
        #     AtividadeQuestao(
        #         atividade=atividade,
        #         questao=questao,
        #     ).save()
        send_message_success(self.request, "Atividade adicionada à aula")
        return redirect(f'/ensino/aula/{self.get_object().id}')


class ResolucaoAtividade(DetailView):
    template_name = 'ensino/atividade_aula.html'
    model = AtividadeAula

    def get_context_data(self, **kwargs):
        context = super(ResolucaoAtividade,
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
        send_message_grade(self.request, nota)

        return redirect(f'/ensino/aula/{self.get_object().aula.id}')


class UpdateAtividadeConcluida(DetailView):
    template_name = 'ensino/atividade_aula.html'
    model = EnvioAtividadeAula

    def get_context_data(self, **kwargs):
        context = super(UpdateAtividadeConcluida,
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
            pass
        send_message_grade(self.request, nota)

        return redirect(f'/ensino/aula/{self.get_object().atividade.aula.id}')


class BuscaView(DetailView):
    template_name = 'ensino/busca.html'
    model = Lingua

    def setup(self, *args, **kwargs):
        super().setup(*args, **kwargs)
        self.palavra_e = self.request.GET.get('palavra')
        self.palavra = Palavra.objects.filter(
            palavra=self.palavra_e
        ).first()

        self.context = {
            'palavra_e': self.palavra_e,
            'palavras': Palavra.objects.filter(
                Q(palavra=self.palavra_e) |
                Q(palavra__icontains=f'{self.palavra_e[:3]}'),
                lingua=self.get_object()
            ).distinct()[:6],
            'recent_words': get_recent_word(self.get_object()),
            'lingua': self.get_object(),
        }
        self.renderizar = render(
            self.request, self.template_name, self.context
        )

    def get(self, *args, **kwargs):
        if self.palavra:
            return redirect(
                f'/ensino/lingua/palavra/{self.palavra.id}/')
        return self.renderizar


# AJAX VIEWS
def ajax_alter_nivel(request):
    lingua_id = request.GET.get('lingua')
    if not lingua_id:
        return render(request, 'ensino/ajax/nivel_list.html', {'niveis': ['Please select a language']})
    lingua = Lingua.objects.filter(
        id=lingua_id
    ).first()
    niveis = NivelLingua.objects.filter(
        valor_nivel__lte=NivelLingua.objects.filter(
            id__in=UsuarioLingua.objects.filter(
                usuario_id=request.session['usuario_logado']['usuario_id'],
                lingua=lingua,
            ).values('nivel__id')
        ).first().valor_nivel
    ).exclude(valor_nivel=0)
    if not niveis:
        niveis = ["You cannot post a class for this language"]

    return render(request, 'ensino/ajax/nivel_list.html', {'niveis': niveis})
