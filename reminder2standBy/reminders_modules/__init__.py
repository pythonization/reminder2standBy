"""All main program modules."""

from . import autostart, helpers, listeners, settings, sound_play, timer_events
from . import tray

# useful if "from reminders_modules import *" will be called. Also prevent
# warnings in pyflakes
__all__ = [
    'autostart', 'listeners', 'helpers', 'settings', 'sound_play',
    'timer_events', 'tray',
]
