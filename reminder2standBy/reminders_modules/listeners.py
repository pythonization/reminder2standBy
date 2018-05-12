"""Module with user actions listeners, to react on user activity."""

import threading

# Used module PyUserInput. Can be installed with:
# sudo pip3 install PyUserInput
from pykeyboard import PyKeyboardEvent
from pymouse import PyMouseEvent

from common_qt_app.helpers import give_name2thread


class CommonListener():
    """Common listeners functions."""

    def __init__(self, object2notify):
        """Create CommonListener.

        :param object2notify: object with property "notification_flag"
            property type is threading.Event()
            property is set when event ocurred
        """
        self._object2notify = object2notify
        self.should_notify = threading.Event()
        self.should_notify.clear()

    def notify_if_should(self):
        """Notify _object2notify object if listener is active.

        (Will do action if should_notify flag is set.)
        """
        if self.should_notify.is_set():
            self._object2notify.notification_flag.set()


class KeyboardListener(PyKeyboardEvent, CommonListener):
    """Listen keyboard."""

    def __init__(self, object2notify):
        """Create KeyboardListener.

        :param object2notify: MainTimer object
        :type object2notify: MainTimer
        """
        CommonListener.__init__(self, object2notify)
        PyKeyboardEvent.__init__(self)

    # reactions on keyboard - notify _object2notify
    def tap(self, keycode, character, press):
        """Parent class PyKeyboardEvent call this method when user tap keyboard key.

        See PyUserInput documentation for parameter meaning.
        """
        give_name2thread('keyboard_event_thread', self)
        self.notify_if_should()

    def escape(self, event):
        """Determine when to stop listening.

        event - from this can get that key is pressed

        Always return False, to never stop.
        (I do not want to stop keyboard listener in my program.)
        (The default behavior WAS to stop when the 'Esc' key is pressed.)
        (Should not stop using this way, because then keyboard listening thread
        will consume 100% of CPU thread.)

        :returns: False
        :rtype: bool
        """
        return False


class MouseListener(PyMouseEvent, CommonListener):
    """Listen mouse."""

    def __init__(self, object2notify):
        """Create MouseListener.

        :param object2notify: MainTimer object
        :type object2notify: MainTimer
        """
        CommonListener.__init__(self, object2notify)
        PyMouseEvent.__init__(self)

    # reactions on mouse - notify _object2notify
    def click(self, x, y, button, press):
        """Parent class PyMouseEvent call this method when user click mouse key.

        See PyUserInput documentation for parameter meaning.
        """
        self.notify_if_should()

    def move(self, x, y):
        """Parent class PyMouseEvent call this method when user move mouse."""
        give_name2thread('mouse_event_thread', self)
        self.notify_if_should()

    def scroll(self, x, y, vertical, horizontal):
        """User scroll mouse.

        Called by parent class PyMouseEvent when user do this.
        """
        self.notify_if_should()
