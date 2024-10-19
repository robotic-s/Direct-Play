from ytmusicapi import YTMusic
import yt_dlp
import subprocess
import os
import signal
import re
import sys
from colorama import init, Fore, Style
import json
import pyfiglet
from collections import deque
import concurrent.futures

import urllib.request

def download_file(url, save_dir):
    # Send a request to the URL
    response = urllib.request.urlopen(url)
    
    # Get the 'Content-Disposition' header
    content_disposition = response.headers.get('Content-Disposition')

    # Extract the filename from the 'Content-Disposition' header
    filename = None
    if content_disposition:
        # Regex to extract filename
        filename_match = re.findall('filename="(.+)"', content_disposition)
        if filename_match:
            filename = filename_match[0]
    
    # If filename isn't found in the headers, use the last part of the URL as a fallback
    if not filename:
        filename = os.path.basename(url)

    # Create the full file path
    save_path = os.path.join(save_dir, filename)
    
    # Write the content to the file
    with open(save_path, 'wb') as file:
        file.write(response.read())
    
  




if not os.path.exists(os.path.join(os.getcwd(), "mpv", "mpv.exe")):
    download_file("https://github.com/robotic-s/Direct-Play/releases/download/Asset/mpv.exe",os.path.join(os.getcwd(), "mpv"))
PLAYER = os.path.join(os.getcwd(), "mpv", "mpv.exe")
init(autoreset=True)

process_dict = {'mpv_process': None}
youtube_url_regex = re.compile(r'(https?://)?(www\.)?(music\.)?(youtube\.com|youtu\.be)/.+')

ytmusic = YTMusic()
queue = deque()
played_songs = set()

def clear_terminal(keep_art=True):
    os.system('cls' if os.name == 'nt' else 'clear')
    if keep_art:
        show_ascii_art()

def show_ascii_art():
    ascii_art = pyfiglet.figlet_format("Sangeet Radio", font="slant")
    print(Fore.CYAN + ascii_art + Style.RESET_ALL)
    print("\n" + "=" * 50)
    print("Welcome to Enhanced DirectPlay")
    print("=" * 50)
    print("Author      : Robotics (R)")
    print("Version     : 2.1.0")
    print("Support     : Non-LTS")
    print("=" * 50)

def is_youtube_url(input_text):
    return youtube_url_regex.match(input_text)

def extract_video_id(youtube_url):
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'username': 'oauth2',
        'config-location': 'yt-dlp.conf',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(youtube_url, download=False)
        return result.get('id') if result else None

def search_song(song_name):
    search_results = ytmusic.search(song_name, filter='songs')
    
    if search_results:
        best_match = search_results[0]
        song_details = {
            'title': best_match['title'],
            'artist': best_match['artists'][0]['name'] if best_match['artists'] else 'Unknown Artist',
            'album': best_match['album']['name'] if 'album' in best_match else 'Unknown Album',
            'videoId': best_match['videoId']
        }
        return song_details
    else:
        print(f"Song '{song_name}' not found.")
        return None

def get_audio_url(video_id):
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'get_url': True,
        'username': 'oauth2',
        'config-location': 'yt-dlp.conf',
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(video_url, download=False)
        if 'url' in result:
            if "itag=774" in result['url']:
                print("Got the premium stream!")
            elif "itag=251" in result['url']:
                print("Got regular stream")
            else:
                print("Playing the best available stream")
            return result['url']
    return None

def get_lyrics(video_id):
    try:
        watch_playlist = ytmusic.get_watch_playlist(videoId=video_id)
        lyrics_browse_id = watch_playlist.get('lyrics')
        if lyrics_browse_id:
            lyrics_data = ytmusic.get_lyrics(lyrics_browse_id)
            if lyrics_data and 'lyrics' in lyrics_data:
                return json.dumps({
                    'status': 'success',
                    'lyrics': lyrics_data['lyrics'],
                    'source': "Sangeet One..."
                }, indent=4)
        return json.dumps({
            'status': 'not_found',
            'message': 'No lyrics available for this song.'
        }, indent=4)
    except Exception as e:
        return json.dumps({
            'status': 'error',
            'message': str(e)
        }, indent=4)

def display_lyrics(lyrics):
    if lyrics:
        print(Fore.GREEN + "Lyrics:\n" + Fore.CYAN + lyrics)
    else:
        print(Fore.RED + "Lyrics not available.")

def handle_exit_signal(signal_received, frame):
    print(Fore.RED + "\nExit signal received. Cleaning up..." + Style.RESET_ALL)
    kill_previous_process()
    clear_queue()
    sys.exit(0)

def kill_previous_process():
    if process_dict['mpv_process'] is not None:
        try:
            process_dict['mpv_process'].terminate()
            process_dict['mpv_process'].wait()
            print(f"Killed previous mpv process (PID: {process_dict['mpv_process'].pid})")
        except Exception as e:
            print(f"Error killing mpv process: {e}")
        finally:
            process_dict['mpv_process'] = None

