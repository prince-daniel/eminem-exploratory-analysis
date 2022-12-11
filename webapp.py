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

st.title("an exploratory analysis on eminem's")


with st.sidebar:
    st.markdown("""
        <center>
        <ul style="list-style-type: none;">
            <li><img src="https://cdn.albumoftheyear.org/artists/sq/eminem_1579280783.jpg" alt="Eminem" style="border-radius: 50%; width: 250px; height: 250px;"></li>
            <li></br></li>
            <li>17 October 1972</li>
        </ul>
        <ul style="list-style-type: none;">
        <li><b>notable achievements</b></li>
        <li>First Artist to Have 10 Consecutive Number-One Albums</li>
            <li>First Rapper to Win an Oscar</li>
            <li>Bagged 15 Grammys</li>
            <li>Top selling artist of the 2000s</li>
            <li>Broke 2 Guinness World Records For Fast Rapping</li>
        </ul>
        <ul style="list-style-type: none;">
        <li><i>“You don’t get another chance, life is no Nintendo game.”</i></li>
        </ul>
        </center>
    """,unsafe_allow_html=True)
    # st.caption("an outsider who proved himself. he had a turbulent childhood, marked by poverty and allegations of abuse")

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
    dataset.markdown("""<h6 style="text-align: right;">analysis has been performed on feasible scraped data and also exluding intro, interlude, skit & outro &#128591;</h6>""",unsafe_allow_html=True)
    # dataset.markdown("""<h6 style="text-align: right;">* </h6>""",unsafe_allow_html=True)

with visualization:
    visualization.title("let's take a look :eyes:")
    words_rapped, music_duration = visualization.columns(2)
    words_rapped.subheader(f":speaking_head_in_silhouette: {songs['words'].sum()} words")
    music_duration.subheader("{} seconds/ {} minutes/ {} hours of :musical_note:".format(songs['duration_in_secs'].sum(),songs['duration_in_mins'].sum(),round(songs['duration_in_mins'].sum()/60,2)))

    #albums
    # album_piechart = px.pie(albums, values='song_count',names='album',title="album overview")
    donut_album = go.Figure(data=[go.Pie(values=albums['song_count'],labels=albums['album'], hole=0.5, title='albums')])
    # donut_album.update_layout(margin=dict(t=0, b=0, l=0, r=0))
    visualization.write(donut_album)

    #words_rapped by album
    bar = px.bar(words_by_album, x="album", y="words", barmode='group')
    bar.update_layout(margin=dict(t=0, b=0, l=0, r=0))
    visualization.write(bar)
    # bar = px.bar(songs[['album','title','words']],x='album',y='words', color='title')
    # bar.update_layout(margin=dict(t=0, b=0, l=0, r=0))
    # visualization.write(bar)

    critic_score_line, user_score_line = visualization.columns(2)
    #user vs critics (linechart)
    critic_score = px.line(albums.query('critic_score != 0'), x='year', y='critic_score', markers=True, hover_data=['critic_rating'])
    # critic_score.update_layout(margin = dict(t=0, b=0, l=0, r=0))
    critic_score_line.write(critic_score)

    user_score = px.line(albums, x='year', y='user_score', markers=True, hover_data=['user_rating'])
    # user_score.update_layout(margin = dict(t=0, b=0, l=0, r=0))
    user_score_line.write(user_score)

    visualization.markdown("""<h6 style="text-align: right;">scores obtained from <a href='https://www.albumoftheyear.org/artist/104-eminem/'>albumoftheyear.org<a></h6>""",unsafe_allow_html=True)

    words_box = px.box(songs[['words']], y='words')
    # words_box.update_layout(margin = dict(t=0, b=0, l=250, r=250))
    visualization.write(words_box)

    visualization.image(f'{img_path}/blue-wordcloud.jpg', use_column_width='auto')

with youtube:
    #picking up top 5 most viewed video
    most_viewed = eminem_yt[['title','views']].sort_values(by=['views'], ascending=[False])[0:10][::-1]
    most_viewed_bar = px.bar(most_viewed, x='views', y='title', orientation='h', title='Most Viewed Videos')
    youtube.write(most_viewed_bar)
    
    #picking up top 5 videos by likes
    most_liked = eminem_yt[['title','likes']].sort_values(by=['likes'], ascending=[False])[0:10][::-1]
    most_liked_bar = px.bar(most_liked, x='likes', y='title', orientation='h', title='Most Liked Videos')
    youtube.write(most_liked_bar)
    
    #distibution of videos
    year_df = eminem_yt[['uploaded_at','views']]
    year_df['year'] = year_df['uploaded_at'].dt.year
    year_grouped = year_df[['year','views']].groupby('year', as_index=False).sum()
    video_dist = px.violin(year_grouped, y = year_grouped['views'], box=True, # draw box plot inside the violin
                points='all', width=600, height=1200, hover_data=['year'], title='Distribution of Views by Year')
    # video_dist.update_layout(margin=dict(t=0, b=0, l=350, r=350))
    youtube.write(video_dist)
    
    #view trends
    view_trend = px.line(year_grouped, x='year', y='views', title='View Trends', text='year', width=1200, height=800)
    youtube.write(view_trend)
    
    #popular day of upload
    eminem_yt['day_of_week'] = eminem_yt['uploaded_at'].dt.day_name()
    days_of_upload = eminem_yt.groupby('day_of_week', as_index=False).count()
    day_pie = px.pie(days_of_upload, values='title', names = 'day_of_week', title='Day Of Uploads')
    youtube.write(day_pie)
    
with references:
    references.title('data sources')
    st.markdown('**:point_right: _https://www.azlyrics.com/e/eminem.html_**')
    st.markdown('**:point_right: _https://www.albumoftheyear.org/artist/104-eminem/_**')
    st.markdown('**:point_right: _https://en.wikipedia.org/wiki/Eminem_**')

with wave:
    wave.write('')
    wave.markdown("""
        <center>
        <img src="https://media.tenor.com/lx88s7ymScAAAAAC/bye-wave.gif" width="683" height="379.065" alt="Bye Wave GIF - Bye Wave Eminem GIFs" style="max-width: 683px; border-radius: 5%;">
        </center>
    """,unsafe_allow_html=True)
    # wave.markdown("""<center><img src="https://media.tenor.com/IcQhcOKnPuIAAAAC/eminem-bowing-eminem-encore.gif" width="683" height="384.0160642570281" alt="Eminem Bowing Eminem Encore GIF - Eminem Bowing Eminem Encore Eminem Encore Bow GIFs" style="max-width: 683px;"><center>""",unsafe_allow_html=True)
    # wave.markdown("<h1 style='text-align: center; color: black; font-size: 100px'>&#128075;</h1>", unsafe_allow_html=True)

    
        
   
    
    
