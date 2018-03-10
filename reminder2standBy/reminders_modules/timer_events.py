"""Module to work with timer and react on events."""

# import prctl
import threading
import os
import sys
from datetime import datetime, timedelta
from time import sleep

from PyQt4 import QtCore
from PyQt4.QtCore import QTimer

# other programs modules
from reminders_modules.listeners import KeyboardListener, MouseListener
from reminders_modules.sound_play import AsyncMusic

STANDBY_EXIT_CATCHER = timedelta(seconds=5)
PROGRAMM_RESOURCE_PATH = os.path.join(sys.path[0], 'resources')


def put_system_standby():
    """Put system into standby."""
    os.system('systemctl suspend')
    # worked in 14.04
    # os.system(
    #     'dbus-send --system --print-reply --dest="org.freedesktop.UPower" '
    #     '/org/freedesktop/UPower org.freedesktop.UPower.Suspend'
    # )


class InfinityBeep(threading.Thread):
    """Play infinity beeping sound."""

    def __init__(self, sound_path):
        """Create InfinityBeep.

        sound_path - path where sound located
        """
        threading.Thread.__init__(self)
        self.stoprequest = threading.Event()
        self._player = AsyncMusic(sound_path)

    def run(self):
        """Plays endless beeps.

        Note: calling this function directly will call it in current thread.
        So current thread will wait while sound is playing.
        You might want to call it using .start() function - then it will be
        called in separate thread
        """
        # do not delete. thread name useful for searching bugs
        self.name = 'infinity_beep_th'
        # prctl.set_name('infinity_beep_th')

        self.stoprequest.clear()  # if stopped before, clear
        while not self.stoprequest.is_set():
            self._player.run()  # call and wait
            sleep(2)


class EventEntry():
    """Description of Event."""

    _fired = False

    def __init__(
        self, current_configuration, tray, name,

        sound_path=None, notification_text=None, function2do=None,
        thread2start=None
    ):
        """Create EventEntry.

        current_configuration - SettingsManager object
        tray - TrayController object
        name - event name (same as in current_configuration object)
        sound_path - if need to play sound, during event
        notification_text - if need to show message to user, during event
        function2do - function to execute during event
        thread2start - object that starts some work in separate thread during
        event
        """
        self.current_configuration = current_configuration
        self.tray = tray
        self._name = name
        self._sound_path = sound_path
        self._notification_text = notification_text
        self._function2do = function2do
        self._thread2start_class = thread2start

    def event_reaction(self, time_passed):
        """Fire event.

        Do its job if not fired before and time elapsed to fire event.
        time_passed - current elapsed time
        """
        if (
            (not self._fired) and
            (self.current_configuration[self._name] < time_passed)
        ):
            self._fired = True

            if self._function2do:
                self._function2do()

            if self._notification_text:
                self.tray.show_message(
                    self._notification_text
                )

            if self._thread2start_class:
                self._thread2start_obj = self._thread2start_class(
                    self._sound_path)
                self._thread2start_obj.start()
            elif self._sound_path:
                player = AsyncMusic(self._sound_path)
                player.start()

    def reset_fired(self):
        """Stop job started by event and reset it - so it can fire again."""
        if self._fired and hasattr(self, '_thread2start_obj'):
            self._thread2start_obj.stoprequest.set()  # stopping thread
        self._fired = False


class EventList():
    """Event group."""

    def __init__(self, *events):
        """Create EventList.

        *events - numerous of EventEntry objects
        """
        self._events = []
        for event in events:
            self._events.append(event)

    def event_reaction(self, time_passed):
        """Try to fire every event if they need to fire.

        time_passed - currently elapsed time
        """
        for event in self._events:
            event.event_reaction(time_passed)

    def reset_fired(self):
        """Stop job started by every event and reset them.

        So they can fire again
        """
        for event in self._events:
            event.reset_fired()


