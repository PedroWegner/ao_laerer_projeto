from utils.send_messages import *
from typing import Dict, List
from ensino.models import EnvioAtividadeAula, Palavra, Contexto, UsuarioLingua, Alternativa, AtividadeAula, \
    EnvioAtividadeAula, Questao, AtividadeQuestao
import random


def send_message_grade(request, grade):
    if grade < 70.0:
        send_message_error(request, f"Sua nota foi: {grade}")
    else:
        send_message_success(request, f"Sua nota foi: {grade}")


def get_recent_word(lingua) -> Dict:
    return Palavra.objects.filter(
        lingua=lingua
    ).order_by('-data_cadastro')[:5]


def get_similar_level_word(lingua, nivel) -> Dict:
    return Palavra.objects.filter(
        lingua=lingua,
        nivel=nivel
    ).order_by('?')[:5]


def checa_nivel_aula_user(nivel, request, lingua):
    nivel_usuario = UsuarioLingua.objects.filter(
        lingua=lingua,
        usuario__id=request['usuario_logado']['usuario_id']
    ).first()
    if (nivel_usuario.nivel.valor_nivel + 1) < nivel.valor_nivel:
        return False
    return True


def seleciona_alternativas(questao) -> List:
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


def checa_nivel_lingua(atividade, request) -> None:
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


def cria_atividade(atividade, nota, request) -> None:
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


def checa_questoes(atividade, request) -> float:
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


def get_palavracontexto(palavras: List) -> Dict:
    palavra_dict = {}
    for palavra in palavras:
        palavra_dict.update(
            {
                palavra: Contexto.objects.filter(
                    palavracontexto__palavra=palavra
                ).order_by('?').first()
            }
        )
    return palavra_dict
