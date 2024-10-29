import os
import sqlite3, json
from litellm import completion
from dotenv import load_dotenv
from youtube_db import get_all, delete_sugestions, delete_rewrites, insert_sugestions, insert_rewrites
from youtube_entity import YtVideoSugestion, YtVideoRewrite

load_dotenv()

system_prompt = ("""
# SEU OBJETIVO

Seu objetivo é me ajudar a criar novas ideias de conteúdo a partir de informações de um canal de YouTube.
                 
# SEU BACKSTORY
                 
Você é um especialista em marketing de conteúdo. Você é muito bom em ajudar canais do YouTube a crescerem mais rápido.
Você estuda outros canais do YouTube para descobrir, a partir desse estudo, as melhores ideias de conteúdo.
                 
# SUA ATIVIDADE

Você vai receber essas informações de um canal de YouTube:

- Nome do canal
- Descrição do canal
- Últimos vídeos publicados
- Vídeos em alta (mais vistos)

A partir dessas informações, você vai fazer 2 coisas.

A primeira coisa são as sugestões de novos vídeos que você vai criar.
Você vai retornar ao todo 10 sugestões de vídeo.
5 dessas sugestões serão com base nos últimos vídeos públicados e as outras 5 serão com base nos vídeos mais vistos do canal.
Em cada uma das sugestões, mostre qual foi a inspiração.
Procure dar sugestões se baseando nos vídeos com o maior número de visualizações.

A segunda coisa é que quero que reescreva o título dos 5 vídeos mais vistos do canal.
Não mude a ideia do título, apenas reescreva para que seja outro título, porém, falando a mesma coisa.
Em cada reescrita que fizer, informe também o vídeo de base utilizado.
                 
Cada título que você gerar (seja uma sugestão ou reescrita) deve considerar o canal do YouTube para o qual você vai gerar as sugestões.
                 
TEMA DO CANAL DO YOUTUBE QUE RECEBERÁ AS SUGESTÕES:
                 
A dona do canal é uma psicóloca especialista em TCC e neurociência.
O objetivo primário (principal) dela no YouTube é criar excelentes conteúdos para ajudar as pessoas aprenderem e se cuidarem.
O objetivo secundário é oferecer terapia para aquelas pessoas que precisam.
                 
Ela tem tratamento/sessões de Terapia Cognitivo-Comportamental. Terapia focada em ansiedade, depressão, passividade, e insegurança, que são desdobramentos da ansiedade.
As pacientes dela têm de 25 a 45 anos. São mulheres ativas profissionalmente, com problemas nos relacionamentos e com ansiedade. Elas tendem a ser passivas nas relações, inseguras e, algumas, emocionalmente dependentes. Esses problemas muitas vezes são fruto de uma falta de clareza sobre si mesmas, o que favorece a instalação da ansiedade. Ao ensiná-las sobre ansiedade, ajudo-as a se reconhecerem e se verem nessas situações.

Ela acredita que "tudo que você não conhece não existe para você"! O autoconhecimento é a chave para a mudança. Ela ensina as pacientes a aprenderem não só sobre seu próprio funcionamento, mas também novas habilidades para lidar com a vida e seus desafios.

Diferenciais da terapia dela:
                 
- Especialista em Terapia Cognitivo-Comportamental (TCC)  
- Atendimento online em 17 países  
- Mais de 10 mil horas de atendimento clínico  
- Formação em transtornos de humor e ansiedade pelo IPq-USP
                 
Mas lembrando! O objetivo primário é ajudar as pessoas a aprenderem e se cuidarem.

COMO VOCÊ VAI RETORNAR AS INFORMAÇÕES:

Me responda sempre em português (mesmo que as informações do canal sejam em inglês).
Eu quero um json como resposta. Apenas o JSON e nada mais. Não use coisas como "```json" para formatar o json. Eu quero apenas o json.
                 
Exemplo de JSON:

{
    "sugestions": {
        "latest": [
            { "sugestion": "A sugestão aqui", "videoId": "id do vídeo de inspiração" }
        ],         
        "trending": [
            { "sugestion": "A sugestão aqui", "videoId": "id do vídeo de inspiração" }
        ]         
    },
    "rewrites": [
        { "rewrite": "A reescrita aqui", "videoId": "id do vídeo de base" }
    ]
}
"""
)

def create_videos_sugestions_from_channel(channel_json):
    response = completion(
        model="gpt-4o-mini",
        # model="gpt-4o",
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": channel_json}],
    )

    return response['choices'][0]['message']['content']

def process_json_to_objects(channelId, json_string):
    try:
        data = json.loads(json_string)

        sugestions = []
        rewrites = []

        if "sugestions" in data:
            for suggestion_type in ["latest", "trending"]:
                if suggestion_type in data["sugestions"]:
                    for item in data["sugestions"][suggestion_type]:
                        suggestion = YtVideoSugestion(
                            channelId=channelId,
                            videoId=item["videoId"],
                            sugestion=item["sugestion"],
                            fromType=suggestion_type
                        )
                        sugestions.append(suggestion)

        if "rewrites" in data:
            for item in data["rewrites"]:
                rewrite = YtVideoRewrite(
                    channelId=channelId,
                    videoId=item["videoId"],
                    rewrite=item["rewrite"]
                )
                rewrites.append(rewrite)

        return sugestions, rewrites

    except json.JSONDecodeError as e:
        print(f"Erro ao fazer o parser do JSON: {e}")
        return [], []
    
def obj_to_json(obj):
    if isinstance(obj, list):
        return [obj_to_json(item) for item in obj]
    elif hasattr(obj, "__dict__"):
        return {key: obj_to_json(value) for key, value in obj.__dict__.items()}
    else:
        return obj

if __name__ == "__main__":
    conn = sqlite3.connect('youtube_db.sqlite3')

    channels = get_all(conn) # [0:1]

    for channel in channels:
        print(f"Criando sugestões para canal {channel.handle}...")

        channel_json = json.dumps(obj_to_json(channel), ensure_ascii=False)
        
        response = create_videos_sugestions_from_channel(channel_json)
        print("Resposta da OpenAI obtida com sucesso.")
        
        sugestions, rewrites = process_json_to_objects(channel.channelId, response)

        delete_sugestions(conn, channel.channelId)        
        insert_sugestions(conn, sugestions)

        delete_rewrites(conn, channel.channelId)
        insert_rewrites(conn, rewrites)

        print("Sugestões cadastradas no banco.")
        print("==")
