import sqlite3
from youtube_entity import YtChannelInfo, YtVideoInfo

def execute_sql_file(conn, sql_file_path):
    try:
        with open(sql_file_path, 'r') as sql_file:
            sql_script = sql_file.read()

        cur = conn.cursor()
        cur.executescript(sql_script)
        conn.commit()
        print("Script SQL executado com sucesso!")
    
    except sqlite3.Error as e:
        print(f"Erro ao executar o script SQL: {e}")

def insert(conn, channel):
    if not channel_exists(conn, channel.channelId):
        insert_channel(conn, channel)

    for video in channel.last_videos_list:
        if not video_exists(conn, video.videoId):
            insert_video(conn, video)

    for video in channel.trending_videos_list:
        if not video_exists(conn, video.videoId):
            insert_video(conn, video)

def get_all(conn):
    channels = get_channels(conn)
    for channel in channels:
        channel.last_videos_list = get_channel_latest_videos(conn, channel.channelId)
        channel.trending_videos_list = get_channel_trending_videos(conn, channel.channelId)
    
    return channels

def get_channels(conn):
    sql = '''
        SELECT channelId, handle, title, description FROM YtChannelInfo
    '''
    try:
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        
        channels = []
        for row in rows:
            channel = YtChannelInfo(
                channelId=row[0],
                handle=row[1],
                title=row[2],
                description=row[3],
                last_videos_list=[],
                trending_videos_list=[]
            )

            channels.append(channel)
        
        return channels

    except sqlite3.Error as e:
        print(f"Erro ao obter canais: {e}")
        return []
    
def channel_exists(conn, channelId):
    sql = '''
        SELECT 1 FROM YtChannelInfo WHERE channelId = ?
    '''
    try:
        cur = conn.cursor()
        cur.execute(sql, (channelId,))
        
        result = cur.fetchone()
        
        return result is not None
    
    except sqlite3.Error as e:
        print(f"Erro ao verificar existência do canal: {e}")
        return False

def insert_channel(conn, channel):
    sql = '''
        INSERT INTO YtChannelInfo (channelId, handle, title, description)
        VALUES (?, ?, ?, ?)
    '''
    try:
        cur = conn.cursor()
        cur.execute(sql, (channel.channelId, channel.handle, channel.title, channel.description))
        
        conn.commit()
        print("Canal inserido com sucesso!")
    
    except sqlite3.Error as e:
        print(f"Erro ao inserir canal: {e}")

def get_channel_latest_videos(conn, channelId):
    sql = '''
        SELECT videoId, title, viewCount, publishedAt
        FROM YtVideoInfo
        WHERE channelId = ?
        ORDER BY publishedAt DESC
        LIMIT 10
    '''
    try:
        cur = conn.cursor()
        cur.execute(sql, (channelId,))
        rows = cur.fetchall()
        
        videos = []
        for row in rows:
            video = YtVideoInfo(
                channelId=channelId,
                title=row[1],
                videoId=row[0],
                viewCount=row[2],
                publishedAt=row[3]
            )
            videos.append(video)
        
        return videos

    except sqlite3.Error as e:
        print(f"Erro ao obter vídeos do canal: {e}")
        return []
    
def get_channel_trending_videos(conn, channelId):
    sql = '''
        SELECT videoId, title, viewCount, publishedAt
        FROM YtVideoInfo
        WHERE channelId = ?
        ORDER BY viewCount DESC
        LIMIT 10
    '''
    try:
        cur = conn.cursor()
        cur.execute(sql, (channelId,))
        rows = cur.fetchall()
        
        videos = []
        for row in rows:
            video = YtVideoInfo(
                channelId=channelId,
                title=row[1],
                videoId=row[0],
                viewCount=row[2],
                publishedAt=row[3]
            )
            videos.append(video)
        
        return videos

    except sqlite3.Error as e:
        print(f"Erro ao obter vídeos em tendência do canal: {e}")
        return []

def video_exists(conn, videoId):
    sql = '''
        SELECT 1 FROM YtVideoInfo WHERE videoId = ?
    '''
    try:
        cur = conn.cursor()
        cur.execute(sql, (videoId,))
        result = cur.fetchone()
        return result is not None
    except sqlite3.Error as e:
        print(f"Erro ao verificar existência do vídeo: {e}")
        return False


def insert_video(conn, video):
    sql = '''
        INSERT INTO YtVideoInfo (videoId, channelId, title, viewCount, publishedAt)
        VALUES (?, ?, ?, ?, ?)
    '''
    try:
        cur = conn.cursor()
        cur.execute(sql, (video.videoId, video.channelId, video.title, video.viewCount, video.publishedAt))
        conn.commit()
        print("Vídeo inserido com sucesso!")
    except sqlite3.Error as e:
        print(f"Erro ao inserir vídeo: {e}")

def delete_sugestions(conn, channelId):
    sql = '''
        DELETE FROM YtVideoSugestion
        WHERE channelId = ?
    '''
    try:
        cur = conn.cursor()
        cur.execute(sql, (channelId,))
        conn.commit()
        print(f"Sugestões do canal {channelId} deletadas com sucesso!")
    
    except sqlite3.Error as e:
        print(f"Erro ao deletar sugestões: {e}")

def insert_sugestions(conn, sugestions):
    for sugestion in sugestions:
        insert_sugestion(conn, sugestion)

def insert_sugestion(conn, sugestion):
    sql = '''
        INSERT INTO YtVideoSugestion (channelId, videoId, sugestion)
        VALUES (?, ?, ?)
    '''
    try:
        cur = conn.cursor()
        cur.execute(sql, (sugestion.channelId, sugestion.videoId, sugestion.sugestion))
        conn.commit()
        print(f"Sugestão para o vídeo {sugestion.videoId} inserida com sucesso!")
    except sqlite3.Error as e:
        print(f"Erro ao inserir sugestão: {e}")

def delete_rewrites(conn, channelId):
    sql = '''
        DELETE FROM YtVideoRewrite
        WHERE channelId = ?
    '''
    try:
        cur = conn.cursor()
        cur.execute(sql, (channelId,))
        conn.commit()
        print(f"Reescritas do canal {channelId} deletadas com sucesso!")
    
    except sqlite3.Error as e:
        print(f"Erro ao deletar reescritas: {e}")

def insert_rewrites(conn, rewrite):
    for rewrites in rewrite:
        insert_rewrite(conn, rewrites)

def insert_rewrite(conn, rewrite):
    sql = '''
        INSERT INTO YtVideoRewrite (channelId, videoId, rewrite)
        VALUES (?, ?, ?)
    '''
    try:
        cur = conn.cursor()
        cur.execute(sql, (rewrite.channelId, rewrite.videoId, rewrite.rewrite))
        conn.commit()
        print(f"Reescrita para o vídeo {rewrite.videoId} inserida com sucesso!")
    except sqlite3.Error as e:
        print(f"Erro ao inserir reescrita: {e}")


if __name__ == "__main__":
    conn = sqlite3.connect('youtube_db.sqlite3')

    execute_sql_file(conn, 'db-data-test.sql')