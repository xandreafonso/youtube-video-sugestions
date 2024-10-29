import os
import sqlite3
from litellm import completion
from dotenv import load_dotenv

from youtube_service import get_channel_id_by_handle, get_last_videos, get_trending_videos, get_channel_info
from youtube_entity import YtChannelInfo, YtVideoInfo
from youtube_db import insert

load_dotenv()

def chl_info(handle):
    channelId = get_channel_id_by_handle(handle)

    if not channelId:
        raise Exception(f"Canal {handle} não encontrado!")

    last_videos = get_last_videos(channelId)
    last_videos_list = []

    for video in last_videos:
        last_videos_list.append(YtVideoInfo(channelId, video['title'], video['videoId'], video['viewCount'], video['publishedAt']))

    trending_videos = get_trending_videos(channelId)
    trending_videos_list = []

    for video in trending_videos:
        trending_videos_list.append(YtVideoInfo(channelId, video['title'], video['videoId'], video['viewCount'], video['publishedAt']))

    c_info = get_channel_info(channelId)

    return YtChannelInfo(channelId, handle, c_info['title'], c_info['description'], last_videos_list, trending_videos_list)

handles = [
    "@AlanaAnijar",
    "@rafaelgratta",
    "@NeuroVox",
    "@ClaramenteNT",
    "@drali",
    "@Katimorton",
    "@TherapyinaNutshell",
    "@MarkTyrrellUnk",
    "@theanxietyproject",
    "@ocdandanxiety",
    "@PracticalPsychologyTips",
    "@PsychExplained",
    "@DrJulie",
    "@DraAnnaLuyzaAguiar",
    "@podpeopleanabeatriz",
    "@AugustoCury",
    "@NeurologiaePsiquiatria",
    "@danielamargotti",
    "@psicojuliapaschoalino",
    "@psicologasandrabueno"
]

if __name__ == "__main__":
    conn = sqlite3.connect('youtube_db.sqlite3')

    for handle in handles:
        try:
            print(f"Obtendo informações do canal {handle}")
            c_info = chl_info(handle)

            insert(conn, c_info)
            print(f"Canal {handle} inserido com sucesso!")
        except Exception as e:
            print(f"Erro ao obter informações do canal {handle}: {e}")
            continue
    



