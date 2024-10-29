class YtVideoInfo:
    def __init__(self, channelId, title, videoId, viewCount, publishedAt):
        self.channelId = channelId
        self.title = title
        self.videoId = videoId
        self.viewCount = viewCount
        self.publishedAt = publishedAt

    def __repr__(self):
        return (f"YtVideoInfo(title='{self.title}', videoId='{self.videoId}', "
                f"viewCount={self.viewCount}, publishedAt='{self.publishedAt}')")

class YtChannelInfo:
    def __init__(self, channelId, handle, title, description, last_videos_list, trending_videos_list, sugestions_list=[], rewrites_list=[]):
        self.channelId = channelId
        self.handle = handle
        self.title = title
        self.description = description
        self.last_videos_list = last_videos_list
        self.trending_videos_list = trending_videos_list
        self.sugestions_list = sugestions_list
        self.rewrites_list = rewrites_list

    def __repr__(self):
        return (f"YtChannel(handle='{self.handle}', title='{self.title}', description='{self.description}', "
                f"last_videos_list={len(self.last_videos_list)} vídeos, "
                f"trending_videos_list={len(self.trending_videos_list)} vídeos)")
    

class YtVideoSugestion:
    def __init__(self, channelId, videoId, sugestion, fromType, videoTitle=None):
        self.channelId = channelId
        self.videoId = videoId
        self.sugestion = sugestion
        self.fromType = fromType
        self.videoTitle = videoTitle

    def __repr__(self):
        return (f"YtVideoSugestion(channelId='{self.channelId}', videoId='{self.videoId}', "
                f"sugestion='{self.sugestion}')")
    
class YtVideoRewrite:
    def __init__(self, channelId, videoId, rewrite, videoTitle=None):   
        self.channelId = channelId
        self.videoId = videoId
        self.rewrite = rewrite
        self.videoTitle = videoTitle

    def __repr__(self):
        return (f"YtVideoSugestion(channelId='{self.channelId}', videoId='{self.videoId}', "
                f"rewrite='{self.rewrite}')")