def play_song(url):
    system = os.name

    if system == "nt":
        process = subprocess.Popen([PLAYER, url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    elif system == "posix":
        process = subprocess.Popen(["mpv", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        print(f"Unknown system: {system}")
  
    process_dict['mpv_process'] = process
    print(f"Song is now playing (PID: {process.pid})...")

def get_recommendations(video_id):
    watch_playlist = ytmusic.get_watch_playlist(videoId=video_id)
    recommendations = watch_playlist.get('tracks', [])
    return [track['videoId'] for track in recommendations if track['videoId'] not in played_songs]

def add_to_queue(video_id):
    if video_id not in queue and video_id not in played_songs:
        queue.append(video_id)

def clear_queue():
    queue.clear()
    played_songs.clear()

def get_yt_dlp_details(video_id):
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
        'username': 'oauth2',
        'config-location': 'yt-dlp.conf',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(video_url, download=False)
            return {
                'title': info.get('title', 'Unknown Title'),
                'artist': info.get('artist', 'Unknown Artist'),
                'album': info.get('album', 'Unknown Album'),
            }
        except Exception as e:
            print(f"Error fetching details from yt-dlp: {str(e)}")
            return None

def get_ytmusic_details(video_id):
    try:
        song_details = ytmusic.get_song(video_id)
        return {
            'title': song_details.get('title', 'Unknown Title'),
            'artist': song_details.get('artists', [{'name': 'Unknown Artist'}])[0]['name'],
            'album': song_details.get('album', {'name': 'Unknown Album'})['name'],
        }
    except Exception as e:
        print(f"Error fetching details from ytmusic: {str(e)}")
        return None

def get_song_details(video_id):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        ytmusic_future = executor.submit(get_ytmusic_details, video_id)
        yt_dlp_future = executor.submit(get_yt_dlp_details, video_id)
        
        ytmusic_result = ytmusic_future.result()
        yt_dlp_result = yt_dlp_future.result()
    
    if ytmusic_result and ytmusic_result['title'] != 'Unknown Title':
        return ytmusic_result
    elif yt_dlp_result:
        return yt_dlp_result
    else:
        return {
            'title': 'Unknown Title',
            'artist': 'Unknown Artist',
            'album': 'Unknown Album',
        }

def play_next_song():
    if queue:
        next_video_id = queue.popleft()
        played_songs.add(next_video_id)
        audio_url = get_audio_url(next_video_id)
        if audio_url:
            kill_previous_process()
            play_song(audio_url)
            
            song_details = get_song_details(next_video_id)
            print(f"\nNow Playing: {song_details['title']}")
            print(f"Artist: {song_details['artist']}")
            print(f"Album: {song_details['album']}\n")
            
            lyrics_json = get_lyrics(next_video_id)
            lyrics = json.loads(lyrics_json).get('lyrics', None)
            display_lyrics(lyrics)
            
            # Add new recommendations to the queue
            new_recommendations = get_recommendations(next_video_id)
            for rec_id in new_recommendations:
                add_to_queue(rec_id)
        else:
            print("Could not extract audio URL. Playing next song.")
            play_next_song()
    else:
        print("Queue is empty. Please search for a song.")

def main():
    signal.signal(signal.SIGINT, handle_exit_signal)
    signal.signal(signal.SIGTERM, handle_exit_signal)

    clear_terminal()

    while True:
        options = ["Enter the song name or YouTube URL", "'clear' to clear screen"]
        if queue:
            options.append("'next' for next song")
        options.append("'exit' to quit")
        
        prompt = Fore.YELLOW + f"\n{', '.join(options)}: " + Style.RESET_ALL
        song_name = input(prompt)

        if song_name.lower() == 'exit':
            print("Exiting the music player.")
            kill_previous_process()
            clear_queue()
            break

        if song_name.lower() == 'clear':
            clear_terminal(keep_art=True)
            continue

        if song_name.lower() == 'next':
            if queue:
                play_next_song()
            else:
                print("No songs in queue. Please search for a song.")
            continue

        if is_youtube_url(song_name):
            video_id = extract_video_id(song_name)
        else:
            song_details = search_song(song_name)
            if song_details:
                video_id = song_details['videoId']
                print(f"\nFound: {song_details['title']}")
                print(f"Artist: {song_details['artist']}")
                print(f"Album: {song_details['album']}\n")
            else:
                video_id = None

        if video_id:
            clear_queue()  # Clear the queue when a new song is explicitly requested
            add_to_queue(video_id)
            play_next_song()
            
            # Add recommendations to the queue
            recommendations = get_recommendations(video_id)
            for rec_id in recommendations:
                add_to_queue(rec_id)
        else:
            print("Could not find video ID for the song.")

if __name__ == "__main__":
    main()
