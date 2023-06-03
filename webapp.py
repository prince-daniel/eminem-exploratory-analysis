import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import isodate
import datetime

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
st.caption('analysis has been performed on feasible scraped data')

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
eminem_yt[datetime_cols] = eminem_yt[datetime_cols].astype('datetime64[ns]')

words_by_album = songs.groupby(by='album', as_index=False).agg(sum)

title = st.container()
content = st.container()
dataset = st.container()
visualization = st.container()
youtube = st.container()
references = st.container()
wave = st.container()

with visualization:
    visualization.title("let's take a look :eyes:")
   
    visualization.write('\n')
    
    words_rapped, music_duration = visualization.columns(2)
    words_rapped.subheader(f":speaking_head_in_silhouette: {songs['words'].sum()} words")
    music_duration.subheader("{} seconds/ {} minutes/ {} hours of :musical_note:".format(songs['duration_in_secs'].sum(),songs['duration_in_mins'].sum(),round(songs['duration_in_mins'].sum()/60,2)))

    visualization.header('albums & songs')
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

    p_data = albums[['year','album','songs']]

    year_album = p_data.groupby(['year','album']).count().reset_index()
    temp = p_data
    temp['songs'] = temp['songs'].str.len()
    album_song = temp[['album','songs']]

    year_album['songs'] = album_song['songs']
    year_album.columns = ['source','target','value']

    exploded_songs = albums[['album','songs']].explode('songs')
    exploded_songs['value'] = 5
    exploded_songs.columns = ['source','target','value']

    links = pd.concat([year_album,exploded_songs])

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

    visualization.plotly_chart(fig, theme=None, use_container_width=True)

    visualization.header('album composition')
    donut_album = go.Figure(data=[go.Pie(values=albums['song_count'],labels=albums['album'], hole=0.5, title='albums')])
    donut_album.update_layout(margin=dict(t=0, b=0, l=0, r=0))
    visualization.plotly_chart(donut_album, theme=None, use_container_width=True)

    #words_rapped by album
    visualization.header('words in each album')
    bar = px.bar(words_by_album, x="album", y="words", barmode='group')
    # bar.update_layout(margin=dict(t=0, b=0, l=0, r=0))
    visualization.plotly_chart(bar, theme='streamlit', use_container_width=True)

    critic_score_line, user_score_line = visualization.columns(2)
    #user vs critics (linechart)
    critic_score_df = albums.query('critic_score != 0')
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
    youtube.header('most viewed music video')
    most_viewed = eminem_yt[['title','views']].sort_values(by=['views'], ascending=[False])[0:10][::-1]
    most_viewed_bar = px.bar(most_viewed, x='views', y='title', orientation='h')
    youtube.plotly_chart(most_viewed_bar, theme='streamlit', use_container_width=True)
    
    #picking up top 5 videos by likes
    youtube.header('most like music video')
    most_liked = eminem_yt[['title','likes']].sort_values(by=['likes'], ascending=[False])[0:10][::-1]
    most_liked_bar = px.bar(most_liked, x='likes', y='title', orientation='h')
    youtube.plotly_chart(most_liked_bar, theme='streamlit', use_container_width=True)
    
    #distibution of videos
    youtube.header('YouTube views trend')
    year_df = eminem_yt[['uploaded_at','views']]
    year_df['year'] = year_df['uploaded_at'].dt.year
    year_grouped = year_df[['year','views']].groupby('year', as_index=False).sum()
    
    #view trends
    view_trend = px.line(year_grouped, x='year', y='views', text='year', width=1200, height=800)
    youtube.plotly_chart(view_trend, theme='streamlit', use_container_width=True)
    
    #popular day of upload
    youtube.header('YouTube uploads')
    video_uploads = pd.DataFrame(columns=['Morning','Afternoon','Evening','Night'], index=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'])
    video_uploads = video_uploads.fillna(0)
    #morning -> 6:00 AM to 11:59 AM
    #afternoon -> 12:00 PM to 16:59 PM
    #evening -> 17:00 PM to 20:59 PM
    #night -> 21:00 PM to 05:59 AM

    def time_of_day(py_datetime):
        morning_start = datetime.time(6,0,0)
        morning_end = datetime.time(11,59,59)
        afternoon_start = datetime.time(12,0,0)
        afternoon_end = datetime.time(16,59,59)
        evening_start = datetime.time(17,0,0) 
        evening_end = datetime.time(20,59,59)
        night_start = datetime.time(21,0,0)
        night_end = datetime.time(5,59,59)
        if morning_start <= py_datetime.time() <= morning_end:
            return 'Morning'
        elif afternoon_start <= py_datetime.time() <= afternoon_end:
            return 'Afternoon'
        elif evening_start <= py_datetime.time() <= evening_end:
            return 'Evening'
        else:
            return 'Night'

    def day_from_date(py_datetime):
        if py_datetime.strftime('%A') == 'Monday':
            return 'Monday' 
        if py_datetime.strftime('%A') == 'Tuesday':
            return 'Tuesday'
        if py_datetime.strftime('%A') == 'Wednesday':
            return 'Wednesday'
        if py_datetime.strftime('%A') == 'Thursday':
            return 'Thursday'
        if py_datetime.strftime('%A') == 'Friday':
            return 'Friday'
        if py_datetime.strftime('%A') == 'Saturday':
            return 'Saturday'
        if py_datetime.strftime('%A') == 'Sunday':
            return 'Sunday'

    def add_time_of_day(dt):
        py_datetime = dt.to_pydatetime()
        day = day_from_date(py_datetime)
        time = time_of_day(py_datetime)
        video_uploads.loc[day,time] = video_uploads.loc[day,time] + 1
        

    datetime_list = eminem_yt['uploaded_at'].to_list()
    for dt in datetime_list:
        add_time_of_day(dt)
        
    heat_map = px.imshow(video_uploads, labels=dict(color='Video Upload'),height=800)
    heat_map.update_xaxes(side='top')
    
    youtube.plotly_chart(heat_map,theme=None,use_container_width=True)

with references:
    references.title('data sources')
    st.markdown('_https://www.azlyrics.com/e/eminem.html_')
    st.markdown('_https://www.albumoftheyear.org/artist/104-eminem/_')
    st.markdown('_https://en.wikipedia.org/wiki/Eminem_')
    st.markdown('_https://developers.google.com/youtube/v3_')

with wave:
    wave.write('')
    wave.markdown("""
        <center>
        <img src="https://media.tenor.com/lx88s7ymScAAAAAC/bye-wave.gif" width="683" height="379.065" alt="Bye Wave GIF - Bye Wave Eminem GIFs" style="max-width: 683px; border-radius: 5%;">
        </center>
    """,unsafe_allow_html=True)

    
