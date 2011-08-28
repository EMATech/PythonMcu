#!/usr/bin/env python
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

from PythonMcu.Hardware import *
from PythonMcu.MackieControl.MackieHostControl import MackieHostControl
from PythonMcu.McuInterconnector.McuInterconnector import McuInterconnector
from PythonMcu.Midi.MidiConnection import MidiConnection
from PythonMcu.Tools.ApplicationConfiguration import *
from PythonMcu.Tools.AboutDialog import *

import platform
import sys

import pygame.version
import PySide
from PySide.QtCore import *
from PySide.QtGui import *


configuration = ApplicationConfiguration()


class PythonMcu(QFrame):
    def __init__(self, parent=None):
        super(PythonMcu, self).__init__(parent)

        font = QFont()
        font.setStyleHint(QFont.TypeWriter, QFont.PreferAntialias)

        char_format = QTextCharFormat()
        char_format.setFontFamily(font.defaultFamily())
        text_width = QFontMetrics(char_format.font()).width('*') * 80

        # must be defined before starting the logger!
        self._edit_logger = QPlainTextEdit()
        self._edit_logger.setReadOnly(True)
        self._edit_logger.setCurrentCharFormat(char_format)
        self._edit_logger.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self._edit_logger.setFixedWidth(text_width)

        # must be defined before reading the configuration file!
        self._edit_usage_hint = QPlainTextEdit()
        self._edit_usage_hint.setReadOnly(True)
        self._edit_usage_hint.setCurrentCharFormat(char_format)

        self.callback_log('')
        self.callback_log(configuration.get_full_description())
        self.callback_log('')
        self.callback_log('')
        self.callback_log('Version numbers')
        self.callback_log('===============')
        self.callback_log('Python:  %s (%s)' % ( \
                platform.python_version(), platform.python_implementation()))
        self.callback_log('PySide:  %s' % PySide.__version__)
        self.callback_log('pygame:  %s' % pygame.version.ver)
        self.callback_log('')
        self.callback_log('')

        # auto-scroll log window by setting cursor to end of document
        self._edit_logger.moveCursor(QTextCursor.End, QTextCursor.MoveAnchor)

        self._read_configuration()

        self._timer = None
        self._interconnector = None

        icon = self.style().standardIcon(QStyle.SP_TitleBarMenuButton)
        self.setWindowIcon(icon)

        mcu_model_ids = ['Logic Control', 'Logic Control XT', \
                              'Mackie Control', 'Mackie Control XT']

        hardware_controllers = [ \
            'Novation ZeRO SL MkII', \
            'Novation ZeRO SL MkII (MIDI)'
        ]

        # get version number of "Python MCU"
        version = configuration.get_application_information('version')
        self.setWindowTitle(configuration.get_version(True))

        # create layouts and add widgets
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.layout_2 = QVBoxLayout()
        self.layout.addLayout(self.layout_2)

        self.frame_mcu = QFrame()
        self.frame_mcu.setFrameStyle(QFrame.Box)
        self.frame_mcu.setFrameShadow(QFrame.Sunken)
        self.layout_2.addWidget(self.frame_mcu)
        self.grid_layout_mcu = QGridLayout()
        self.frame_mcu.setLayout(self.grid_layout_mcu)

        self.frame_controller = QFrame()
        self.frame_controller.setFrameStyle(QFrame.Box)
        self.frame_controller.setFrameShadow(QFrame.Sunken)
        self.layout_2.addWidget(self.frame_controller)
        self.grid_layout_controller = QGridLayout()
        self.frame_controller.setLayout(self.grid_layout_controller)


        self._combo_mcu_model_id = self._create_combo_box( \
            self.grid_layout_mcu, self._mcu_emulated_model, \
                'Emulation:', mcu_model_ids)

        connection_types = [MackieHostControl.ASSUME_SUCCESSFUL_CONNECTION, \
                                MackieHostControl.CHALLENGE_RESPONSE, \
                                MackieHostControl.WAIT_FOR_MIDI_DATA]
        self._combo_mcu_connection = self._create_combo_box( \
            self.grid_layout_mcu, self._mcu_connection, \
                'Connection:', connection_types)

        self._combo_mcu_midi_input = self._create_combo_box( \
            self.grid_layout_mcu, self._mcu_midi_input, \
                'MIDI In:', MidiConnection.get_midi_inputs())

        self._combo_mcu_midi_output = self._create_combo_box( \
            self.grid_layout_mcu, self._mcu_midi_output, \
                'MIDI Out:', MidiConnection.get_midi_outputs())


        self._combo_hardware_controller = self._create_combo_box( \
            self.grid_layout_controller, self._hardware_controller, \
                'Controller:', hardware_controllers)

        self._combo_controller_midi_input = self._create_combo_box( \
            self.grid_layout_controller, self._controller_midi_input, \
                'MIDI In:', MidiConnection.get_midi_inputs())

        self._combo_controller_midi_output = self._create_combo_box( \
            self.grid_layout_controller, self._controller_midi_output, \
                'MIDI Out:', MidiConnection.get_midi_outputs())

        self.grid_layout_controller.addWidget( \
            self._edit_usage_hint, self.grid_layout_controller.rowCount(), \
                0, 1, 2)

        self.layout.addWidget(self._edit_logger)

        self.bottom_layout = QHBoxLayout()
        self.layout_2.addLayout(self.bottom_layout)

        self.button_start_stop = QPushButton('&Start')
        self.bottom_layout.addWidget(self.button_start_stop)
        self.button_start_stop.setDefault(True)
        self.button_start_stop.setFocus()
        self.button_start_stop.clicked.connect(self.interconnector_start_stop)

        self.button_close = QPushButton('&Close')
        self.bottom_layout.addWidget(self.button_close)
        self.button_close.clicked.connect(self.close_application)

        self.button_about = QPushButton('A&bout')
        self.bottom_layout.addWidget(self.button_about)
        self.button_about.clicked.connect(self.display_about)

        self._enable_controls(True)

        self._timer = QTimer(self)
        self._timer.setInterval(int(self._midi_latency))
        self._timer.timeout.connect(self.process_midi_input)


    def _read_configuration(self):
        # initialise defaults for MCU and hardware controller
        mcu_emulated_model_default = MackieHostControl.get_preferred_mcu_model()
        hardware_controller_default = 'Novation ZeRO SL MkII'
        midi_latency_default = '1'

        # retrieve user configuration for MCU and hardware controller
        self._mcu_emulated_model = configuration.get_option( \
            'Python MCU', 'mcu_emulated_model', mcu_emulated_model_default)
        self._hardware_controller = configuration.get_option( \
            'Python MCU', 'controller_hardware', hardware_controller_default)
        self._midi_latency = configuration.get_option( \
            'Python MCU', 'midi_latency', midi_latency_default)

        # calculate MCU model ID from its name
        self._mcu_model_id = MackieHostControl.get_mcu_id_from_model( \
            self._mcu_emulated_model)

        # Logic Control units use MCU challenge-response by default, ...
        if self._mcu_model_id in [0x10, 0x11]:
            mcu_connection_default = MackieHostControl.CHALLENGE_RESPONSE
        # whereas Mackie Control Units don't seem to use it
        else:
            mcu_connection_default = MackieHostControl.WAIT_FOR_MIDI_DATA

        self._mcu_connection = configuration.get_option( \
            'Python MCU', 'mcu_connection', mcu_connection_default)

        # get preferred MIDI ports for hardware controller
        (controller_midi_input_default, controller_midi_output_default) = \
            self._initialise_hardware_controller()

        # initialise MIDI port defaults for MCU and hardware
        # controller
        mcu_midi_input_default = \
            MackieHostControl.get_preferred_midi_input()
        mcu_midi_output_default = \
            MackieHostControl.get_preferred_midi_output()

        # retrieve user configuration for MCU's MIDI ports
        self._mcu_midi_input = configuration.get_option( \
            'Python MCU', 'mcu_midi_input', \
                mcu_midi_input_default)
        self._mcu_midi_output = configuration.get_option( \
            'Python MCU', 'mcu_midi_output', \
                mcu_midi_output_default)

        # retrieve user configuration for hardware controller's MIDI
        # ports
        self._controller_midi_input = configuration.get_option( \
            'Python MCU', 'controller_midi_input', \
                controller_midi_input_default)
        self._controller_midi_output = configuration.get_option( \
            'Python MCU', 'controller_midi_output', \
                controller_midi_output_default)


    def _create_combo_box(self, layout, selection, label_text, choices):
        row = layout.rowCount()

        label = QLabel(None)
        label.setText(label_text)
        layout.addWidget(label, row, 0)

        widget = QComboBox()
        layout.addWidget(widget, row, 1)

        choices.sort()
        widget.addItems(choices)

        current_index = widget.findText(selection)
        widget.setCurrentIndex(current_index)
        widget.currentIndexChanged.connect(self.combobox_item_selected)

        return widget


    def _enable_controls(self, state):
        self.frame_mcu.setEnabled(state)
        self.frame_controller.setEnabled(state)


    def _initialise_hardware_controller(self):
        # the hardware controller's class name is simply the
        # controller's manufacturer and name with all spaces converted
        # to underscores and all brackets removed
        self._hardware_controller_class = \
            self._hardware_controller.replace(' ', '_')
        self._hardware_controller_class = \
            self._hardware_controller_class.replace('(', '').replace(')', '')
        self._hardware_controller_class = \
            self._hardware_controller_class.replace('[', '').replace(']', '')
        self._hardware_controller_class = \
            self._hardware_controller_class.replace('{', '').replace('}', '')

        # get hardware controller's preferred MIDI ports
        eval_controller_midi_input = \
            '{0!s}.{0!s}.get_preferred_midi_input()'.format( \
            self._hardware_controller_class)
        eval_controller_midi_output = \
            '{0!s}.{0!s}.get_preferred_midi_output()'.format( \
            self._hardware_controller_class)

        controller_midi_input_default = eval(eval_controller_midi_input)
        controller_midi_output_default = eval(eval_controller_midi_output)

        # show controller's usage hint
        usage_hint = '{0!s}.{0!s}.get_usage_hint()'.format( \
            self._hardware_controller_class)
        self._edit_usage_hint.setPlainText(eval(usage_hint))

        return (controller_midi_input_default, controller_midi_output_default)


    def callback_log(self, message, repaint=False):
        if repaint:
            self._edit_logger.repaint()

        print message
        self._edit_logger.appendPlainText(message)


    def combobox_item_selected(self, selected_text):
        widget = self.sender()

        if widget == self._combo_mcu_model_id:
            self._mcu_emulated_model = selected_text
            configuration.set_option( \
                'Python MCU', 'mcu_emulated_model', \
                    self._mcu_emulated_model)

            if self._mcu_emulated_model.startswith('Logic'):
                current_index = self._combo_mcu_connection.findText( \
                    MackieHostControl.CHALLENGE_RESPONSE)
                self._combo_mcu_connection.setCurrentIndex(current_index)
            else:
                current_index = self._combo_mcu_connection.findText( \
                    MackieHostControl.WAIT_FOR_MIDI_DATA)
                self._combo_mcu_connection.setCurrentIndex(current_index)

        elif widget == self._combo_mcu_midi_input:
            self._mcu_midi_input = selected_text
            configuration.set_option( \
                'Python MCU', 'mcu_midi_input', \
                    self._mcu_midi_input)
        elif widget == self._combo_mcu_midi_output:
            self._mcu_midi_output = selected_text
            configuration.set_option( \
                'Python MCU', 'mcu_midi_output', \
                    self._mcu_midi_output)
        elif widget == self._combo_hardware_controller:
            self._hardware_controller = selected_text
            configuration.set_option( \
            'Python MCU', 'controller_hardware', \
                self._hardware_controller)

            # get preferred MIDI ports for hardware controller
            (controller_midi_input_default, controller_midi_output_default) = \
                self._initialise_hardware_controller()

            # update hardware controller's MIDI ports in GUI
            current_index = self._combo_controller_midi_input.findText( \
                controller_midi_input_default)
            self._combo_controller_midi_input.setCurrentIndex(current_index)

            current_index = self._combo_controller_midi_output.findText( \
                controller_midi_output_default)
            self._combo_controller_midi_output.setCurrentIndex(current_index)
        elif widget == self._combo_controller_midi_input:
            self._controller_midi_input = selected_text
            configuration.set_option( \
                'Python MCU', 'controller_midi_input', \
                    self._controller_midi_input)
        elif widget == self._combo_controller_midi_output:
            self._controller_midi_output = selected_text
            configuration.set_option( \
                'Python MCU', 'controller_midi_output', \
                    self._controller_midi_output)
        elif widget == self._combo_mcu_connection:
            self._mcu_connection = selected_text
            configuration.set_option( \
                'Python MCU', 'mcu_connection', \
                    self._mcu_connection)
        else:
            self.callback_log('QComboBox not handled ("%s").' % selected_text)


    def process_midi_input(self):
        self._interconnector.process_midi_input()


    def display_about(self):
        AboutDialog(self).show()


    def interconnector_start_stop(self):
        if not self._interconnector:
            self._enable_controls(False)
            self.button_start_stop.setText('&Stop')

            self.callback_log('Settings')
            self.callback_log('========')
            self.callback_log('MCU emulation:  %s' % self._mcu_emulated_model)
            self.callback_log('Connection:     %s' % self._mcu_connection)
            self.callback_log('MIDI input:     %s' % self._mcu_midi_input)
            self.callback_log('MIDI output:    %s' % self._mcu_midi_output)
            self.callback_log('')
            self.callback_log('Controller:     %s' % self._hardware_controller)
            self.callback_log('MIDI input:     %s' % \
                                  self._controller_midi_input)
            self.callback_log('MIDI output:    %s' % \
                                  self._controller_midi_output)
            self.callback_log('')
            self.callback_log('MIDI latency:   %s ms' % self._midi_latency)
            self.callback_log('')
            self.callback_log('')

            if configuration.has_changed():
                self.callback_log('Saving configuration file ...')
                configuration.save_configuration()

            self.callback_log('Starting MCU emulation...')
            self.callback_log('', True)

            # the "interconnector" is the brain of this application -- it
            # interconnects Mackie Control Host and MIDI controller while
            # handling the complete MIDI translation between those two
            self._interconnector = McuInterconnector( \
                self._mcu_model_id, \
                    self._mcu_connection, \
                    self._mcu_midi_input, \
                    self._mcu_midi_output, \
                    self._hardware_controller_class, \
                    self._controller_midi_input, \
                    self._controller_midi_output, \
                    self.callback_log)
            self._interconnector.connect()

            self._timer.start()
        else:
            self._enable_controls(True)
            self.button_start_stop.setText('&Start')
            self._interconnector_stop()


    def _interconnector_stop(self):
            self._timer.stop()

            self.callback_log('')
            self.callback_log('Stopping MCU emulation...')
            self.callback_log('')

            self._interconnector.disconnect()
            self._interconnector = None

            self.callback_log('', True)


    def close_application(self):
        self.close()


    def closeEvent(self, event):
        if self._interconnector:
            self._interconnector_stop()

        self.callback_log('Exiting application...')
        self.callback_log('', True)


if __name__ == '__main__':
    # Create the Qt Application
    app = QApplication(sys.argv)

    # Create and show the form
    python_mcu = PythonMcu()
    python_mcu.show()

    # Run the main Qt loop
    sys.exit(app.exec_())
