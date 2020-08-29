import sys

from PyQt5.QtCore import QThread, pyqtSlot, pyqtSignal, Qt
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLineEdit, QFileDialog, QLabel, QProgressBar, \
    QMessageBox, QGridLayout, QShortcut
from PyQt5.QtGui import QKeySequence

from pytube import Stream
from pytube.exceptions import PytubeError, VideoUnavailable, RegexMatchError, LiveStreamError

from downloader import Downloader


class SimpleGUI(QWidget):

    # A single signal to tell the downloader to begin a download
    start_download = pyqtSignal(str, str)

    def __init__(self):
        super(SimpleGUI, self).__init__()

        # Create a new thread of the downloader to run in when the time comes
        self.thread = QThread()

        # Create all of the QWidgets we need for the program
        self.label = QLabel('Youtube URL', self)
        self.textbox = QLineEdit(self)
        self.button = QPushButton('Download MP3', self)
        self.layout = QGridLayout(self)
        self.current_vid = QLabel('', self)
        self.progress = QProgressBar(self)

        # Create the downloader object and configure it
        self.downloader = Downloader()
        self.init_downloader()

        # Set a quick shortcut to be able to hit enter instead of clicking the button to download
        self.shortcut = QShortcut(QKeySequence(Qt.Key_Return), self)
        self.shortcut.activated.connect(self.download)

        # Then configure all the widgets
        self.init_ui()

    def init_ui(self):
        # Setup the basic attributes of the application
        self.setWindowTitle('Youtube Downloader')
        self.setGeometry(400, 300, 500, 70)

        # Add a little prompt so we know what the box is for
        self.layout.addWidget(self.label, 0, 0)

        # Add the box to actually input the url
        self.layout.addWidget(self.textbox, 1, 0)
        self.textbox.resize(300, 30)

        # Add the button to download the recipe
        self.button.resize(130, 30)
        self.layout.addWidget(self.button, 1, 1)

        # Add the progress bar and label to the window
        self.layout.addWidget(self.current_vid, 2, 0)
        self.layout.addWidget(self.progress, 3, 0)

        # Then promptly hide them until they are needed
        self.progress.hide()
        self.current_vid.hide()

        # If the button is clicked then trigger the download
        self.button.clicked.connect(self.download)

        # Center and show the window to the user
        self.center_on_screen()
        self.setLayout(self.layout)
        self.show()

    def init_downloader(self):
        # Connect all of the downloader's signals to all of the GUI's slots
        self.downloader.error_occurred.connect(self.show_error)
        self.downloader.update_progress_bar.connect(self.update_progress)
        self.downloader.download_complete.connect(self.download_complete)

        # Connect the single GUI signal to the downloader's slot
        self.start_download.connect(self.downloader.download)

        # Move the downloader to another thread and start that thread
        self.downloader.moveToThread(self.thread)
        self.thread.start()

    def center_on_screen(self):
        # Shout out to this excellent article on how to center the window on the screen
        # https://pythonprogramminglanguage.com/pyqt5-center-window/
        rect = self.frameGeometry()
        center_pt = QApplication.primaryScreen().availableGeometry().center()
        rect.moveCenter(center_pt)
        self.move(rect.topLeft())

    def download(self):

        if self.textbox.text() != '':
            # Hide the window before we show the file dialog
            self.hide()
            # Get the filepath and url form the user's inputs
            filepath, ext = QFileDialog.getSaveFileName(self, 'MP3 Save Location')
            url = self.textbox.text()

            if filepath != '':
                # If the didnt hit cancel then show the progress bar and label
                self.progress.show()
                self.current_vid.show()
                # Then start the download of the requested videos
                self.start_download.emit(url, filepath)

            # Then show the window again
            self.show()

    @pyqtSlot(Stream, int)
    def update_progress(self, stream=None, remaining=None):
        # Get the rough percentage progress, that being bytes downloaded over total bytes
        ind_progress = (100 * ((stream.filesize - remaining) / stream.filesize)) / self.downloader.num_downloads
        tot_progress = 100 * (self.downloader.num_completed / self.downloader.num_downloads)

        # If we have some bytes remaining then we are still downloading
        if 0 < remaining:
            self.current_vid.setText(stream.title)
        # Otherwise we are converting the video to MP3 format
        else:
            self.current_vid.setText('Converting Video...')

        # Then update the progress bar byte percentage of the current video over all remaining videos
        self.progress.setValue(int(ind_progress) + int(tot_progress))

    @pyqtSlot()
    def download_complete(self):
        # Create a new message box, and set its window title, and brief message
        dialog = QMessageBox()
        dialog.setWindowTitle('Download Complete!')
        dialog.setText('The specified videos have been downloaded and converted')

        # Hide the progress bar and label again as they arent needed
        self.progress.hide()
        self.current_vid.hide()

        # Show the dialog box to the user
        dialog.exec()

    @pyqtSlot(PytubeError)
    def show_error(self, error):
        # Create a new message box and set its title
        dialog = QMessageBox()
        dialog.setWindowTitle('PyTube 3 Error')

        # Then get the error strings based on the exception type and set them
        header, message = self.get_error_strings(error)
        dialog.setText(header)
        dialog.setInformativeText(message)

        # Set the icon for the window and show it to the user
        dialog.setIcon(QMessageBox.Critical)
        dialog.exec_()

    @staticmethod
    def get_error_strings(error):
        # Get the header and message depending on the type of error encountered
        if type(error) == VideoUnavailable:
            header = 'Video Unavailable Error'
            message = 'PyTube 3 cannot download the current video as it is not available via Youtube'
        elif type(error) == RegexMatchError:
            header = 'Regex Match Error'
            message = 'The URL you entered did not return any matches. Make sure the URL you entered is correct'
        elif type(error) == LiveStreamError:
            header = 'Live Stream Error'
            message = 'The URL you entered refers to a live stream so it cannot be downloaded'
        else:
            header = 'Unknown Error'
            message = "Something went wrong and we're not quite sure what. Please try again"
        # Then return them to the caller
        return header, message


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = SimpleGUI()
    app.exec()
