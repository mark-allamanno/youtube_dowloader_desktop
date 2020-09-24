# Youtube Downloader Desktop
Simple desktop application to download Youtube videos.

# Installation
Download the main.py and downloader.py files in the repository and ensure all dependencies are installed. 

Additionally you will need to download, install, and add FFMPEG to the system PATH as it is needed for the conversion from mp4 to mp3.

# General Usage 
Run the program through the python interpreter and paste in either a link to a Youtube video or playlist. Once you do that you can either hit the enter key or the onscreen button to download the MP3's for the requested video(s). It will then ask you to specify a destination for the MP3's to be saved to. 

If you pasted in a link to a single video then the video will be saved under the name you entered. If you entered a link to a playlist then a directory will be created with the name you entered and the videos will be saved inside.

# Dependencies
Pytube3 - https://pypi.org/project/pytube3/

PyQt5 - https://pypi.org/project/PyQt5/

FFMPEG - https://ffmpeg.org/
