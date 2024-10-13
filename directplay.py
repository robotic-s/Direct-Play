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
PLAYER = os.path.join(os.getcwd() , "mpv" , "mpv.exe")
# Initialize colorama
init(autoreset=True)

# Dictionary to store the current mpv process
process_dict = {'mpv_process': None}

# Regular expression to match YouTube and YouTube Music URLs
youtube_url_regex = re.compile(r'(https?://)?(www\.)?(music\.)?(youtube\.com|youtu\.be)/.+')

def clear_terminal(keep_art=True):
    """Clear the terminal screen, with an option to keep ASCII art at the top."""
    os.system('cls' if os.name == 'nt' else 'clear')
    if keep_art:
        show_ascii_art()

def show_ascii_art():
    """Display the colorful ASCII art for Sangeet Radio."""
    ascii_art = pyfiglet.figlet_format("Sangeet Radio", font="slant")
    print(Fore.CYAN + ascii_art + Style.RESET_ALL)
    print("\n" + "=" * 50)
    print("Welcome to DirectPlay")
    print("=" * 50)
    print("Author      : Robotics (R)")
    print("Version     : 1.0.0.1.1")
    print("Support     : Non-LTS")
    print("=" * 50)

def is_youtube_url(input_text):
    """Check if the input is a YouTube or YouTube Music URL."""
    return youtube_url_regex.match(input_text)

def extract_video_id(youtube_url):
    """Extract the video ID from a YouTube or YouTube Music URL."""
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
    """Search for the song on YouTube Music and return the song details."""
    ytmusic = YTMusic()  # Ensure that ytmusicapi is authenticated
    search_results = ytmusic.search(song_name, filter='songs')
    
    if search_results:
        # Fetch details of the first search result
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
    """Extract the best audio URL using yt-dlp with optimal settings."""
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    
    ydl_opts = {
        'format': 'bestaudio/best',  # Get the best available audio format
        'noplaylist': True,
        'quiet': True,
        'get_url': True,  # Only retrieve the direct URL without downloading
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
    """Fetch lyrics using the provided video ID."""
    ytmusic = YTMusic()
    try:
        # Get the watch playlist to access the lyrics ID
        watch_playlist = ytmusic.get_watch_playlist(videoId=video_id)
        lyrics_browse_id = watch_playlist.get('lyrics')
        if lyrics_browse_id:
            # Fetch the lyrics using the browse ID
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
    """Print lyrics in colored text."""
    if lyrics:
        print(Fore.GREEN + "Lyrics:\n" + Fore.CYAN + lyrics)
    else:
        print(Fore.RED + "Lyrics not available.")

def handle_exit_signal(signal_received, frame):
    """Handle the exit signals and gracefully terminate processes."""
    print(Fore.RED + "\nExit signal received. Cleaning up..." + Style.RESET_ALL)
    kill_previous_process()  # Terminate any running mpv process
    sys.exit(0)  # Exit the program

def kill_previous_process():
    """Kill the previous mpv process if it exists."""
    if process_dict['mpv_process'] is not None:
        try:
            process_dict['mpv_process'].terminate()  # Terminate the process
            process_dict['mpv_process'].wait()  # Wait for process to finish
            print(f"Killed previous mpv process (PID: {process_dict['mpv_process'].pid})")
        except Exception as e:
            print(f"Error killing mpv process: {e}")
        finally:
            process_dict['mpv_process'] = None

def play_song(url):
    """Play the song using mpv without blocking the script."""
    system = os.name

    if system == "nt":
        process = subprocess.Popen([PLAYER, url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    elif system == "posix":
        process = subprocess.Popen(["mpv", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        print(f"Unknown system: {system}")
  
    process_dict['mpv_process'] = process
    print(f"Song is now playing (PID: {process.pid})...")

def main():
    # Register the signal handler for graceful exit
    signal.signal(signal.SIGINT, handle_exit_signal)
    signal.signal(signal.SIGTERM, handle_exit_signal)

    # Clear the terminal and show ASCII art
    clear_terminal()

    while True:
        song_name = input(Fore.YELLOW + "\nEnter the song name or YouTube URL, 'clear' to clear screen, 'download' to download song (or type 'exit' to quit): " + Style.RESET_ALL)

        if song_name.lower() == 'exit':
            print("Exiting the music player.")
            kill_previous_process()
            break

        if song_name.lower() == 'clear':
            clear_terminal(keep_art=True)
            continue

        if is_youtube_url(song_name):
            video_id = extract_video_id(song_name)
            if video_id:
                audio_url = get_audio_url(video_id)
                if audio_url:
                    kill_previous_process()
                    play_song(audio_url)
                    lyrics_json = get_lyrics(video_id)
                    lyrics = json.loads(lyrics_json).get('lyrics', None)
                    display_lyrics(lyrics)
                else:
                    print("Could not extract audio URL.")
            else:
                print("Could not extract video ID from the provided URL.")
        else:
            song_details = search_song(song_name)
            if song_details:
                video_id = song_details['videoId']
                audio_url = get_audio_url(video_id)
                if audio_url:
                    print(f"\nPlaying: {song_details['title']}")
                    print(f"Artist: {song_details['artist']}")
                    print(f"Album: {song_details['album']}\n")
                    kill_previous_process()
                    play_song(audio_url)
                    lyrics_json = get_lyrics(video_id)
                    lyrics = json.loads(lyrics_json).get('lyrics', None)
                    display_lyrics(lyrics)
                else:
                    print("Could not extract audio URL.")
            else:
                print("Could not find video ID for the song.")

if __name__ == "__main__":
    main()
