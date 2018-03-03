"""Module with user actions listeners, to react on user activity"""

import threading

# Used module PyUserInput. Can be installed with:
# sudo pip3 install PyUserInput
from pykeyboard import PyKeyboardEvent  
from pymouse import PyMouseEvent


class CommonListener():
    """Common listeners functions"""
    
    def __init__(self, object2notify):
        """object2notify - object with property "notification_flag"
        property type is threading.Event()
        property is set when event ocurred
        """
        self._object2notify = object2notify
        self.should_notify=threading.Event()
        self.should_notify.clear()
    
    def notify_if_should(self):
        """Notify _object2notify object if listener is active (should_notify
        flag is set)
        """
        if self.should_notify.is_set():
            self._object2notify.notification_flag.set()


class KeyboardListener(PyKeyboardEvent, CommonListener):
    """Listen keyboard"""
    
    def __init__(self, object2notify):
        """object2notify - MainTimer object"""
        CommonListener.__init__(self, object2notify)
        PyKeyboardEvent.__init__(self)
        
    # reactions on keyboard - notify _object2notify
    def tap(self, keycode, character, press):
        """Parent class PyKeyboardEvent call this method when user tap
        keyboard key. See PyUserInput documentation for parameter meaning.
        """
        self.notify_if_should()


class MouseListener(PyMouseEvent, CommonListener):
    """Listen mouse"""
    
    def __init__(self, object2notify):
        """object2notify - MainTimer object"""
        CommonListener.__init__(self, object2notify)
        PyMouseEvent.__init__(self)

    # reactions on mouse - notify _object2notify
    def click(self, x, y, button, press):
        """Parent class PyMouseEvent call this method when user click mouse
        key. See PyUserInput documentation for parameter meaning.
        """
        self.notify_if_should()
 
    def move(self, x, y):
        """Parent class PyMouseEvent call this method when user move mouse.
        """
        self.notify_if_should()
        
    def scroll(self, x, y, vertical, horizontal):
        """Parent class PyMouseEvent call this method when user scroll mouse.
        """
        self.notify_if_should()
