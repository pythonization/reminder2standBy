"""Module, that plays sounds in separate thread.

Module imports another module PyAudio. Can be installed with:
sudo apt-get install python-pyaudio python3-pyaudio
Module analogs: audiere, PyMedia
"""

import pyaudio
import wave
import threading

from common_qt_app.helpers import give_name2thread

# TODO: try Muting error messages, that shows in console
# but code from
# http://stackoverflow.com/questions/7088672/pyaudio-working-but-spits-out-error-messages-each-time
# is not working

CHUNK = 1024
pyaudio_obj = pyaudio.PyAudio()


class AsyncMusic(threading.Thread):
    """Class for playing music in separate thread."""

    def __init__(self, sound_path):
        """Create AsyncMusic object.

        :param sound_path: path string where .wav sound located
        :type sound_path: str
        """
        threading.Thread.__init__(self)
        self._sound_path = sound_path

    def run(self):
        """Plays sound.

        Note: calling this function directly will call it in current thread.
        So current thread will wait while sound is playing.
        You might want to call it using .start() function - then it will be
        called in separate thread
        """
        give_name2thread('playing_song_' + self._sound_path, self)

        with wave.open(self._sound_path, 'rb') as sound_file:
            stream = pyaudio_obj.open(
                format=pyaudio_obj.get_format_from_width(
                    sound_file.getsampwidth()
                ),
                channels=sound_file.getnchannels(),
                rate=sound_file.getframerate(),
                output=True
            )

            data = sound_file.readframes(CHUNK)
            while len(data):
                stream.write(data)
                data = sound_file.readframes(CHUNK)

            stream.stop_stream()
            stream.close()
            # this line was in original tutorial, but seems I do not need it
#             pyaudio_obj.terminate()
