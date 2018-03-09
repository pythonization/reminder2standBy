"""Package that describe all GUI Windows.

generated from *.ui files with commands, such a:
pyuic4 reminders_windows/settings_win.ui > reminders_windows/settings_win.py
"""

from . import settings_win

# useful if "from reminders_modules import *" will be called. Also prevent
# warnings in pyflakes
__all__ = [
    'settings_win',
]
