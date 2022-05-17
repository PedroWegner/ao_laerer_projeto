from django.contrib import admin

from forum.models import Comentario, Conversa, Mensagem, Noticia

# Register your models here.
admin.site.register(Mensagem)
admin.site.register(Noticia)
admin.site.register(Comentario)
