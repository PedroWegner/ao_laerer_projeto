from django.core.files.storage import default_storage
from django.conf import settings
from django.core.files.base import ContentFile
from datetime import date
import os
from typing import Dict
from forum.models import Conversa, ConversaUsuario
from usuario.models import Usuario, Pessoa
import bcrypt
from django.shortcuts import get_object_or_404


def get_last_chat(request):
    conversa = Conversa.objects.filter(
        id__in=ConversaUsuario.objects.filter(
            usuario_id=request.session['usuario_logado']['usuario_id']
        ).values('conversa_id')
    ).order_by('-ultima_atualizcao').first()
    return conversa


def get_conversations_list(request) -> Dict:
    lista_conversas = {}
    conversas = Conversa.objects.filter(
        id__in=ConversaUsuario.objects.filter(
            usuario_id=request.session['usuario_logado']['usuario_id']
        ).values('conversa_id')
    )
    usuarios = Usuario.objects.filter(
        id__in=ConversaUsuario.objects.filter(
            conversa_id__in=conversas
        ).values('usuario_id')
    ).exclude(id=request.session['usuario_logado']['usuario_id'])

    for usuario in usuarios:
        conversa = Conversa.objects.filter(
            id__in=ConversaUsuario.objects.filter(
                usuario_id=usuario.id
            ).values('conversa_id')
        ).filter(
            id__in=ConversaUsuario.objects.filter(
                usuario_id=request.session['usuario_logado']['usuario_id']
            ).values('conversa_id')
        ).first()
        lista_conversas.update(
            {
                usuario: conversa
            }
        )
    return lista_conversas


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
