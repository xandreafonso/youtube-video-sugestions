CREATE TABLE YtChannelInfo (
    channelId TEXT PRIMARY KEY,
    handle TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT
);

CREATE TABLE YtVideoInfo (
    videoId TEXT PRIMARY KEY,
    channelId TEXT NOT NULL,
    title TEXT NOT NULL,
    viewCount INTEGER,
    publishedAt TEXT,
    FOREIGN KEY (channelId) REFERENCES YtChannelInfo (channelId)
);

CREATE TABLE YtVideoSugestion (
    channelId TEXT NOT NULL,
    videoId TEXT NOT NULL,
    sugestion TEXT NOT NULL,
    fromType TEXT NOT NULL,
    FOREIGN KEY (channelId) REFERENCES YtChannelInfo (channelId),
    FOREIGN KEY (videoId) REFERENCES YtVideoInfo (videoId)
);

CREATE TABLE YtVideoRewrite (
    channelId TEXT NOT NULL,
    videoId TEXT NOT NULL,
    rewrite TEXT NOT NULL,
    FOREIGN KEY (channelId) REFERENCES YtChannelInfo (channelId),
    FOREIGN KEY (videoId) REFERENCES YtVideoInfo (videoId)
);
