import os
import json
import subprocess

from PyQt5 import QtWidgets
from PyQt5 import uic

import utils


class EvaluatorGui(QtWidgets.QWidget):

    def __init__(self, x, y, h):

        super().__init__()

        if os.path.isfile(utils.cfg_filename):
            with open(utils.cfg_filename, 'r') as cfg:
                self.paths = json.load(cfg)
        else:
            self.paths = dict()

        uic.loadUi(utils.join('ui', 'Evaluation.ui'), self)

        folder = self.paths.get('evaluation_data', '')
        self.data_path = folder if os.path.isdir(folder) else ''
        self.data_folder_line.setText(self.data_path)
        folder = self.paths.get('evaluation_results', '')
        self.result_path = folder if os.path.isdir(folder) else ''
        self.result_folder_line.setText(self.result_path)

        self.data_folder_select_button.clicked.connect(self.open_data_path)
        self.result_folder_select_button.clicked.connect(self.open_result_path)
        self.evaluate_button.clicked.connect(self.evaluate)
        self.show_button.clicked.connect(self.show_points)

        self.eval_bat_file = utils.join(utils.root_folder, 'ins_gps_project',
                                        'sources', 'movement_model', 'eval_results.cmd')
        self.show_bat_file = utils.join(utils.root_folder, 'ins_gps_project',
                                        'sources', 'movement_model', 'show_user.cmd')

        self.setFixedSize(self.geometry().width(), self.geometry().height())
        self.move(x, y + h + 2)
        self.show()

        self.pid = None

    def evaluate(self):

        out_string = ''
        if self.position_checkbox.isChecked():
            out_string += 'position,'
        if self.velocity_checkbox.isChecked():
            out_string += 'velocity,'
        if self.course_checkbox.isChecked():
            out_string += 'course,'
        if self.pitch_checkbox.isChecked():
            out_string += 'pitch,'
        if self.roll_checkbox.isChecked():
            out_string += 'roll,'
        if self.sat_num_checkbox.isChecked():
            out_string += 'sat_num,'
        if self.sat_mean_checkbox.isChecked():
            out_string += 'sat_mean,'
        if self.sphere_checkbox.isChecked():
            out_string += 'sphere,'
        if self.pos_ratio_checkbox.isChecked():
            out_string += 'pos_ratio,'
        if self.vel_ratio_checkbox.isChecked():
            out_string += 'vel_ratio,'
        if self.course_ratio_checkbox.isChecked():
            out_string += 'course_ratio,'

        utils.save_cfg(self.paths)

        if self.pid is None:
            with open(self.eval_bat_file, 'w') as f:
                f.write('@echo off\n')
                f.write(''.join(['cd ', os.path.split(self.eval_bat_file)[0], '\n']))
                f.write(''.join(['"', self.paths['matlab'], '"',
                                 ' -nosplash -nodesktop -minimize -r \"addpath(\'',
                                 os.path.split(self.eval_bat_file)[0],
                                 '\'); display_results_func(\'',
                                 self.data_path,
                                 '\', \'',
                                 self.result_path,
                                 '\', {\'sel\', \'',
                                 out_string,
                                 '\'});\"\n']))

            self.pid = subprocess.Popen([self.eval_bat_file])
            self.evaluate_button.setText('CLOSE')
        else:
            utils.close_matlab()
            self.evaluate_button.setText('EVALUATE')
            self.pid = None

    def show_points(self):

        utils.save_cfg(self.paths)

        if self.pid is None:
            with open(self.show_bat_file, 'w') as f:
                f.write('@echo off\n')
                f.write(''.join(['cd ', os.path.split(self.show_bat_file)[0], '\n']))
                f.write(''.join(['"', self.paths['matlab'], '"',
                                 ' -nosplash -nodesktop -minimize -r \"addpath(\'',
                                 os.path.split(self.show_bat_file)[0],
                                 '\'); display_user_points_func(\'',
                                 self.result_path,
                                 '\');\"\n']))

            self.pid = subprocess.Popen([self.show_bat_file])
            self.show_button.setText('CLOSE')
        else:
            utils.close_matlab()
            self.show_button.setText('SHOW POINTS')
            self.pid = None

    def open_data_path(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        open_path = self.paths.get('evaluation_data', '')
        if not os.path.isdir(open_path):
            open_path = ''
        dirname = QtWidgets.QFileDialog.getExistingDirectory(self,
                                                             'Select Folder',
                                                             os.path.split(open_path)[0],
                                                             options=options)
        if dirname:
            self.paths['evaluation_data'] = dirname
            self.data_folder_line.setText(self.paths['evaluation_data'])
            self.data_path = self.paths['evaluation_data']

    def open_result_path(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        open_path = self.paths.get('evaluation_results', '')
        if not os.path.isdir(open_path):
            open_path = ''
        dirname = QtWidgets.QFileDialog.getExistingDirectory(self,
                                                             'Select Folder',
                                                             os.path.split(open_path)[0],
                                                             options=options)
        if dirname:
            self.paths['evaluation_results'] = dirname
            self.result_folder_line.setText(self.paths['evaluation_results'])
            self.result_path = self.paths['evaluation_results']

    def closeEvent(self, event):

        utils.save_cfg(self.paths)
