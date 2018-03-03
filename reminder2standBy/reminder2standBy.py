#!/usr/bin/env python3

"""Python file to run Reminder to Stand By program
All program code and other files (except files in resources folder) distributed
under GNU GPLv3 license.
To read about license of resources files read "resources/sources" where you can
find information:
1) URL with file description (for most files)
or
2) Source of file and file usage rules (for moonOnBlue256.png)
"""

import sys, os

from PyQt4 import QtGui, QtCore

# other programs module
from  reminders_modules.tray import TrayController

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)  # start GUI Application and give args
    
    # load translations
    translator = QtCore.QTranslator(app)
    translator.load(os.path.join(
        sys.path[0],
        'i18n',
        'reminder_%s.qm' % QtCore.QLocale().name()
    ))
    app.installTranslator(translator)
    
    # set icon used in taskbar, when settings opened
    app_icon = QtGui.QIcon(os.path.join(
        sys.path[0],
        'resources',
        'moonOnBlue256.png'
    ))
    app.setWindowIcon(app_icon)  # not changing icon on Linux - use *.desktop file
    
    tray_obj = TrayController()
    tray_obj.set_menu(# Drawing menu
        app.quit,  # app.quit similar to app.exit(0)
        app_icon
    )
    
    sys.exit(# exit called, with result of app.exit()
        app.exec()  # running app
    )

# TODO: create .deb package, create .desktop files there, do not forget about dependency including python3
# TODO: distribute trough PPA

# TODO: more tests after renaming

# TODO: create Windows program version. Delete unnecessary code to set icon. Save settings, in same directory as main .py file.
# TODO: complete functions, that controllers is disabled in GUI (settings window) (when track sound try not to be reseted by sounds this program created)

"""May be useful information:

if need Xlib
sudo apt-get install python3-xlib
but for last version
sudo pip3 install python3-xlib
 
if need Linux terminal listener:
Identify your keyboard id with: xinput --list
Log keystrokes with: xinput --test $id
Match numbers to keys with: xmodmap -pke"""
