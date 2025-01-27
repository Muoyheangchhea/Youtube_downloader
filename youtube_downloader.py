import streamlit as st
from pytube import YouTube
import os
from urllib.parse import urlparse, parse_qs
from datetime import datetime

def on_progress(stream, chunk, bytes_remaining):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    percentage_completed = bytes_downloaded / total_size * 100
    st.session_state.progress = percentage_completed

@st.cache_data()
def download_video(url, resolution, download_audio, custom_path):
    st.session_state.progress = 0
    st.session_state.status = "Downloading..."
    st.session_state.progress_text = st.empty()

    try:
        yt = YouTube(url, on_progress_callback=on_progress)

        if download_audio:
            stream = yt.streams.filter(only_audio=True).first()
            ext = "mp3"
        else:
            stream = yt.streams.filter(res=resolution).first()
            ext = "mp4"

        if not custom_path:
            custom_path = os.path.join(os.path.expanduser("~"), "Downloads")

        if not os.path.exists(custom_path):
            os.makedirs(custom_path)

        download_path = os.path.join(custom_path, f"{yt.title}.{ext}")

        if stream is None:
            raise ValueError("No stream found for the selected resolution or type.")

        stream.download(output_path=custom_path, filename=f"{yt.title}.{ext}")
        st.session_state.status = "Downloaded!"
        st.session_state.download_history.append({"Title": yt.title, "URL": url, "Path": download_path})

    except Exception as e:
        st.session_state.status = f"Error: {str(e)}"

def validate_url(url):
    try:
        parsed_url = urlparse(url)
        if parsed_url.scheme in ["http", "https"]:
            if parsed_url.netloc in ["www.youtube.com", "youtube.com", "youtu.be"]:
                if parsed_url.netloc == "youtu.be":
                    return True
                elif parsed_url.path == "/watch" and "v" in parse_qs(parsed_url.query):
                    return True
        return False
    except ValueError:
        return False

def get_video_details(url):
    yt = YouTube(url)
    title = yt.title
    author = yt.author
    publish_date = yt.publish_date
    length = yt.length
    return title, author, publish_date, length

def clear_history():
    st.session_state.download_history = []
    st.session_state.status = "Download history cleared."

def delete_history_entry(index):
    if index < len(st.session_state.download_history):
        del st.session_state.download_history[index]
        st.session_state.status = "Entry deleted from download history."

if 'url' not in st.session_state:
    st.session_state.url = ""

if 'resolution' not in st.session_state:
    st.session_state.resolution = "720p"

if 'progress' not in st.session_state:
    st.session_state.progress = 0

if 'status' not in st.session_state:
    st.session_state.status = ""

if 'download_audio' not in st.session_state:
    st.session_state.download_audio = False

if 'custom_path' not in st.session_state:
    st.session_state.custom_path = os.path.join(os.path.expanduser("~"), "Downloads")

if 'download_history' not in st.session_state:
    st.session_state.download_history = []

st.title("YouTube Downloader")

st.text_input("Enter the YouTube URL here:", key='url')

if validate_url(st.session_state.url):
    st.video(st.session_state.url)
    title, author, publish_date, length = get_video_details(st.session_state.url)
    st.write(f"**Title:** {title}")
    st.write(f"**Author:** {author}")
    st.write(f"**Published Date:** {publish_date.strftime('%Y-%m-%d')}")
    st.write(f"**Length:** {length} seconds")

resolutions = ["720p", "480p", "360p", "240p"]
st.selectbox("Select resolution:", resolutions, key='resolution')
st.checkbox("Download audio only", key='download_audio')

custom_path_input = st.text_input("Custom download path:", value=st.session_state.custom_path)
st.session_state.custom_path = custom_path_input

if st.button("Download"):
    if validate_url(st.session_state.url):
        download_video(st.session_state.url, st.session_state.resolution, st.session_state.download_audio, st.session_state.custom_path)
    else:
        st.session_state.status = "Please enter a valid YouTube URL."

st.text(st.session_state.status)

st.write("## Download History")

if st.button("Clear History"):
    clear_history()

columns = st.columns(4)
columns[0].write("Title")
columns[1].write("URL")
columns[2].write("Path")
columns[3].write("Actions")

for index, entry in enumerate(st.session_state.download_history):
    with st.container():
        col1, col2, col3, col4 = st.columns(4)
        col1.write(entry["Title"])
        col2.write(entry["URL"])
        col3.write(entry["Path"])

        if col4.button("Open", key=f"open_{index}"):
            os.startfile(entry["Path"])

        if col4.button("Delete", key=f"delete_{index}"):
            delete_history_entry(index)
