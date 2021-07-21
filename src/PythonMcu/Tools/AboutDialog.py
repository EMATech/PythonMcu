# -*- coding: utf-8 -*-

"""
PythonMcu
=========
Mackie Host Controller written in Python
Copyright (c) 2011 Martin Zuther (http://www.mzuther.de/)
Copyright (c) 2021 Raphaël Doursenaud <rdoursenaud@free.fr>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

Thank you for using free software!

"""

import sys

if __name__ == "__main__":
    # allow "PythonMcu" package imports when executing this module
    sys.path.append('../../')

from PythonMcu.Tools.ApplicationConfiguration import *

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super(AboutDialog, self).__init__(parent)

        self._configuration = ApplicationConfiguration()
        self.setWindowTitle( \
            'About ' + self._configuration.get_application_information( \
                'application'))

        self._layout = QVBoxLayout()
        self.setLayout(self._layout)

        font = QFont()
        font.setStyleHint(QFont.TypeWriter, QFont.PreferAntialias)

        char_format = QTextCharFormat()
        char_format.setFontFamily(font.defaultFamily())
        text_width = QFontMetrics(char_format.font()).width('*') * 83
        text_height = QFontMetrics(char_format.font()).height() * 40

        self._edit_license = QTextBrowser()
        self._edit_license.setOpenExternalLinks(True)
        self._edit_license.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self._edit_license.setFixedWidth(text_width)
        self._edit_license.setFixedHeight(text_height)
        self._edit_license.setHtml( \
            self._configuration.get_full_description('html') + '<hr>' + \
                self._configuration.get_license('html'))

        self._layout.addWidget(self._edit_license)

        self._layout_2 = QHBoxLayout()
        self._layout.addLayout(self._layout_2)

        self._label_thanks = QLabel('Thank you for using free software!')
        self._layout_2.addWidget(self._label_thanks)

        self._button_close = QPushButton('I like &free software!')
        self._button_close.clicked.connect(self.close)
        self._layout_2.addWidget(self._button_close)


if __name__ == '__main__':
    # Create the Qt Application
    app = QApplication(sys.argv)

    # Create and show the license dialog
    about_dialog = AboutDialog()
    about_dialog.show()

    # Run the main Qt loop
    sys.exit(app.exec_())
