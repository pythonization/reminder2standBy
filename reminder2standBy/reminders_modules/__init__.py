"""All main program modules."""

from . import autostart, listeners, settings, sound_play, timer_events, tray

# useful if "from reminders_modules import *" will be called. Also prevent
# warnings in pyflakes
__all__ = [
    'autostart', 'listeners', 'settings', 'sound_play', 'timer_events', 'tray',
]
