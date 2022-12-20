import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from PIL import Image
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import numpy as np
import os
from pathlib import Path
import isodate
from statistics import mean
from numpy import diff

data_path = Path(__file__).parent / "data"
img_path = Path(__file__).parent / "img"

#layout
st.set_page_config(layout="wide")

page_bg = f"""
<style>
[data-testid='stAppViewContainer'] {{
    background-image: url('https://i.gadgets360cdn.com/large/eminem_bayc_ape_nft_opensea_twitter_large_1641207298788.jpg?downsize=950:*')
}}
</style>
"""

# st.markdown(page_bg, unsafe_allow_html=True)
st.title("an exploratory analysis on eminem")


with st.sidebar:
    st.markdown("""
        <center>
        <ul style="list-style-type: none;">
            <li><img src="https://cdn.albumoftheyear.org/artists/sq/eminem_1579280783.jpg" alt="Eminem" style="border-radius: 50%; width: 250px; height: 250px;"></li>
            <li></br></li>
            <li>Marshall Bruce Mathers A.K.A Eminem</li>
        </ul>
        <ul style="list-style-type: none;">
        <li>First Artist to Have 10 Consecutive Number-One Albums</li>
            <li>First Rapper to Win an Oscar</li>
            <li>15 Grammys</li>
            <li>Top selling artist of the 2000s</li>
            <li>Broke 2 Guinness World Records For Fast Rapping</li>
        </ul>
        <ul style="list-style-type: none;">
        <li><b><i>“You don’t get another chance, life is no Nintendo game.”</i><b></li>
        </ul>
        </center>
    """,unsafe_allow_html=True)

#cols
time_cols = ['duration']
datetime_cols = ['uploaded_at']
    
#conversion
convert_to_minutes = lambda duration: round(isodate.parse_duration(duration).total_seconds()/60,2)
    
#dataframes
albums = pd.read_json(f'{data_path}/processed_albums.json', lines=True)
songs = pd.read_json(f'{data_path}/processed_songs.json', lines=True)
eminem_yt = pd.read_csv(f'{data_path}/eminem_yt.csv')
eminem_yt[datetime_cols] = eminem_yt[datetime_cols].astype('datetime64')

words_by_album = songs.groupby(by='album', as_index=False).agg(sum)

title = st.container()
content = st.container()
dataset = st.container()
visualization = st.container()
youtube = st.container()
references = st.container()
wave = st.container()

with dataset:
    albums_dataset, songs_dataset = dataset.columns(2)
    #adding albums dataset
    albums_dataset.title(f'albums ({len(albums)})')
    albums_dataset.write(albums[['album','songs','year']].head(len(albums)))

    #adding songs dataset
    songs_dataset.title(f'songs ({len(songs)})')
    songs_dataset.write(songs[['album','title','lyrics']].head(len(songs)))
    dataset.markdown("""<h6 style="text-align: right;">analysis has been performed on feasible scraped data &#128591;</h6><br>""",unsafe_allow_html=True)


with visualization:
    # visualization.title("let's take a look :eyes:")
    visualization.markdown("""
        <center>
        <img src="https://media.tenor.com/DKdtevWRXvsAAAAC/lets-have-a-look-gill.gif" width="546" height="546" alt="Lets Have A Look Gill GIF - Lets Have A Look Gill Engvid GIFs" style="max-width: 546px;">
        </center>
    """,unsafe_allow_html=True)
    visualization.write('\n')
    words_rapped, music_duration = visualization.columns(2)
    words_rapped.subheader(f":speaking_head_in_silhouette: {songs['words'].sum()} words")
    music_duration.subheader("{} seconds/ {} minutes/ {} hours of :musical_note:".format(songs['duration_in_secs'].sum(),songs['duration_in_mins'].sum(),round(songs['duration_in_mins'].sum()/60,2)))

    visualization.header('albums & songs')
    #albums -> remove donut_album and replace with a sankey chart (year -> album -> song)
    year_label = []
    year_label.extend(albums['year'])
    album_label = []
    album_label.extend(albums['album'])
    song_label = []
    for i in albums['songs']:
        song_label.extend(i)
    all_labels = []
    all_labels.extend(year_label +  album_label + song_label)

    key_value = {v: i for i,v in enumerate(all_labels)}
    # print(key_value)

    #dataframe -> year, album, title
    # print(albums[['year','album','songs']])
    p_data = albums[['year','album','songs']]
    # p_data['songs'] = p_data['songs'].str.len()
    year_album = p_data.groupby(['year','album']).count().reset_index()
    temp = p_data
    temp['songs'] = temp['songs'].str.len()
    album_song = temp[['album','songs']]

    year_album['songs'] = album_song['songs']
    year_album.columns = ['source','target','value']
    # print(year_album)

    exploded_songs = albums[['album','songs']].explode('songs')
    exploded_songs['value'] = 5
    exploded_songs.columns = ['source','target','value']
    # print(exploded_songs)
    links = pd.concat([year_album,exploded_songs])
    # print(links)

    links['source'] = links['source'].map(key_value)
    links['target'] = links['target'].map(key_value)

    links_dict = links.to_dict(orient='list')


    fig = go.Figure(data=[go.Sankey(
        node = dict(
        #   line = dict(color = "black", width = 0.5),
        label = all_labels,
        color = "green"
        ),
        link = dict(
        source = links_dict["source"],
        target = links_dict["target"],
        value = links_dict["value"],
        color = 'purple'
    ))])
    fig.update_layout(
    autosize=False,
    width=1000,
    height=5380,
    margin=dict(t=0,b=0),title_text="Eminem Album", font_size=10)

    visualization.plotly_chart(fig, theme='streamlit', use_container_width=True)

    visualization.header('album composition')
    donut_album = go.Figure(data=[go.Pie(values=albums['song_count'],labels=albums['album'], hole=0.5, title='albums')])
    donut_album.update_layout(margin=dict(t=0, b=0, l=0, r=0))
    visualization.plotly_chart(donut_album, theme='streamlit', use_container_width=True)

    #words_rapped by album
    visualization.header('words in each album')
    bar = px.bar(words_by_album, x="album", y="words", barmode='group')
    # bar.update_layout(margin=dict(t=0, b=0, l=0, r=0))
    visualization.plotly_chart(bar, theme='streamlit', use_container_width=True)

    critic_score_line, user_score_line = visualization.columns(2)
    #user vs critics (linechart)
    critic_score_line.header('critic rating')
    critic_score = px.line(albums.query('critic_score != 0'), x='year', y='critic_score', markers=True, hover_data=['critic_rating'])
    critic_score_line.plotly_chart(critic_score, theme='streamlit', use_container_width=True)

    user_score_line.header('user rating')
    user_score = px.line(albums, x='year', y='user_score', markers=True, hover_data=['user_rating'])
    # user_score.update_layout(margin = dict(t=0, b=0, l=0, r=0))
    user_score_line.plotly_chart(user_score, theme='streamlit', use_container_width=True)

    visualization.markdown("""<h6 style="text-align: right;">scores obtained from <a href='https://www.albumoftheyear.org/artist/104-eminem/'>albumoftheyear.org<a></h6>""",unsafe_allow_html=True)

    box_left, box_mid, box_right = visualization.columns([1,3,1])
    box_mid.header('distribution of words')
    words_box = px.violin(songs, y='words', height=800, box=True,hover_data=['title'], points='all', )
    box_mid.plotly_chart(words_box, theme='streamlit', use_container_width=True)

    visualization.image(f'{img_path}/blue-wordcloud.jpg', use_column_width='auto', caption='most used words of all his songs')

