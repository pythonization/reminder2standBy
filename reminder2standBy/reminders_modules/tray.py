"""Module for displaying tray icon, and working with its context menu."""

import os
import sys

from PyQt4.QtGui import QMenu, QIcon, QSystemTrayIcon
from PyQt4 import QtCore

# other programs module
from reminders_modules.settings import SettingsManager

PROGRAMM_RESOURCE_PATH = os.path.join(sys.path[0], 'resources')


class TrayController():
    """Display and control context menu."""

    setings_win = None

    def __init__(self):
        """Create TrayController."""
        self._tray_ico = QSystemTrayIcon()

    def set_menu(self, quit_callable, app_icon):
        """Show context menu and sets all its items.

        :param quit_callable: function to call when user choose Exit menu item
        :type quit_callable: function
        :param app_icon: QIcon object - tray icon image
        :type app_icon: QIcon
        """
        tray_menu = QMenu()

        self._delay_menu = tray_menu.addAction(
            QIcon(
                os.path.join(PROGRAMM_RESOURCE_PATH, 'k-timer-icon.png')
            ),
            QtCore.QCoreApplication.translate('TrayController', 'Delay')
        )
        delay_sub_menu = QMenu()
        delay_sub_menu.addAction(
            QtCore.QCoreApplication.translate('TrayController', '15 minutes'),
            self.action_delay15
        )
        delay_sub_menu.addAction(
            QtCore.QCoreApplication.translate('TrayController', '30 minutes'),
            self.action_delay30
        )
        delay_sub_menu.addAction(
            QtCore.QCoreApplication.translate('TrayController', '1 hour'),
            self.action_delay60
        )
        delay_sub_menu.addAction(
            QtCore.QCoreApplication.translate('TrayController', '2 hours'),
            self.action_delay120
        )
        self._delay_menu.setMenu(delay_sub_menu)

        self._resume_menu = tray_menu.addAction(
            QIcon(
                os.path.join(PROGRAMM_RESOURCE_PATH,
                             'App-Quick-restart-icon.png')
            ),
            QtCore.QCoreApplication.translate('TrayController', 'Resume'),
            self.action_resume
        )
        self._resume_menu.setVisible(False)

        tray_menu.addAction(
            QIcon(
                os.path.join(PROGRAMM_RESOURCE_PATH, 'Settings-icon.png')
            ),
            QtCore.QCoreApplication.translate('TrayController', 'Settings'),
            self.show_settings
        )
        tray_menu.addSeparator()
        tray_menu.addAction(
            QIcon(
                os.path.join(PROGRAMM_RESOURCE_PATH, 'delete-icon.png')
            ),
            QtCore.QCoreApplication.translate('TrayController', 'Exit'),
            quit_callable
        )

        self._tray_ico.setContextMenu(tray_menu)
        self._tray_ico.setToolTip(
            QtCore.QCoreApplication.translate(
                'TrayController', 'Reminder to Stand By'
            )
        )
        self._tray_ico.setIcon(app_icon)
        self._tray_ico.show()
        self.setings_win = SettingsManager(self, app_icon)

    def show_message(self, message):
        """Show message near tray icon.

        (alternative to show message is via module
        from PyQt4.QtGui import QMessageBox)

        :param message: message string
        :type message: str
        """
        self._tray_ico.showMessage(
            QtCore.QCoreApplication.translate(
                'TrayController', 'Reminder to Stand By'),
            message,
            msecs=5000
        )

    # Functions - menu click actions
    def toggle_delay_menu(self):
        """Toggle some context menu items.

        (depending program delay is on or off)
        """
        delay_on = self.setings_win.main_timer.delay_on
        self._resume_menu.setVisible(delay_on)
        self._delay_menu.setVisible(not delay_on)
        self.setings_win.ui.notActiveLb.setText(
            QtCore.QCoreApplication.translate('TrayController', 'Delay time')
            if delay_on else
            QtCore.QCoreApplication.translate(
                'TrayController', 'Time not active'
            )
        )

    def action_delay15(self):
        """User choose to delay program on 15 minutes."""
        self.setings_win.main_timer.set_work_delay(15)

    def action_delay30(self):
        """User choose to delay program on 30 minutes."""
        self.setings_win.main_timer.set_work_delay(30)

    def action_delay60(self):
        """User choose to delay program on 1 hour."""
        self.setings_win.main_timer.set_work_delay(60)

    def action_delay120(self):
        """User choose to delay program on 2 hours."""
        self.setings_win.main_timer.set_work_delay(120)

    def action_resume(self):
        """User cancel delay."""
        self.setings_win.main_timer.delay_on = False
        self.toggle_delay_menu()

    def show_settings(self):
        """Show settings window."""
        self.setings_win.show()
