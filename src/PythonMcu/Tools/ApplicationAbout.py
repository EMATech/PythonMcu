# -*- coding: utf-8 -*-

"""
PythonMcu
=========
Mackie Host Controller written in Python

Copyright (c) 2011 Martin Zuther (http://www.mzuther.de/)

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

import gettext
import locale
import os


# initialise localisation settings
module_path = os.path.dirname(os.path.realpath(__file__))
gettext.bindtextdomain('PythonMcu', os.path.join(module_path, 'po/'))
gettext.textdomain('PythonMcu')
_ = gettext.lgettext

class ApplicationAbout:
    """Store application information in one place and make it available.
    """

    # this may be queried from other classes to ascertain compatibility
    _INCARNATION = 2

    def __init__(self):
        """Initialise application information.

        Keyword arguments:
        None

        Return value:
        None

        """
        self._about = { \
            'about_class_incarnation':  self._INCARNATION,
            'application':              'PythonMcu',
            'cmd_line':                 'PythonMcu.py',
            'description':              _('Mackie Host Controller written in Python'),
            'version':                  '1.05',
            'authors':                  'Martin Zuther',
            'copyright_years':          '2011',
            'license_short':            _('GPL version 3 (or later)'),
            'license_long': \
"""This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

Thank you for using free software!"""
        }

        # set path to configuration file
        if os.name == 'nt':
            self._about['config_file_path'] = \
                os.path.expanduser('~/_python_mcu')
        else:
            self._about['config_file_path'] = \
                os.path.expanduser('~/.python_mcu')


    def __repr__(self):
        """Return all application information as string.

        Keyword arguments:
        None

        Return value:
        Formatted string containing all application information

        """
        output = '\nAbout the application\n=====================\n'

        keys = self._about.keys()
        keys.sort()

        for setting in keys:
            output += '[%s]\n%s\n\n' % (setting, self._about[setting])
        output = output.strip('\n')

        # dump the whole thing
        return output


    def get(self, information):
        """Return requested application information as string.

        Keyword arguments:
        information -- application information to query

        Return value:
        Formatted string containing application information (or None
        for invalid queries)

        """
        if information in self._about:
            return self._about[information]
        else:
            return None


    def get_copyrights(self):
        """Return application copyrights as string.

        Keyword arguments:
        None

        Return value:
        Formatted string containing application copyrights

        """
        return '(c) %(copyright_years)s %(authors)s' % \
            {'copyright_years': self.get('copyright_years'),\
                 'authors': self.get('authors')}


    def get_license(self, long):
        """Return application license as string.

        Keyword arguments:
        long -- Boolean indication whether to output long version of
                license

        Return value:
        Formatted string containing application license

        """
        if long:
            return self.get('license_long')
        else:
            return self.get('license_short')


    def get_description(self, long):
        """Return application description as string.

        Keyword arguments:
        long -- Boolean indication whether to output long version of
                description

        Return value:
        Formatted string containing application description

        """
        description = '%(application)s v%(version)s' % \
            {'application': self.get('application'), \
                 'version': self.get('version')}
        description += '\n' + '=' * len(description)

        if long:
            description += '\n%(description)s' % \
                {'description': self.get('description')}

        return description


    def get_full_description(self):
        """Return full application description as string.

        Return value:
        Formatted string containing full application description

        """
        output = self.get_description(True) + '\n'
        output += self.get_copyrights() + '\n\n'
        output += self.get_license(True)

        return output


if __name__ == "__main__":
    about = ApplicationAbout()
    output = about.get_full_description() + '\n\n\n' + str(about)

    print
    for line in output.split('\n'):
        print '  ' + line

    # wait for key press
    print
    print
    print '  Press any key ...',
    raw_input()