with youtube:
    #picking up top 5 most viewed video
    most_viewed = eminem_yt[['title','views']].sort_values(by=['views'], ascending=[False])[0:10][::-1]
    most_viewed_bar = px.bar(most_viewed, x='views', y='title', orientation='h', title='most viewed music video')
    youtube.plotly_chart(most_viewed_bar, theme='streamlit', use_container_width=True)
    
    #picking up top 5 videos by likes
    most_liked = eminem_yt[['title','likes']].sort_values(by=['likes'], ascending=[False])[0:10][::-1]
    most_liked_bar = px.bar(most_liked, x='likes', y='title', orientation='h', title='most liked music video')
    youtube.plotly_chart(most_liked_bar, theme='streamlit', use_container_width=True)
    
    #distibution of videos
    year_df = eminem_yt[['uploaded_at','views']]
    year_df['year'] = year_df['uploaded_at'].dt.year
    year_grouped = year_df[['year','views']].groupby('year', as_index=False).sum()
    # video_dist = px.histogram(year_grouped, x = year_grouped['year'], y=year_grouped['views'], nbins=10, height=800, hover_data=['year'], title='Distribution of YouTube Views')
    # video_dist.update_layout(bargap=0.01, nbins=20)
    # violin_left, violin, violin_right = youtube.columns([1,2,1])
    # visualization.plotly_chart(video_dist, theme='streamlit', use_container_width=True)
    
    #view trends
    view_trend = px.line(year_grouped, x='year', y='views', title='YouTube views trend', text='year', width=1200, height=800)
    youtube.plotly_chart(view_trend, theme='streamlit', use_container_width=True)
    
    #popular day of upload
    eminem_yt['day_of_week'] = eminem_yt['uploaded_at'].dt.day_name()
    days_of_upload = eminem_yt.groupby('day_of_week', as_index=False).count()
    day_pie = px.pie(days_of_upload, values='title', names = 'day_of_week', title='YouTube day of upload')
    day_pie.update_layout(margin=dict(t=30, b=30, l=30, r=30))
    upload_left, upload, upload_right = youtube.columns([1,2,1])
    upload.plotly_chart(day_pie, theme='streamlit', use_container_width=True)
    
with references:
    references.title('data sources')
    st.markdown('**:point_right: _https://www.azlyrics.com/e/eminem.html_**')
    st.markdown('**:point_right: _https://www.albumoftheyear.org/artist/104-eminem/_**')
    st.markdown('**:point_right: _https://en.wikipedia.org/wiki/Eminem_**')
    st.markdown('**:point_right: _https://developers.google.com/youtube/v3_**')

with wave:
    wave.write('')
    wave.markdown("""
        <center>
        <img src="https://media.tenor.com/lx88s7ymScAAAAAC/bye-wave.gif" width="683" height="379.065" alt="Bye Wave GIF - Bye Wave Eminem GIFs" style="max-width: 683px; border-radius: 5%;">
        </center>
    """,unsafe_allow_html=True)
    # wave.markdown("""<center><img src="https://media.tenor.com/IcQhcOKnPuIAAAAC/eminem-bowing-eminem-encore.gif" width="683" height="384.0160642570281" alt="Eminem Bowing Eminem Encore GIF - Eminem Bowing Eminem Encore Eminem Encore Bow GIFs" style="max-width: 683px;"><center>""",unsafe_allow_html=True)
    # wave.markdown("<h1 style='text-align: center; color: black; font-size: 100px'>&#128075;</h1>", unsafe_allow_html=True)
