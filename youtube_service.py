import os
import googleapiclient.discovery
from dotenv import load_dotenv
import isodate

load_dotenv()

API_KEY = os.environ.get("YOUTUBE_API_KEY")
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"

def get_youtube_service():
    return googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, developerKey=API_KEY)

def get_channel_id_by_handle(handle):
    youtube = get_youtube_service()

    request = youtube.search().list(
        part="snippet",
        q=handle,
        type="channel",
        maxResults=1
    )
    response = request.execute()

    if response['items']:
        return response['items'][0]['snippet']['channelId']
    else:
        return None

def get_last_videos(channel_id):
    youtube = get_youtube_service()

    request = youtube.search().list(
        part="id",
        channelId=channel_id,
        maxResults=25,
        order="date"
    )
    response = request.execute()

    video_ids = [item['id']['videoId'] for item in response['items'] if item['id']['kind'] == 'youtube#video']

    if not video_ids:
        return []

    # Inclui 'contentDetails' para pegar a duração dos vídeos
    request = youtube.videos().list(
        part="snippet,statistics,contentDetails",
        id=",".join(video_ids)
    )
    response = request.execute()

    videos = []
    for video in response['items']:
        duration = video['contentDetails']['duration']

        # Exclui vídeos com menos de 60 segundos (Shorts)
        if is_short_video(duration):
            continue

        video_info = {
            'title': video['snippet']['title'],
            'videoId': video['id'],
            'viewCount': video['statistics']['viewCount'],
            'publishedAt': video['snippet']['publishedAt']
        }
        videos.append(video_info)

    # Ordenar explicitamente por data, do mais recente para o mais antigo
    videos = sorted(videos, key=lambda x: x['publishedAt'], reverse=True)

    return videos

def get_trending_videos(channel_id):
    youtube = get_youtube_service()

    request = youtube.search().list(
        part="id",
        channelId=channel_id,
        maxResults=25,
        order="viewCount"
    )
    response = request.execute()

    video_ids = [item['id']['videoId'] for item in response['items'] if item['id']['kind'] == 'youtube#video']

    if not video_ids:
        return []

    # Inclui 'contentDetails' para pegar a duração dos vídeos
    request = youtube.videos().list(
        part="snippet,statistics,contentDetails",
        id=",".join(video_ids)
    )
    response = request.execute()

    trending_videos = []
    for video in response['items']:
        duration = video['contentDetails']['duration']

        # Exclui vídeos com menos de 60 segundos (Shorts)
        if is_short_video(duration):
            continue

        video_info = {
            'title': video['snippet']['title'],
            'videoId': video['id'],
            'viewCount': video['statistics']['viewCount'],
            'publishedAt': video['snippet']['publishedAt']
        }
        trending_videos.append(video_info)

    return trending_videos

def is_short_video(duration):
    duration_seconds = isodate.parse_duration(duration).total_seconds()
    
    return duration_seconds < 180

def get_channel_info(channel_id):
    youtube = get_youtube_service()

    request = youtube.channels().list(
        part="snippet",
        id=channel_id
    )
    response = request.execute()

    if response['items']:
        return {
            'title': response['items'][0]['snippet']['title'],
            'description': response['items'][0]['snippet']['description']
        }
    else:
        return {
            'title': None,
            'description': None
        }


