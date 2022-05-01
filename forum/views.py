from select import select
from django.http import HttpResponseRedirect
from django.views import View
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView
from django.views.generic import FormView
from django.views.generic.detail import DetailView
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .forms import *
from usuario.models import Usuario
from ensino.models import Lingua
from .models import *


# Create your views here.


class ForumView(ListView):
    template_name = 'forum/forum.html'
    model = Lingua
    context_object_name = 'linguas'


class ForumLinguaView(DetailView):
    template_name = 'forum/forum_lingua.html'
    model = Lingua
    context_object_name = 'lingua'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['postagens'] = Postagem.objects.filter(
            lingua=self.get_object()
        ).all
        context['postagens_recentes'] = Postagem.objects.filter(
            lingua=self.get_object()
        )[:5]

        return context


class PostagemRegistraView(FormView):
    template_name = 'forum/cadastro_postagem.html'
    form_class = PostagemForms

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['postagens_recentes'] = Postagem.objects.filter(
            lingua=get_object_or_404(
                Lingua, id=self.request.build_absolute_uri()[-1]
            )
        )[:5]
        context['lingua'] = get_object_or_404(
            Lingua, id=self.request.build_absolute_uri()[-1]
        )

        return context

    def get_success_url(self):
        return reverse('forum:forum')

    def get(self,  *args, **kwargs):

        return super().get(*args, **kwargs)

    def form_valid(self, form):
        if not form.is_valid():
            return render(self.request, self.template_name)

        postagem = form.save(commit=False)
        postagem.autor = get_object_or_404(
            Usuario, id=self.request.session['usuario_logado']['usuario_id']
        )
        postagem.lingua = get_object_or_404(
            Lingua, id=self.request.build_absolute_uri()[-1]
        )
        postagem.save()
        return super().form_valid(form)


class PostagemView(DetailView):
    template_name = 'forum/postagem.html'
    model = Postagem
    context_object_name = 'postagem'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comentarios'] = Comentario.objects.filter(
            postagem=self.get_object()
        ).all
        context['postagens_recentes'] = Postagem.objects.filter(
            lingua=self.get_object().lingua
        )[:5]
        context['form'] = ComentarioForms(
            data=self.request.POST or None,
            files=self.request.FILES or None
        )

        return context

    def post(self, *args, **kwargs):
        Comentario(
            autor=get_object_or_404(
                Usuario, id=self.request.session['usuario_logado']['usuario_id'],
            ),
            postagem=self.get_object(),
            conteudo_comentario=self.request.POST.get('conteudo_comentario'),
            imagem_comentario=self.request.FILES.get(
                'imagem_comentario') or None,
        ).save()
        return HttpResponseRedirect(self.request.path_info)


class NoticiaCadastroView(FormView):
    template_name = 'forum/cadastro_noticia.html'
    model = Noticia
    form_class = PublicarNoticiaForms

    def get(self, *args, **kwargs):
        if not 'usuario_logado' in self.request.session:
            return redirect('usuario:login')

        if not self.request.session['usuario_logado']['is_admin']:
            return redirect('usuario:home')

        return super().get(*args, **kwargs)

    def get_success_url(self):
        return reverse('usuario:home')

    def form_valid(self, form):
        if not form.is_valid():
            return render(self.request, self.template_name)

        noticia = form.save(commit=False)
        noticia.administrador = get_object_or_404(
            Usuario, id=self.request.session['usuario_logado']['usuario_id'])
        noticia.save()
        return super().form_valid(form)


class NoticiaView(DetailView):
    template_name = 'forum/noticia.html'
    model = Noticia
    context_object_name = 'noticia'

# class PerfilUsuarioView(DetailView):
#     template_name = 'forum/perfil_usuario.html'
#     model = Usuario
#     object_context_name = 'usuario'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         print(self.get_object())
#         if self.get_object().tipo_usuario.id == 1:
#             pass
#             # context['cursos_vinculados'] = ModuloMatriculaAluno.objects.filter(
#             #     aluno__usuario=self.get_object(),
#             #     aprovado=True
#             # )
#         else:
#             pass
#             # context['cursos_vinculados'] = ModuloVinculoProfessor.objects.filter(
#             #     professor__usuario=self.get_object(),
#             # )
#         context['postagens'] = Postagem.objects.filter(
#             autor=self.get_object()
#         )[:5]
#         context['comentarios'] = Comentario.objects.filter(
#             autor=self.get_object()
#         )[:5]

#         if self.get_object().id == self.request.session['usuario_logado']['usuario_id']:
#             pass
#         else:
#             conversa = ConversaUsuario.objects.filter(
#                 usuario_id=self.get_object().id,
#                 conversa=get_object_or_404(
#                     Conversa,
#                     conversausuario__usuario_id=self.request.session['usuario_logado']['usuario_id']
#                 )
#             ).values('conversa_id').first()
#             if not conversa:
#                 context['conversa'] = None
#             else:
#                 context['conversa'] = get_object_or_404(
#                     Conversa, id=conversa['conversa_id']
#                 )
#         return context


# class ConversaView(DetailView):
#     template_name = 'forum/conversa.html'
#     model = Conversa
#     object_context_name = 'conversa'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['form'] = MensagemForms(
#             data=self.request.POST or None,
#             files=self.request.FILES or None
#         )
#         context['mensagens'] = Mensagem.objects.filter(
#             conversa=self.get_object()
#         )

#         return context

#     def get(self, *args, **kwargs):
#         # aqui precisa colocar a lógica para evtar que um outro usuario nao da conversa tenha acesso

#         return super().get(*args, **kwargs)

#     def post(self, *args, **kwargs):
#         Mensagem(
#             conversa=self.get_object(),
#             autor=get_object_or_404(
#                 Usuario, id=self.request.session['usuario_logado']['usuario_id'],
#             ),
#             texto=self.request.POST.get('texto'),
#             imagem_mensagem=self.request.FILES.get(
#                 'imagem_comentario') or None,
#         ).save()
#         return HttpResponseRedirect(self.request.path_info)
