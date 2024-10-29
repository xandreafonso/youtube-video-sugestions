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

A segunda coisa é que quero que reescreva o títulos dos 5 vídeos mais vistos do canal.
Não mude a ideia do título apenas reescreva.
Em cada reescrita que fizer, informe também o vídeo de base utilizado.

COMO VOCÊ VAI RETORNAR AS INFORMAÇÕES:
                 
Eu quero um json como resposta. Apenas o JSON e nada mais.
                 
Exemplo:

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
        { "rewrite": "A reescrita aqui", "videoId": "id do vídeo de inspiração" }
    ]
}
"""
)

def create_videos_sugestions_from_channel(channel_json):
    response = completion(
        model="gpt-4o-mini",
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
                            sugestion=item["sugestion"]
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

    channels = get_all(conn)

    for channel in channels:
        channel_json = json.dumps(obj_to_json(channel), ensure_ascii=False)
        print(channel_json)
        
        response = create_videos_sugestions_from_channel(channel_json)
        sugestions, rewrites = process_json_to_objects(channel.channelId, response)

        delete_sugestions(conn, channel.channelId)        
        insert_sugestions(conn, sugestions)

        delete_rewrites(conn, channel.channelId)
        insert_rewrites(conn, rewrites)
