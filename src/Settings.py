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

import ConfigParser
import gettext
import locale
import os
import types

# initialise localisation settings
module_path = os.path.dirname(os.path.realpath(__file__))
gettext.bindtextdomain('PythonMcu', os.path.join(module_path, 'po/'))
gettext.textdomain('PythonMcu')
_ = gettext.lgettext

class Settings:
    """Store user and application settings in one place and make them available.
    """
    def __init__(self):
        """Initialise user settings and application information.

        Keyword arguments:
        None

        Return value:
        None

        """
        # common application copyrights and information (only set here, private)
        self.__application__ = 'PythonMcu.py'
        self.__cmd_line__ = 'PythonMcu'
        self.__version__ = '1.01'
        self.__years__ = '2011'
        self.__authors__ = 'Martin Zuther'
        self.__license_short__ = 'GPL version 3 (or later)'
        self.__license_long__ = """This program is free software: you can redistribute it and/or modify
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
        self.__description__ = _('Mackie Host Controller written in Python')

        # set INI file path
        if os.name == 'posix':
            self.__config_file_path__ = os.path.expanduser('~/.python_mcu')
        elif os.name == 'nt':
            # for the lack of a good place, look for the configuration
            # file in the application's directory
            self.__config_file_path__ = os.path.expanduser('~/python_mcu.conf')
        else:
            assert(False)

        # if INI file doesn't exist or cannot be read, ...
        #if not os.access(self.__config_file_path__, os.F_OK | os.R_OK):
            #raise IOError(_('File "%s" not found.') % self.__config_file_path__)

        # read application settings from INI file
        self.__settings__ = ConfigParser.RawConfigParser()
        self.__settings__.read(self.__config_file_path__)


    def __repr__(self):
        """Return all the contents of the INI file as string.

        Keyword arguments:
        None

        Return value:
        Formatted string containing all settings from the INI file

        """
        output = ''
        # sort and output sections
        for section in self.sections():
            output += '\n[%s]\n' % section
            # sort and output settings
            for item in self.items(section):
                output += '%s: %s\n' % (item[0], item[1])
        # dump the whole thing
        return output.lstrip('\n')


    def get(self, section, setting, allow_empty):
        """Get an application setting.

        Keyword arguments:
        section -- string that specifies the section to be queried
        setting -- string that specifies the setting to be queried
        allow_empty -- queried string may be empty or setting may be
                       non-existant

        Return value:
        String containing the specified application setting

        """
        try:
            value = self.__settings__.get(section, setting)
            if not value and not allow_empty:
                raise ValueError( \
                    "option '%(setting)s' in section '%(section)s' is empty" % \
                                     {'setting': setting, 'section': section})
            else:
                return value
        except ConfigParser.NoOptionError:
            if allow_empty:
                return ''
            else:
                raise ValueError( \
                    "option '%(setting)s' not found in section '%(section)s'" % \
                        {'setting': setting, 'section': section})


    def items(self, section):
        """Get all application setting names of a section

        Keyword arguments:
        section -- string that specifies the section to be queried

        Return value:
        List containing application setting names of the given section

        """
        items = self.__settings__.items(section)
        items.sort()
        return items


    def sections(self):
        """Get all sections.

        Keyword arguments:
        None

        Return value:
        List containing all section names

        """
        sections = self.__settings__.sections()
        sections.sort()

        # move section 'default' to the top so that the default backup
        # will be run first
        if 'default' in  sections:
            item = sections.pop(sections.index('default'))
            sections.insert(0, item)

        return sections


    def get_variable(self, variable):
        """Return application describing variable as string.

        Keyword arguments:
        variable -- variable to query

        Return value:
        Formatted string containing variable's value (or None for
        invalid queries)

        """
        # list of variable names that may be queried (as a security measure)
        valid_variable_names = ('application', 'cmd_line', 'version', \
                                    'years', 'authors', 'license_short', \
                                    'license_long', 'description')

        if variable in valid_variable_names:
            return eval('self.__%s__' % variable)
        else:
            return None


    def get_description(self, long):
        """Return application description as string.

        Keyword arguments:
        long -- Boolean indication whether to output long version of description

        Return value:
        Formatted string containing application description

        """
        description = '%(application)s v%(version)s' % \
            {'application':self.get_variable('application'), \
                 'version':self.get_variable('version')}
        description += '\n' + '=' * len(description)

        if long:
            description += '\n%(description)s' % \
                {'description':self.get_variable('description')}

        return description


    def get_copyrights(self):
        """Return application copyrights as string.

        Keyword arguments:
        None

        Return value:
        Formatted string containing application copyrights

        """
        return '(c) %(years)s %(authors)s' % \
            {'years':self.get_variable('years'),\
                 'authors':self.get_variable('authors')}


    def get_license(self, long):
        """Return application license as string.

        Keyword arguments:
        long -- Boolean indication whether to output long version of description

        Return value:
        Formatted string containing application license

        """
        if long:
            return self.get_variable('license_long')
        else:
            return self.get_variable('license_short')


# make everything available ("from Settings import *")
settings = Settings()
