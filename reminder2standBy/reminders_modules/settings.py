"""Enable user change settings.

Store settings in *.ini file and make settings available for program.
"""

import os
import sys
from datetime import timedelta
from configparser import SafeConfigParser, NoSectionError, NoOptionError

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import QTime

# other programs modules
from reminders_modules.timer_events import MainTimer
from reminders_modules import autostart

# import window module
from reminders_windows.settings_win import Ui_settingsWin

# configuration file - time in seconds
# SettingEntry - time in timedeltas
# Qt widgets - time in QTime

PROGRAMM_NAME = 'rem_to_standby'
PROGRAMM_RUN_PATH = 'python3 ' + \
    os.path.join(sys.path[0], 'reminder2standBy.py')
CONFIG_FILE_PATH = os.path.join(
    os.path.expanduser("~"),
    '.reminders_config'
)
# CONFIG_FILE_PATH = os.path.join(sys.path[0], 'reminders_config')


class SettingEntry():
    """One setting entry."""

    def __init__(self, name, data_type, section, gui_widget, default_value):
        """Create SettingEntry.

        :param name: setting name
        :type name: str
        :param data_type: timedelta or bool can be used
        :type data_type: str
        :param section: timings or track
        :type section: str
        :param gui_widget: Qt GUI widget object
        :type gui_widget: Qt GUI widget object
        :param default_value: value that will be user if error in *.ini file or
            if file does not exist
        :type default_value: int, bool ...
        """
        self._name = name
        self.data_type = data_type
        self.section = section
        self.gui_widget = gui_widget
        self.set_value(default_value)

    def set_value(self, value):
        """Change value for this setting.

        :param value: new value
        :type value: int, bool ...
        """
        if self.data_type == 'timedelta':
            self.value = timedelta(seconds=value)
        else:
            self.value = value


class SettingList():
    """Group of settings."""

    def __init__(self, *settings_elements):
        """Create SettingList.

        :param *settings_elements: numerous tuple objects to initialize
            numerous SettingEntry
        :type *settings_elements: SettingEntry
        """
        self._settings_data = {}
        self._unique_sections = set()
        for entry in settings_elements:
            self._settings_data[entry[0]] = SettingEntry(*entry)
            self._unique_sections.add(entry[2])

    def __getitem__(self, key):
        """To make object act as dictionary.

        Following is possible:
        x=SettingList()
        val=x['key']

        :param key: SettingEntry name
        :type key: str

        :returns: value inside SettingEntry object
        :rtype: timedelta, bool...
        """
        return self._settings_data[key].value

    def import_from_parser(self, parser):
        """Load data from *.ini file into program.

        Note: load settings one by one, because part of file may be corrupted

        :param parser: SafeConfigParser object
        :type parser: SafeConfigParser
        """
        for entry in self._settings_data.values():
            if entry.data_type == 'timedelta':
                value = parser.getint(entry.section, entry._name)
            else:
                value = parser.getboolean(entry.section, entry._name)

            entry.set_value(value)

    def export2gui(self):
        """Take data from program and fills GUI widget values."""
        for entry in self._settings_data.values():
            if entry.data_type == 'timedelta':
                entry.gui_widget.setTime(
                    QTime(
                        0,
                        entry.value.total_seconds() // 60,
                        entry.value.total_seconds() % 60
                    )
                )
            else:
                entry.gui_widget.setChecked(entry.value)

    def import_from_gui(self):
        """Take GUI widget values and make it current program values."""
        for entry in self._settings_data.values():
            if entry.data_type == 'timedelta':
                time = entry.gui_widget.time()
                value = time.minute() * 60 + time.second()
            else:
                value = entry.gui_widget.isChecked()
            entry.set_value(value)

    def export2parser(self, parser):
        """Take data from program and save it into *.ini file.

        :param parser: SafeConfigParser object
        :type parser: SafeConfigParser
        """
        for section in self._unique_sections:
            parser[section] = {}  # We should init every section
        for entry in self._settings_data.values():
            if entry.data_type == 'timedelta':
                value = int(
                    entry.value.total_seconds()
                )
            else:
                value = entry.value
            parser[entry.section][entry._name] = str(value)


class SettingsManager(QtGui.QMainWindow):
    """Works with setting window."""

    def __init__(self, tray, icon, parent=None):
        """Create SettingsManager.

        :param tray: TrayController object
        :type tray: TrayController
        :param icon: QIcon object
        :type icon: QIcon
        """
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_settingsWin()
        self.ui.setupUi(self)
        self.setFixedSize(self.size())  # disable resize
        # not changing icon on Linux - use *.desktop file
        self.setWindowIcon(icon)

        # here we connect signals with our slots
        QtCore.QObject.connect(
            self.ui.bottomBb,
            QtCore.SIGNAL("rejected()"),
            self.hide_button
        )
        QtCore.QObject.connect(
            self.ui.bottomBb,
            QtCore.SIGNAL("accepted()"),
            self.save_button
        )

        # setup SettingList and provide default values
        self.current_configuration = SettingList(
            ('bored', 'timedelta', 'timings', self.ui.boringTe, 180),
            ('remind1', 'timedelta', 'timings', self.ui.remindTe, 300),
            (
                'continuously', 'timedelta', 'timings',
                self.ui.continuouslyTe, 600
            ),
            ('put_stand_by', 'timedelta', 'timings', self.ui.standbyTe, 900),

            ('keyboard', 'bool', 'track', self.ui.keyboardCb, True),
            ('mouse', 'bool', 'track', self.ui.mouseCb, True),
            ('sound', 'bool', 'track', self.ui.soundCb, False),
        )

        # reading settings configuration file
        parser = SafeConfigParser()
        parser.read(CONFIG_FILE_PATH)
        try:
            self.current_configuration.import_from_parser(parser)
        except (NoSectionError, NoOptionError):
            tray.show_message(QtCore.QCoreApplication.translate(
                'SettingsManager',
                'Error reading configuration file.\n'
                'You can stop this message by saving configuration in settings'
                ' window.'
            ))

        # export configuration file and autostart check result to GUI
        self.current_configuration.export2gui()
        self.ui.autostartCb.setChecked(
            autostart.exists(PROGRAMM_NAME)
        )

        self.main_timer = MainTimer(self, tray)

    def closeEvent(self, event):
        """On corner "X" button press reaction."""
        event.ignore()
        self.hide_button()

    def hide_button(self):
        """On "Close" (one of two button in bottom) press reaction."""
        self.hide()
        # export configuration file and autostart check result to GUI
        self.current_configuration.export2gui()
        self.ui.autostartCb.setChecked(
            autostart.exists(PROGRAMM_NAME)
        )

    def save_button(self):
        """On "Save" (one of two button in bottom) press reaction."""
        self.hide()
        self.current_configuration.import_from_gui()
        # refreshing listeners
        self.main_timer.enable_needed_listeners()

        # writing settings to configuration file
        conf_writer = SafeConfigParser()
        self.current_configuration.export2parser(conf_writer)
        with open(CONFIG_FILE_PATH, 'w') as configfile:
            conf_writer.write(configfile)
        # saving autostart settings
        if self.ui.autostartCb.isChecked():
            autostart.add(PROGRAMM_NAME, PROGRAMM_RUN_PATH)
        else:
            autostart.remove(PROGRAMM_NAME)
