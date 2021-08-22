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

import configparser
import os

from PythonMcu.Tools import ApplicationAbout


class SortedDict(dict):
    """Subclass of "dict" which automatically sorts keys.

    """
    def keys(self):
        """Return a sorted copy of the dictionary’s list of keys

        Keyword arguments:
        None

        Return value:
        List containing a sorted copy of the dictionary’s list of keys

        """
        keys = list(dict.keys(self))
        keys.sort()
        return keys

    def items(self):
        """Return a sorted copy of the dictionary’s (key, value) pairs.

        Keyword arguments:
        None

        Return value:
        List containing a sorted copy of the dictionary’s (key, value)
        pairs

        """
        items = list(dict.items(self))
        items.sort()
        return items


class ApplicationConfiguration:
    """Store user settings and application information in one place
       and make them available.

       Incarnation #7.
    """
    def __init__(self):
        """Initialise user configuration and application information.

        Keyword arguments:
        None

        Return value:
        None

        """
        # initialise application information
        self._about = ApplicationAbout.ApplicationAbout()

        # ascertain compatibility with the class "ApplicationAbout"
        assert self.get_application_information('about_class_incarnation') == 3

        # this variable is used to check whether the user
        # configuration has changed and is in need of saving
        self._configuration_changed = False

        # initialise and load user configuration
        self._configuration = configparser.RawConfigParser(dict_type=SortedDict)
        self.load_configuration()

    def __repr__(self):
        """Return application information and user configuration file
        as string.

        Keyword arguments:
        None

        Return value:
        Formatted string containing all options from the configuration file

        """
        # get application information ...
        output = str(self._about)

        # ... and append user configuration
        output += '\n\n\nConfiguration file\n=================='
        # append sorted sections
        for section in self.get_sections():
            output += '\n[%s]\n' % section
            # append sorted options
            for item in self.get_items(section):
                output += '%s: %s\n' % (item[0], item[1])

        # dump the whole thing
        return output.strip('\n')

    def load_configuration(self, force=False):
        """Load user configuration file into memory.

        Keyword arguments:
        force -- Boolean stating whether a changed configuration
                 should be overwritten

        Return value:
        Boolean value that is "True" if configuration was loaded and
        "False" if configuration has changed and needs saving first

        """
        # configuration has changed and needs saving first
        if self.has_changed() and not force:
            # signal failure
            return False

        # read application settings from configuration file
        # retrieve location of configuration file
        file_name = self.get_application_information('config_file_path')

        # if configuration file exists, load it
        if os.path.isfile(file_name):
            self._configuration.read(file_name)

            # configuration has just been loaded, so mark as clean
            self._configuration_changed = False
        else:
            # configuration file does not exist, so mark
            # configuration as dirty
            self._configuration_changed = True

        # signal success
        return True

    def save_configuration(self):
        """Save user configuration to file.

        Keyword arguments:
        None

        Return value:
        None

        """
        # cycle sections ...
        for section in self.get_sections():
            # ... and remove empty sections
            if not self.get_options(section):
                self.remove_section(section)

        # if configuration is dirty ...
        if self.has_changed():
            # ... open, truncate and save configuration file
            with open(self.get_application_information('config_file_path'), 'w+') as file:
                self._configuration.write(file)

            # configuration has just been saved, so mark as clean
            self._configuration_changed = False

    def has_changed(self):
        """Query whether user configuration has changed.

        Keyword arguments:
        None

        Return value:
        Boolean value stating whether the user configuration has
        changed

        """
        return self._configuration_changed

    def add_section(self, section):
        """Add a section.

        Keyword arguments:
        section -- string that specifies the section to be created

        Return value:
        None

        """
        # add section if it does not already exist
        if not self._configuration.has_section(section):
            # there's no need to save an empty section, so do NOT mark
            # configuration as dirty here
            self._configuration.add_section(section)

    def remove_section(self, section):
        """Remove a section.

        Keyword arguments:
        section -- string that specifies the section to be removed

        Return value:
        None

        """
        # remove section if it does exist
        if self._configuration.has_section(section):
            self._configuration.remove_section(section)

            # mark configuration as dirty
            self._configuration_changed = True

    def get_sections(self):
        """Get all sections.

        Keyword arguments:
        None

        Return value:
        List containing all section names

        """
        # retrieve and sort sections
        sections = self._configuration.sections()
        sections.sort()

        # if section 'default' exists, move it to the top
        if 'default' in sections:
            item = sections.pop(sections.index('default'))
            sections.insert(0, item)

        # finally, return sections
        return sections

    def get_option(self, section, option, default=None):
        """Get an configuration option.

        Keyword arguments:
        section -- string that specifies the section to be queried
        option -- string that specifies the option to be queried
        default -- this variable is used when the queried string does
                   not exist (or is an empty string)

        Return value:
        String containing the specified configuration option (or the
        default value)

        """
        # if section or option does not exist, store and return
        # default value
        if not self._configuration.has_option(section, option):
            self.set_option(section, option, default)
            return default

        # otherwise retrieve current value
        current_value = self._configuration.get(section, option)

        # if current value is an empty string, store and return
        # default value
        if not current_value:
            self.set_option(section, option, default)
            return default

        # otherwise return current value
        return current_value

    def set_option(self, section, option, current_value):
        """Set (and possibly create) a configuration option.

        Keyword arguments:
        section -- string that specifies the section to be changed; if
                   the section does not exist, it will be created
        option -- string that specifies the option to be changed
        current_value -- string that specifies the value to be set

        Return value:
        None

        """
        # if section or option does not exist, add the section
        if not self._configuration.has_option(section, option):
            self.add_section(section)

        # set configuration option
        self._configuration.set(section, option, current_value)

        # mark configuration as dirty
        self._configuration_changed = True

    def remove_option(self, section, option):
        """Remove a configuration option.

        Keyword arguments:
        section -- string that specifies the section to be removed
        option -- string that specifies the option to be removed

        Return value:
        None

        """
        # if section and option do exist, remove the option
        if self._configuration.has_option(section, option):
            self._configuration.remove_option(section, option)

            # mark configuration as dirty
            self._configuration_changed = True

    def get_options(self, section):
        """Get all option names of a section

        Keyword arguments:
        section -- string that specifies the section to be queried

        Return value:
        List containing all option names of the given section (or
        "None" in case the section doesn't exist)

        """
        # if the section doesn't exist, return "None"
        if not self._configuration.has_section(section):
            return None

        # retrieve, sort and return option names
        options = self._configuration.options(section)
        options.sort()
        return options

    def get_items(self, section):
        """Get all configuration items of a section

        Keyword arguments:
        section -- string that specifies the section to be queried

        Return value:
        List containing all items of the given section (or "None" in
        case the section doesn't exist)

        """
        # if the section doesn't exist, return "None"
        if section not in self.get_sections():
            return None

        # retrieve, sort and return option items
        items = self._configuration.items(section)
        items.sort()
        return items

    def get_application_information(self, information):
        """Return requested application information as string.

        Keyword arguments:
        information -- application information to query

        Return value:
        Formatted string containing application information (or "None"
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

    def get_license(self, selection):
        """Return application license or its terms as string.

        Keyword arguments:

        selection -- String indicating what should be returned:
                     'selected':  name of license and selected options
                     'name':      name of license
                     'short':     shortened license terms as plain text
                     'plain':     license terms as plain text
                     'html':      license terms in HTML format

        Return value:
        Formatted string containing application license or its terms

        """
        return self._about.get_license(selection)

    def get_version(self, long):
        """Return application version as string.

        Keyword arguments:
        long -- Boolean indication whether to output long version of
                version

        Return value:
        Formatted string containing application description

        """
        return self._about.get_version(long)

    def get_description(self, long):
        """Return application description as string.

        Keyword arguments:
        long -- Boolean indication whether to output long version of
                description

        Return value:
        Formatted string containing application description

        """
        return self._about.get_description(long)

    def get_full_description(self, text_format='plain'):
        """Return full application description as string.

        text_format -- String indicating format:
                  'plain':  plain text
                  'html':   HTML format

        Return value:
        Formatted string containing full application description

        """
        return self._about.get_full_description(text_format)


if __name__ == "__main__":
    configuration = ApplicationConfiguration()

    contents = configuration.get_full_description() + '\n\n\n' + str(configuration) + '\n'

    print()
    for line in contents.split('\n'):
        print('  ' + line)

    # wait for key press
    print()
    print('  Press any key ...',)
    input()
