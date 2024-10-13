# DirectPlay - Sangeet Radio

[![Author](https://img.shields.io/badge/Author-Robotics%20(R)-blue.svg)](https://github.com/robotic-s)
[![Version](https://img.shields.io/badge/Version-1.0.0.1.1-brightgreen.svg)](https://github.com/Direct-Play/releases)
![Direct Play Sangeet Radio](https://github.com/robotic-s/Direct-Play/blob/main/sangeet%20radio)
## Project Overview

DirectPlay is a Python-based YouTube Music streaming player that allows users to search for, stream, and display song lyrics in a terminal interface. The project leverages `ytmusicapi` and `yt-dlp` to stream audio directly from YouTube Music and fetch song metadata, including lyrics when available. It also integrates `mpv` for smooth playback and provides a simple command-line interface for playback management.

## Key Features

- **Music Streaming**: Stream audio from YouTube Music with automatic URL extraction using `yt-dlp`.
- **Lyrics Display**: Fetch and display song lyrics in real-time, including both synchronized and non-synchronized formats, using `ytmusicapi`.
- **Player Controls**: Manage playback controls directly from the terminal.
- **Educational Purpose**: This project is meant for educational purposes, showcasing how to interact with online APIs and manage audio playback in Python.
- **Cross-Platform Support**: The project works on any platform where Python and `mpv` are supported.

## Getting Started

1. Clone the repository to your local machine:
   ```
   git clone https://github.com/robotic-s/Direct-Play.git
   cd Direct-Play
   ```

2. Install the necessary dependencies:
   ```
   pip install -r package
   ```
3. For Termux:
   ```
   pkg install mpv
   ```
4. If Issue in termux try updating it:
   ```
   pkg update
   pkg upgrade
   ```
5. For linux:
   ```
   sudo apt update && sudo apt upgrade -y 
   sudo apt install mpv
   ```
6. If yt-dlp is installed through pip or pipx, you can install the plugin with the following:

pip:

python3 -m pip install -U https://github.com/coletdjnz/yt-dlp-youtube-oauth2/archive/refs/heads/master.zip
pipx:

pipx inject yt-dlp https://github.com/coletdjnz/yt-dlp-youtube-oauth2/archive/refs/heads/master.zip
7. Run the player:
   ```
   python directplay.py
   ```
   or
   ```
   python3 directplay.py
   ```

## In-Player Controls

Once the player is running, you will have access to basic player controls directly from the terminal. (You may want to add specific control instructions here.)

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details. It is open for educational purposes and contributions are welcome.

## Disclaimer

This project is for educational purposes only. Please respect copyright laws and terms of service for all platforms used.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

If you encounter any problems or have any questions, please open an issue in the GitHub repository.
