from django.contrib import admin

from forum.models import Comentario, Conversa, Mensagem, Noticia, Postagem

# Register your models here.
admin.site.register(Mensagem)
admin.site.register(Noticia)
admin.site.register(Comentario)
admin.site.register(Postagem)
