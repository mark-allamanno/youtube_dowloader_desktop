from PyQt5.QtCore import pyqtSignal, QObject, pyqtSlot

from pytube import YouTube, Playlist, Stream
from pytube.exceptions import PytubeError

import os
import re
import string
import subprocess


class Downloader(QObject):

    # Various signals and slots for cross thread communication
    error_occurred = pyqtSignal(PytubeError)
    update_progress_bar = pyqtSignal(Stream, int)
    download_complete = pyqtSignal()

    def __init__(self):
        # Call to the super class constructor and set the number of downloads to zero
        super(Downloader, self).__init__()
        self.num_downloads = 0
        self.num_completed = 0

    @pyqtSlot(str, str)
    def download(self, url, filepath):
        try:
            # If the url has the term playlist in it then use the playlist download feature
            if 'playlist' in url:
                self.__download_playlist(url, filepath)
            # Otherwise use the regular single video download feature
            else:
                self.__download_video(url, filepath)
        # If we encountered a Pytube error when executing tell the gui to say something
        except PytubeError as e:
            self.error_occurred.emit(e)

    def __download_video(self, url, filepath):
        # Get the video and stream for the specified video
        video = YouTube(url, on_progress_callback=self.update_gui)
        stream = video.streams.filter(only_audio=True).first()

        # Since we are only downloading a single video the number of downloads is one
        self.num_downloads = 1

        # Then do some regex stuff to separate the filename from the path
        split = filepath.rfind('/')
        path = filepath[0:split]
        filename = filepath[split + 1:]

        # Then download and save the video to the given location and filename
        stream.download(output_path=path, filename=filename)
        abs_path = os.path.join(path, filename)

        # Converts the downloaded mp4 to an mp3 using the ffmpeg subprocess if the user wants to
        subprocess.run(['ffmpeg', '-i',
                        abs_path + '.mp4', abs_path + '.mp3',
                        ])

        # Remove the mp4 and returns the path to the mp3
        os.remove(abs_path + '.mp4')

        # Let the user know their download has finished
        self.download_complete.emit()

    def __download_playlist(self, url, filepath):
        # Make a directory using the path the user gave to us
        os.mkdir(filepath)

        # Make a new playlist object and fix the video parsing error
        playlist = Playlist(url)
        playlist._video_regex = re.compile(r"\"url\":\"(/watch\?v=[\w-]*)")

        # Since we are downloading a playlist the number of downloads is the length of the playlist
        self.num_downloads = len(playlist.video_urls)

        for url in playlist.video_urls:
            # Get the video and stream for the specified video
            video = YouTube(url, on_progress_callback=self.update_gui)
            stream = video.streams.filter(only_audio=True).first()

            # Since the user cannot specify each filename we just use the video title and then download it
            filename = video.title.translate(str.maketrans('', '', string.punctuation))
            stream.download(output_path=filepath, filename=filename)
            abs_path = os.path.join(filepath, filename)

            # Converts the downloaded mp4 to an mp3 using the ffmpeg subprocess if the user wants to
            subprocess.run(['ffmpeg', '-i',
                            abs_path + '.mp4', abs_path + '.mp3',
                            ])

            # Remove the mp4 and returns the path to the mp3
            os.remove(abs_path + '.mp4')

            # We have one less video to download
            self.num_completed += 1

        # Let the user know their download has finished
        self.download_complete.emit()

    def update_gui(self, stream=None, chunk=None, remaining=None):
        # Update the GUI's progress bar in accordance with out progress
        self.update_progress_bar.emit(stream, remaining)