class MainTimer():
    """Count time and react on user activity listeners when need."""

    delay_on = False

    def __init__(self, settings_manager, tray):
        """Create MainTimer object.

        settings_manager - SettingsManager object
        tray - TrayController object
        """
        self.settings_manager = settings_manager
        self.tray = tray

        self._events = EventList(
            EventEntry(
                self.settings_manager.current_configuration, tray, 'bored',
                os.path.join(PROGRAMM_RESOURCE_PATH,
                             'Exhale-SoundBible.com-1772711989.wav'),
                QtCore.QCoreApplication.translate(
                    'MainTimer', 'Where are you, user?')
            ),
            EventEntry(
                self.settings_manager.current_configuration, tray, 'remind1',
                os.path.join(PROGRAMM_RESOURCE_PATH, 'beep-05.wav'),
                QtCore.QCoreApplication.translate(
                    'MainTimer', 'Why I am working?')
            ),
            EventEntry(
                self.settings_manager.current_configuration, tray,
                'continuously',
                os.path.join(PROGRAMM_RESOURCE_PATH, 'beep-05.wav'),
                thread2start=InfinityBeep
            ),
            EventEntry(
                self.settings_manager.current_configuration, tray,
                'put_stand_by',
                function2do=put_system_standby
            ),
        )

#         Event listeners part
        self.notification_flag = threading.Event()
        self.notification_flag.clear()
        self._keyboard = KeyboardListener(self)
        self._mouse = MouseListener(self)

        self.enable_needed_listeners()
        self._keyboard.start()
        self._mouse.start()

        # timer part
        self._last_active = datetime.now()
        self._last_timer_event = self._last_active  # initializing
        self._work_timer = QTimer()
        QtCore.QObject.connect(
            self._work_timer,
            QtCore.SIGNAL("timeout()"),
            self.timer_event
        )
        self._work_timer.start(200)

    def set_work_delay(self, delay_min):
        """Delays timer.

        delay_min - minutes to delay timer
        """
        self._delay_ends = datetime.now() + timedelta(seconds=delay_min * 60)
        self.delay_on = True
        self.tray.toggle_delay_menu()

    # timer
    def timer_event(self):
        """Work that should be done on every QTimer timeout() event."""
        if self.notification_flag.is_set():
            self.notification_flag.clear()
            self.reset_timer()

        # should be after self.reset_timer()
        # because reset_timer has is own datetime.now()
        now = datetime.now()

        # if program was not able to catch timer event some time
        # PC was on stand by, so we need to reset timer, to
        # stop continuous beeping and prevent program to re-put PC on stand by
        time_since_last_timer_event = now - self._last_timer_event
        if STANDBY_EXIT_CATCHER < time_since_last_timer_event:
            self.reset_timer()
        self._last_timer_event = now

        if self.delay_on:
            # user delayed program work
            time2display = self._delay_ends - now
            if self._delay_ends < now:
                # seems it is time to stop delay
                self.reset_timer()
                time2display = timedelta(seconds=0)
                self.delay_on = False
                self.tray.toggle_delay_menu()
        else:
            # normal mode - reaction if user is not active
            time2display = now - self._last_active
            self._events.event_reaction(time2display)  # time passed

        # display time passed since last activity / delay time
        total_sec = (time2display).total_seconds()
        self.settings_manager.ui.notActiveOutLb.setText(
            QtCore.QCoreApplication.translate(
                'MainTimer', '{0} min {1} s'
            ).format(
                    int(total_sec // 60),
                    int(total_sec % 60)
            )
        )

#         Event listeners part
    def reset_timer(self):
        """Reset timer if user do activity."""
        self._last_active = datetime.now()
        self._events.reset_fired()

    def thread_event_toggle(self, listener, config_param):
        """Enable/disable activity listener.

        listener - listener object
        config_param - name of configuration parameter
        """
        if self.settings_manager.current_configuration[config_param]:
            listener.should_notify.set()
        else:
            listener.should_notify.clear()

    def enable_needed_listeners(self):
        """Enable/disable listeners.

        (Check all activity listeners' preferences, to decide enable or not.)
        """
        self.thread_event_toggle(self._keyboard, 'keyboard')
        self.thread_event_toggle(self._mouse, 'mouse')
