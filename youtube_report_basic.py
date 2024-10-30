from youtube_db import get_all
import sqlite3
import pandas as pd
from rich.console import Console
from rich.markdown import Markdown
from io import BytesIO
import markdown
from weasyprint import HTML

def create_dataframe(channels_list):
    data = []

    for channel in channels_list:
        for video in channel.last_videos_list:
            data.append({
                'channelId': channel.channelId,
                'channelHandle': channel.handle,
                'channelTitle': channel.title,
                'channelTescription': channel.description,
                'video_list_type': 'last_videos',
                'videoId': video.videoId,
                'videoTitle': video.title,
                'viewCount': video.viewCount,
                'publishedAt': video.publishedAt
            })

        for video in channel.trending_videos_list:
            data.append({
                'channelId': channel.channelId,
                'channelHandle': channel.handle,
                'channelTitle': channel.title,
                'channelTescription': channel.description,
                'video_list_type': 'trending_videos',
                'videoId': video.videoId,
                'videoTitle': video.title,
                'viewCount': video.viewCount,
                'publishedAt': video.publishedAt
            })

    df = pd.DataFrame(data)
    return df



if __name__ == "__main__":
    markdown_report = ""

    conn = sqlite3.connect('youtube_db.sqlite3')
    channels = get_all(conn)

    markdown_channels = "# CANAIS\n\n"
    
    for c in channels:
        markdown_channels += f"- [{c.handle}](https://www.youtube.com/{c.handle}) - {c.title}\n"

    markdown_report += markdown_channels + "\n\n"

    for c in channels:
        markdown_channel = (
            f"# Canal {c.title} ({c.handle})\n\n"
            f"{c.description}\n\n"
            f"Link para o canal: [https://www.youtube.com/{c.handle}](https://www.youtube.com/{c.handle})\n\n"
        )

        markdown_channel += "## Vídeos em alta\n\n"
        for v in c.trending_videos_list:
            markdown_channel += f"- [{v.title}](https://www.youtube.com/watch?v={v.videoId}) ({v.viewCount} views)\n"

        markdown_channel += "\n"
        
        markdown_channel += "## Vídeos mais recentes\n\n"
        for v in c.last_videos_list:
            markdown_channel += f"- [{v.title}](https://www.youtube.com/watch?v={v.videoId}) ({v.viewCount} views)\n"

        markdown_channel += "\n\n"

        markdown_report += markdown_channel

    console = Console()
    console.print(Markdown(markdown_report))

    with open('report_basic.md', 'w') as md_file:
        md_file.write(markdown_report)

    html_content = markdown.markdown(markdown_report)
    pdf = HTML(string=html_content).write_pdf()

    with open('report_basic.pdf', 'wb') as pdf_file:
        pdf_file.write(pdf)