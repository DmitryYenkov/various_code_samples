import os
import sys
import json
import subprocess

from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import uic

import xml.etree.ElementTree as Xml_ET
import xmltodict

from dfs_gui_scenario import ScenarioGui
import utils


class GeneratorGui(QtWidgets.QWidget):

    def __init__(self, x, y, w, h):

        super().__init__()

        if os.path.isfile(utils.cfg_filename):
            with open(utils.cfg_filename, 'r') as cfg:
                self.paths = json.load(cfg)
        else:
            self.paths = dict()

        if self.paths.get('matlab', None) is None:
            self.matlab_exe_path = os.popen('where matlab.exe').read().strip()  # .replace('\\', '/')
            self.paths['matlab'] = self.matlab_exe_path
        else:
            self.matlab_exe_path = self.paths['matlab']

        uic.loadUi(utils.join('ui', 'Generation.ui'), self)

        self.generate_button.clicked.connect(self.generate)
        self.scenario_open_button.clicked.connect(self.open_scenario)
        self.data_folder_select_button.clicked.connect(self.open_results_path)
        self.edit_scenario_button.clicked.connect(self.edit_scenario)

        self.movement_model_path = utils.join(utils.root_folder, 'ins_gps_project',
                                              'sources', 'movement_model')
        file = self.paths.get('generation_scenario', '')
        if os.path.isfile(file):
            self.scenario_file = file
            self.set_sensors_total()
        else:
            self.scenario_file = ''
        folder = self.paths.get('generation_results', '')
        self.results_path = folder if os.path.isdir(folder) else ''

        self.log_file = utils.join(self.movement_model_path, 'generator_log.txt')
        self.bat_file = utils.join(self.movement_model_path, 'run_model.cmd')
        with open(self.bat_file, 'w') as f:
            f.write('@echo off\n')
            f.write(''.join(['cd ', self.movement_model_path, '\n']))
            f.write(''.join(['"', self.matlab_exe_path, '"',
                             ' -nosplash -nodesktop -minimize -r \"addpath(\'',
                             self.movement_model_path,
                             '\'); movement_main; exit;\"\n']))

        self.scenario_path_line.setText(self.scenario_file)
        self.data_folder_line.setText(self.results_path)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.display_process)
        self.scenario_dialog = None

        self.status_line.setText('Idle')

        self.setFixedSize(w, self.geometry().height())
        self.move(x, y + h + 40)
        self.show()

    def generate(self):

        if not os.path.isfile(self.scenario_file):
            utils.show_error('Scenario File not selected!')

        utils.save_cfg(self.paths)

        utils.close_matlab()
        file = utils.join(self.movement_model_path, 'movement_set_paths.m')
        with open(file, 'w') as f:
            f.write(''.join(['save_path = \'', self.results_path, '\';\n']))
            f.write(''.join(['xml_file = \'', self.scenario_file, '\';\n']))

        open(self.log_file, 'w').close()
        if not self.timer.isActive():
            self.status_line.setText('Starting...')
            self.timer.start(1000)
            os.system(self.bat_file)
            self.generate_button.setText('STOP')
        else:
            self.generate_button.setText('GENERATE')

    def display_process(self):
        f = open(self.log_file, 'r')
        lines = f.readlines()
        f.close()
        if len(lines) > 0:
            last_line = lines[-1].strip()
            if last_line.isdigit():
                self.generation_progress_bar.setValue(int(last_line))
            else:
                self.status_line.setText(last_line)

        poll_matlab = subprocess.Popen('tasklist | more', shell=True, stdout=subprocess.PIPE)
        for line in poll_matlab.stdout:
            line_text = str(line)
            if 'MATLAB' in line_text:
                break
        else:
            self.timer.stop()
            self.status_line.setText('Idle')
            self.generate_button.setText('GENERATE')
            self.generation_progress_bar.setValue(0)

    def open_scenario(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        open_path = self.paths.get('generation_scenario', '')
        if not os.path.isdir(open_path):
            open_path = ''
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self,
                                                            'Open XML file',
                                                            open_path,
                                                            'xml (*.xml)',
                                                            options=options)
        if filename:
            self.set_scenario(filename)

    def set_scenario(self, filename):
        self.paths['generation_scenario'] = filename
        self.scenario_file = filename
        self.scenario_path_line.setText(filename)
        self.set_sensors_total()

    def open_results_path(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        open_path = self.paths.get('generation_results', '')
        if not os.path.isdir(open_path):
            open_path = ''
        dirname = QtWidgets.QFileDialog.getExistingDirectory(self,
                                                             'Select Folder',
                                                             os.path.split(open_path)[0],
                                                             options=options)
        if dirname:
            self.results_path = dirname
            self.paths['generation_results'] = self.results_path
            self.data_folder_line.setText(self.results_path)

    def edit_scenario(self):
        self.scenario_dialog = ScenarioGui(self.geometry().x(), self.geometry().y(),
                                           self.scenario_file)

        self.scenario_dialog.out_signals.out_new_scenario.connect(self.set_scenario)

    def set_sensors_total(self):
        if os.path.isfile(self.scenario_file):
            xml_data = Xml_ET.parse(self.scenario_file).getroot()
        else:
            utils.show_error('XML File Error!')
            return
        xml_str = Xml_ET.tostring(xml_data, encoding='utf-8', method='xml')
        settings = dict(xmltodict.parse(xml_str))
        num = len(settings['params']['sensors'])
        self.sensors_total_line.setText(str(num))

    def closeEvent(self, event):

        utils.save_cfg(self.paths)
        if self.scenario_dialog is not None and self.scenario_dialog.isVisible():
            self.scenario_dialog.close()
