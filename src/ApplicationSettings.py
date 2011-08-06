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
import types

import ApplicationAbout


class SortedDict(dict):
    def keys(self):
        keys = dict.keys(self)
        keys.sort()
        return keys

    def items(self):
        items = dict.items(self)
        items.sort()
        return items


class ApplicationSettings:
    """Store user and application settings in one place and make them available.

       Incarnation #6.
    """
    def __init__(self):
        """Initialise user settings and application information.

        Keyword arguments:
        None

        Return value:
        None

        """
        self._about = ApplicationAbout.ApplicationAbout()
        assert self.get_application_information('about_incarnation') == 2

        self._configuration = ConfigParser.RawConfigParser( \
            dict_type = SortedDict)
        self._configuration_changed = False
        self.load_configuration()


    def __repr__(self):
        """Return all the contents of the configuration file as string.

        Keyword arguments:
        None

        Return value:
        Formatted string containing all options from the configuration file

        """
        output = str(self._about)

        output += '\n\n\nConfiguration file\n=================='
        # sort and output sections
        for section in self.get_sections():
            output += '\n[%s]\n' % section
            # sort and output options
            for item in self.get_items(section):
                output += '%s: %s\n' % (item[0], item[1])

        # dump the whole thing
        return output.strip('\n')


    def load_configuration(self, force=False):
        """Load configuration file to memory.

        Keyword arguments:
        force -- Boolean stating whether a changed configuration
                 should be overwritten

        Return value:
        Boolean value that is "True" if configuration was loaded and
        "False" if configuration has changed and needs saving first

        """
        # configuration has changed and needs saving first
        if self.has_changed() and not force:
            return False
        # read application settings from configuration file
        else:
            self._configuration_changed = False
            self._configuration.read(self._about.get('config_file_path'))
            return True


    def save_configuration(self):
        """Save configuration file.

        Keyword arguments:
        None

        Return value:
        None

        """
        # configuration needs saving
        if self.has_changed():
            f = open(self._about.get('config_file_path'), 'w+')
            self._configuration.write(f)
            f.close()

            self._configuration_changed = False


    def has_changed(self):
        """Query whether configuration has changed.

        Keyword arguments:
        None

        Return value:
        None

        """
        # configuration needs saving
        return self._configuration_changed


    def add_section(self, section):
        """Add a section.

        Keyword arguments:
        section -- string that specifies the section to be created

        Return value:
        None

        """
        if not self._configuration.has_section(section):
            # we don't need to save empty sections, so do not change
            # "self._configuration_changed" here
            self._configuration.add_section(section)


    def remove_section(self, section):
        """Remove a section.

        Keyword arguments:
        section -- string that specifies the section to be removed

        Return value:
        None

        """
        if self._configuration.has_section(section):
            self._configuration_changed = True
            self._configuration.remove_section(section)


    def get_sections(self):
        """Get all sections.

        Keyword arguments:
        None

        Return value:
        List containing all section names

        """
        sections = self._configuration.sections()
        sections.sort()

        # move section 'default' to the top
        if 'default' in sections:
            item = sections.pop(sections.index('default'))
            sections.insert(0, item)

        return sections


    def get_option(self, section, option, default = None):
        """Get an application option.

        Keyword arguments:
        section -- string that specifies the section to be queried
        option -- string that specifies the option to be queried
        default -- this variable is used when the queried string does
                   not exist (or is an empty string)

        Return value:
        String containing the specified application option (or the
        default value)

        """
        try:
            value = self._configuration.get(section, option)
            if value:
                return value
            else:
                return default
        except ConfigParser.NoSectionError:
            return default
        except ConfigParser.NoOptionError:
            return default


    def set_option(self, section, option, value):
        """Set an application option (and adds it if necessary).

        Keyword arguments:
        section -- string that specifies the section to be changed; if
                   the section does not exist, it will be created
        option -- string that specifies the option to be queried
        value -- string that specifies the value to be set

        Return value:
        None

        """

        if not self._configuration.has_option(section, option):
            self.add_section(section)

            self._configuration_changed = True
            self._configuration.set(section, option, value)


    def remove_option(self, section, option):
        """Remove a section.

        Keyword arguments:
        section -- string that specifies the section to be removed
        option -- string that specifies the option to be queried

        Return value:
        None

        """
        if self._configuration.has_option(section, option):
            self._configuration_changed = True
            self._configuration.remove_option(section, option)


    def get_options(self, section):
        """Get all application option names of a section

        Keyword arguments:
        section -- string that specifies the section to be queried

        Return value:
        list containing application option names of the given section
        (or None is the section doesn't exist)

        """
        if not self._configuration.has_section(section):
            return None

        options = self._configuration.options(section)
        options.sort()
        return options


    def get_items(self, section):
        """Get all application options of a section

        Keyword arguments:
        section -- string that specifies the section to be queried

        Return value:
        list containing application option names of the given section
        (or None is the section doesn't exist)

        """
        if section not in self.get_sections():
            return None

        items = self._configuration.items(section)
        items.sort()
        return items


    def get_application_information(self, information):
        """Return requested application information as string.

        Keyword arguments:
        information -- application information to query

        Return value:
        Formatted string containing application information (or None
        for invalid queries)

        """
        return self._about.get(information)


    def get_copyrights(self):
        """Return application copyrights as string.

        Keyword arguments:
        None

        Return value:
        Formatted string containing application copyrights

        """
        return self._about.get_copyrights()


    def get_license(self, long):
        """Return application license as string.

        Keyword arguments:
        long -- Boolean indication whether to output long version of description

        Return value:
        Formatted string containing application license

        """
        return self._about.get_license(long)


    def get_description(self, long):
        """Return application description as string.

        Keyword arguments:
        long -- Boolean indication whether to output long version of description

        Return value:
        Formatted string containing application description

        """
        return self._about.get_description(long)


    def get_full_description(self):
        """Return full application description as string.

        Return value:
        Formatted string containing full application description

        """
        return self._about.get_full_description()


# make everything available ("from Settings import *")
settings = ApplicationSettings()

if __name__ == "__main__":
    output = settings.get_full_description() + '\n\n\n' + str(settings) + '\n'

    print
    for line in output.split('\n'):
        print '  ' + line


    print
    print settings.get_option('Python MCU', 'test')
    print settings.get_option('Python MCU', 'test', 'default')
    settings.set_option('Python MCU', 'test', 'done')
    settings.set_option('Python MCU', 'test2', 'done2')
    print settings.get_option('Python MCU', 'test', 'default')

    print settings.get_items('Python MCU')
    print settings.get_options('Python MCU')
    print settings.get_sections()

    print
    print settings.load_configuration()
    print settings.save_configuration()
    print settings.load_configuration()

    # wait for key press
    #raw_input()
