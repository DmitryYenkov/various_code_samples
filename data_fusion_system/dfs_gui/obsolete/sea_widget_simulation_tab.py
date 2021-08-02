from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui

import os
from shutil import copyfile
import subprocess
import time


def close_matlab():
    poll_matlab = subprocess.Popen('tasklist | more', shell=True, stdout=subprocess.PIPE)
    for line in poll_matlab.stdout:
        line_text = str(line)
        if 'MATLAB' in line_text:
            pid = line_text.split()[1]
            subprocess.Popen('taskkill /F /PID ' + pid, shell=True, stdout=subprocess.PIPE)


def show_error(text):
    err = QtWidgets.QMessageBox()
    err.setIcon(QtWidgets.QMessageBox.Critical)
    err.setText(text)
    err.setWindowTitle('Error')
    err.exec_()


class SimulationTab(QtWidgets.QWidget):

    def __init__(self,
                 parent,
                 quat_lib_path,
                 xml_lib_path,
                 movement_model_path,
                 save_model_path,
                 imu_gps_filter_path):

        super().__init__(parent)

        self.info_label = QtWidgets.QLabel('', parent)
        self.config_path_text = QtWidgets.QLineEdit(parent)
        self.config_path = ''
        self.current_data_path_text = QtWidgets.QLineEdit(parent)
        self.filter_input_path = ''
        self.save_path_text = QtWidgets.QLineEdit(parent)
        self.matlab_exe_path_text = QtWidgets.QLineEdit(parent)

        self.quat_lib_path = quat_lib_path
        self.xml_lib_path = xml_lib_path
        self.movement_model_path = movement_model_path
        self.save_model_path = save_model_path
        self.imu_gps_filter_path = imu_gps_filter_path
        self.filter_param_file = None

        if os.path.isfile('matlab_exe_path.txt'):
            with open('matlab_exe_path.txt', 'r') as f:
                lines = f.readlines()
                self.matlab_exe_path = lines[0]
        else:
            self.matlab_exe_path = ''

        self.simulation_tab_layout(parent)

    def simulation_tab_layout(self, parent):

        layout = QtWidgets.QGridLayout(parent)
        layout.setSpacing(5)

        label_color = self.info_label.palette().color(QtGui.QPalette.Background)
        text_palette = self.info_label.palette()
        text_palette.setColor(self.info_label.backgroundRole(), label_color)
        bold_font = QtGui.QFont()
        bold_font.setBold(True)

        info_font = QtGui.QFont()
        info_font.setBold(True)
        info_font.setPointSize(10)
        self.info_label.setFont(info_font)

        config_path_label = QtWidgets.QLabel('Config File:', parent)
        config_path_label.setFont(bold_font)
        config_path_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.config_path_text.setText(self.config_path)
        self.config_path_text.setEnabled(False)

        matlab_paths_label = QtWidgets.QLabel('MATLAB Paths:', parent)
        matlab_paths_label.setFont(bold_font)
        matlab_paths_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

        self.matlab_exe_path_text.setText(self.matlab_exe_path)
        self.matlab_exe_path_text.setEnabled(False)
        matlab_exe_path_button = QtWidgets.QPushButton('Select EXE path', parent)
        matlab_exe_path_func = lambda: self.set_matlab_exe_path_lambda()
        matlab_exe_path_button.clicked.connect(matlab_exe_path_func)

        matlab_quat_path_label = QtWidgets.QLabel('Quaternion path:', parent)
        matlab_quat_path_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        matlab_quat_path_text = QtWidgets.QLineEdit(parent)
        matlab_quat_path_text.setText(self.quat_lib_path)
        matlab_quat_path_text.setEnabled(False)

        matlab_xml_path_label = QtWidgets.QLabel('XML lib path:', parent)
        matlab_xml_path_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        matlab_xml_path_text = QtWidgets.QLineEdit(parent)
        matlab_xml_path_text.setText(self.xml_lib_path)
        matlab_xml_path_text.setEnabled(False)

        matlab_model_path_label = QtWidgets.QLabel('Model path:', parent)
        matlab_model_path_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        matlab_model_path_text = QtWidgets.QLineEdit(parent)
        matlab_model_path_text.setText(self.movement_model_path)
        matlab_model_path_text.setEnabled(False)

        save_path_label = QtWidgets.QLabel('Save results path:', parent)
        save_path_label.setFont(bold_font)
        self.save_path_text.setText(self.save_model_path)
        self.save_path_text.setEnabled(False)

        save_path_button = QtWidgets.QPushButton('Set path', parent)
        save_path_func = lambda: self.set_save_path_lambda()
        save_path_button.clicked.connect(save_path_func)

        run_data_gen_button = QtWidgets.QPushButton('Run Data Generation', parent)
        run_data_gen_func = lambda: self.run_data_gen_lambda()
        run_data_gen_button.clicked.connect(run_data_gen_func)

        current_data_path_label = QtWidgets.QLabel('Current data path:', parent)
        current_data_path_label.setFont(bold_font)
        self.current_data_path_text.setText(self.filter_input_path)
        self.current_data_path_text.setEnabled(False)

        current_data_path_button = QtWidgets.QPushButton('Select', parent)
        current_data_path_func = lambda: self.set_current_data_path_lambda()
        current_data_path_button.clicked.connect(current_data_path_func)

        filter_path_label = QtWidgets.QLabel('Fusion Filter Model path:', parent)
        filter_path_label.setFont(bold_font)
        filter_path_text = QtWidgets.QLineEdit(parent)
        filter_path_text.setText(self.imu_gps_filter_path)
        filter_path_text.setEnabled(False)

        run_filter_button = QtWidgets.QPushButton('Run Fusion Filter', parent)
        run_filter_func = lambda: self.run_filter_lambda()
        run_filter_button.clicked.connect(run_filter_func)

        eval_button = QtWidgets.QPushButton('Plot results', parent)
        eval_func = lambda: self.eval_lambda()
        eval_button.clicked.connect(eval_func)

        user_button = QtWidgets.QPushButton('Plot user data', parent)
        user_func = lambda: self.user_lambda()
        user_button.clicked.connect(user_func)

        layout.addWidget(config_path_label, 0, 0, 1, 9)
        layout.addWidget(self.config_path_text, 1, 0, 1, 9)
        layout.addWidget(matlab_paths_label, 2, 0, 1, 9)
        layout.addWidget(matlab_exe_path_button, 3, 0, 1, 2)
        layout.addWidget(self.matlab_exe_path_text, 3, 2, 1, 7)
        layout.addWidget(matlab_quat_path_label, 4, 0, 1, 2)
        layout.addWidget(matlab_quat_path_text, 4, 2, 1, 7)
        layout.addWidget(matlab_xml_path_label, 5, 0, 1, 2)
        layout.addWidget(matlab_xml_path_text, 5, 2, 1, 7)
        layout.addWidget(matlab_model_path_label, 6, 0, 1, 2)
        layout.addWidget(matlab_model_path_text, 6, 2, 1, 7)
        layout.addWidget(save_path_label, 7, 0, 1, 9)
        layout.addWidget(self.save_path_text, 8, 0, 1, 7)
        layout.addWidget(save_path_button, 8, 7, 1, 2)
        layout.addWidget(current_data_path_label, 9, 0, 1, 9)
        layout.addWidget(self.current_data_path_text, 10, 0, 1, 7)
        layout.addWidget(current_data_path_button, 10, 7, 1, 2)
        layout.addWidget(filter_path_label, 11, 0, 1, 9)
        layout.addWidget(filter_path_text, 12, 0, 1, 9)

        layout.addWidget(run_data_gen_button, 13, 0, 2, 3)
        layout.addWidget(run_filter_button, 13, 3, 2, 3)
        layout.addWidget(eval_button, 13, 6, 1, 3)
        layout.addWidget(user_button, 14, 6, 1, 3)

        layout.addWidget(self.info_label, 15, 0, 1, 9)

        run_data_gen_button.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        run_filter_button.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        eval_button.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        user_button.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)

        parent.setLayout(layout)

    def run_data_gen_lambda(self):
        close_matlab()
        if not os.path.isfile(self.config_path):
            show_error('XML path not set or settings not saved!')
        else:
            self.info_label.setText('Generating data, please wait...')
            self.info_label.repaint()
            pathfile = os.path.join(self.movement_model_path, 'movement_set_paths.m')
            with open(pathfile, 'w') as f:
                f.write(''.join(['quat_path = \'', self.quat_lib_path, '\';\n']))
                f.write(''.join(['xml_func_path = \'', self.xml_lib_path, '\';\n']))
                f.write(''.join(['save_path = \'', self.save_model_path, '\';\n']))
                f.write(''.join(['xml_file = \'', self.config_path, '\';\n']))
            batfile = os.path.join(self.movement_model_path, 'run_model.bat')
            with open(batfile, 'w') as f:
                f.write('@echo off\n')
                f.write(''.join(['cd ', self.movement_model_path, '\n']))
                f.write(''.join(['"', self.matlab_exe_path, '"',
                                 ' -nosplash -nodesktop -minimize -r \"addpath(\'',
                                 self.movement_model_path,
                                 '\'); movement_main; exit;\"\n']))
            os.system(batfile)
            while True:
                time.sleep(1)
                poll_matlab = subprocess.Popen('tasklist | more', shell=True, stdout=subprocess.PIPE)
                for line in poll_matlab.stdout:
                    line_text = str(line)
                    if 'MATLAB' in line_text:
                        break
                else:
                    break
            all_subdirs = [d for d in os.listdir(self.save_model_path)
                           if os.path.isdir(os.path.join(self.save_model_path, d))]
            latest_subdir = max(all_subdirs,
                                key=lambda p: os.path.getmtime(os.path.join(self.save_model_path, p)))
            self.filter_input_path = os.path.join(self.save_model_path, latest_subdir)
            self.current_data_path_text.setText(self.filter_input_path)
            copyfile(self.config_path, os.path.join(self.filter_input_path, latest_subdir + '_scenario.xml'))
            self.info_label.setText('MATLAB data generation complete!')

    def set_matlab_exe_path_lambda(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        filename = QtWidgets.QFileDialog.getOpenFileName(self,
                                                         'Select File',
                                                         'exe (*.exe)',
                                                         options=options)
        if filename:
            self.matlab_exe_path = filename[0].replace('/', '\\')
            self.matlab_exe_path_text.setText(self.matlab_exe_path)
            with open('matlab_exe_path.txt', 'w') as f:
                f.write(self.matlab_exe_path)

    def set_save_path_lambda(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        dirname = QtWidgets.QFileDialog.getExistingDirectory(self,
                                                             'Select Folder',
                                                             self.save_model_path,
                                                             options=options)
        if dirname:
            dirname += '/' if dirname[-1] != '/' else ''
            self.save_model_path = dirname
            self.save_path_text.setText(self.save_model_path)

    def set_current_data_path_lambda(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        dirname = QtWidgets.QFileDialog.getExistingDirectory(self,
                                                             'Select Folder',
                                                             self.save_model_path,
                                                             options=options)
        if dirname:
            dirname += '/' if dirname[-1] != '/' else ''
            self.filter_input_path = dirname
            self.current_data_path_text.setText(self.filter_input_path)

    def run_filter_lambda(self):
        if not os.path.isdir(self.imu_gps_filter_path) or \
                not os.path.isdir(self.filter_input_path):
            show_error('Filter path or input data path not set!')
        else:
            self.info_label.setText('Processing data, please wait...')
            self.info_label.repaint()
            cmd = ['d:/ins_gps_project/python/python.exe',
                   os.path.join(self.imu_gps_filter_path, 'sensor_processing.py'),
                   '--input', self.filter_input_path]  # , '--silent']
            if self.filter_param_file is not None:
                cmd += ['--filter', self.filter_param_file]
                ckf = os.path.normpath(self.filter_input_path).lstrip(os.path.sep).split(os.path.sep)[-1] + '_ckf_params.txt'
                copyfile(self.filter_param_file, os.path.join(self.filter_input_path, ckf))
            out = subprocess.Popen(cmd)
            # out = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            while out.poll() is None:
                time.sleep(1)
            self.info_label.setText('Fusion Filter data processing complete!')

    def eval_lambda(self):
        close_matlab()
        if not os.path.isdir(self.imu_gps_filter_path) or \
                not os.path.isdir(self.filter_input_path):
            show_error('Filter path or input data path not set!')
            return
        files = os.listdir(self.filter_input_path)
        res = [f for f in files if 'results' in f]
        if not res:
            show_error('No process results data yet!')
            return

        batfile = os.path.join(self.movement_model_path, 'eval_results.bat')
        with open(batfile, 'w') as f:
            f.write('@echo off\n')
            f.write(''.join(['cd ', self.movement_model_path, '\n']))
            f.write(''.join(['"', self.matlab_exe_path, '"',
                             ' -nosplash -nodesktop -minimize -r \"addpath(\'',
                             self.movement_model_path,
                             '\'); display_results_func(\'',
                             self.filter_input_path,
                             '\', {\'x\', \'',
                             self.xml_lib_path,
                             '\'});\"\n']))
        os.system(batfile)

    def user_lambda(self):
        if not os.path.isdir(self.imu_gps_filter_path) or \
                not os.path.isdir(self.filter_input_path):
            show_error('Filter path or input data path not set!')
            return
        files = os.listdir(self.filter_input_path)
        res = [f for f in files if 'user_points' in f]
        if not res:
            show_error('No user points data!')
            return

        batfile = os.path.join(self.movement_model_path, 'show_user_points.bat')
        with open(batfile, 'w') as f:
            f.write('@echo off\n')
            f.write(''.join(['cd ', self.movement_model_path, '\n']))
            f.write(''.join(['"', self.matlab_exe_path, '"',
                             ' -nosplash -nodesktop -minimize -r \"addpath(\'',
                             self.movement_model_path,
                             '\'); display_user_points_func(\'',
                             self.filter_input_path,
                             '\');\"\n']))
        os.system(batfile)
        # os.remove(batfile)

    def settings_tab_out_signal2_response(self, msg):

        self.config_path = msg
        self.config_path_text.setText(self.config_path)

    def filter_tab_out_signal1_response(self, msg):

        self.filter_param_file = msg
