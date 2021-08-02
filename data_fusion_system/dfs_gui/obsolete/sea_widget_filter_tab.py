from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui


class FilterTabOutSignals(QtCore.QObject):

    out_signal1 = QtCore.pyqtSignal(str)


class FilterTab(QtWidgets.QWidget):

    def __init__(self,
                 parent,
                 flt_param_path):

        super().__init__(parent)

        self.info_label = QtWidgets.QLabel('', parent)
        self.flt_param_file_text = QtWidgets.QLineEdit(parent)

        self.flt_param_path = flt_param_path
        self.flt_param_file = ''

        self.sigma_xy = '[10, 10, 10]'
        self.sigma_v = '[0.1, 0.1, 0.1]'
        self.sigma_a = '[0.01, 0.01, 0.01]'
        self.sigma_w = '[1, 1, 1]'
        self.acc_bias = '[1, 1, 1]'
        self.gyr_bias = '[1, 1, 1]'

        self.sigma_xy_text = QtWidgets.QLineEdit(parent)
        self.sigma_v_text = QtWidgets.QLineEdit(parent)
        self.sigma_a_text = QtWidgets.QLineEdit(parent)
        self.sigma_w_text = QtWidgets.QLineEdit(parent)
        self.acc_bias_text = QtWidgets.QLineEdit(parent)
        self.gyr_bias_text = QtWidgets.QLineEdit(parent)

        self.out_signals = FilterTabOutSignals()
        self.filter_tab_layout(parent)

    def filter_tab_layout(self, parent):

        layout = QtWidgets.QGridLayout(parent)
        layout.setSpacing(5)

        label_color = self.info_label.palette().color(QtGui.QPalette.Background)
        text_palette = self.info_label.palette()
        text_palette.setColor(self.info_label.backgroundRole(), label_color)
        bold_font = QtGui.QFont()
        bold_font.setBold(True)

        flt_param_file_label = QtWidgets.QLabel('Config File:', parent)
        flt_param_file_label.setFont(bold_font)
        flt_param_file_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.flt_param_file_text.setText(self.flt_param_file)
        self.flt_param_file_text.setEnabled(False)

        open_flt_param_button = QtWidgets.QPushButton('Open EKF Parameters File', parent)
        open_flt_param_func = lambda: self.open_flt_param_lambda(parent)
        open_flt_param_button.clicked.connect(open_flt_param_func)

        revert_changes_button = QtWidgets.QPushButton('Revert Changes', parent)
        revert_changes_func = lambda: self.revert_changes_lambda()
        revert_changes_button.clicked.connect(revert_changes_func)

        save_flt_param_button = QtWidgets.QPushButton('Save EKF Parameters File', parent)
        save_flt_param_func = lambda: self.save_flt_param_lambda(parent)
        save_flt_param_button.clicked.connect(save_flt_param_func)

        sigma_xy_label = QtWidgets.QLabel('SRNS position sigma, m:', parent)
        sigma_xy_label.setFont(bold_font)
        sigma_xy_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.sigma_xy_text.setText(self.sigma_xy)

        sigma_v_label = QtWidgets.QLabel('SRNS speed sigma, m/s:', parent)
        sigma_v_label.setFont(bold_font)
        sigma_v_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.sigma_v_text.setText(self.sigma_v)

        sigma_a_label = QtWidgets.QLabel('Linear acceleration sigma, m/s2:', parent)
        sigma_a_label.setFont(bold_font)
        sigma_a_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.sigma_a_text.setText(self.sigma_a)

        sigma_w_label = QtWidgets.QLabel('Angular velocity sigma, deg/s:', parent)
        sigma_w_label.setFont(bold_font)
        sigma_w_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.sigma_w_text.setText(self.sigma_w)

        acc_bias_label = QtWidgets.QLabel('Linear acceleration bias, ug:', parent)
        acc_bias_label.setFont(bold_font)
        acc_bias_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.acc_bias_text.setText(self.acc_bias)

        gyr_bias_label = QtWidgets.QLabel('Angular velocity bias, deg/hr:', parent)
        gyr_bias_label.setFont(bold_font)
        gyr_bias_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.gyr_bias_text.setText(self.gyr_bias)

        layout.addWidget(flt_param_file_label, 0, 0, 1, 8)
        layout.addWidget(self.flt_param_file_text, 1, 0, 1, 8)

        layout.addWidget(open_flt_param_button, 2, 0, 1, 3)
        layout.addWidget(revert_changes_button, 2, 3, 1, 2)
        layout.addWidget(save_flt_param_button, 2, 5, 1, 3)

        layout.addWidget(sigma_xy_label, 3, 0, 1, 4)
        layout.addWidget(self.sigma_xy_text, 3, 4, 1, 4)
        layout.addWidget(sigma_v_label, 4, 0, 1, 4)
        layout.addWidget(self.sigma_v_text, 4, 4, 1, 4)

        layout.addWidget(sigma_a_label, 5, 0, 1, 4)
        layout.addWidget(self.sigma_a_text, 5, 4, 1, 4)
        layout.addWidget(sigma_w_label, 6, 0, 1, 4)
        layout.addWidget(self.sigma_w_text, 6, 4, 1, 4)

        layout.addWidget(acc_bias_label, 7, 0, 1, 4)
        layout.addWidget(self.acc_bias_text, 7, 4, 1, 4)
        layout.addWidget(gyr_bias_label, 8, 0, 1, 4)
        layout.addWidget(self.gyr_bias_text, 8, 4, 1, 4)

        layout.addWidget(self.info_label, 9, 0, 5, 8)

        parent.setLayout(layout)

    def open_flt_param_lambda(self, parent):

        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(parent,
                                                            'Open file',
                                                            self.flt_param_path,
                                                            'txt (*.txt)',
                                                            options=options)
        if filename:
            self.flt_param_file = filename
            self.flt_param_file_text.setText(self.flt_param_file)
            self.out_signals.out_signal1.emit(self.flt_param_file)
            self.load_file()
        else:
            return

    def revert_changes_lambda(self):

        if not self.flt_param_file:
            self.sigma_xy = '[10, 10, 10]'
            self.sigma_v = '[0.1, 0.1, 0.1]'
            self.sigma_a = '[0.01, 0.01, 0.01]'
            self.sigma_w = '[1, 1, 1]'
            self.acc_bias = '[1, 1, 1]'
            self.gyr_bias = '[1, 1, 1]'
            self.sigma_xy_text.setText(self.sigma_xy)
            self.sigma_v_text.setText(self.sigma_v)
            self.sigma_a_text.setText(self.sigma_a)
            self.sigma_w_text.setText(self.sigma_w)
            self.acc_bias_text.setText(self.acc_bias)
            self.gyr_bias_text.setText(self.gyr_bias)
        else:
            self.load_file()

    def save_flt_param_lambda(self, parent):

        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(parent,
                                                            'Save file',
                                                            self.flt_param_path,
                                                            'txt (*.txt)',
                                                            options=options)
        if filename:
            self.sigma_xy = self.sigma_xy_text.text()
            self.sigma_v = self.sigma_v_text.text()
            self.sigma_a = self.sigma_a_text.text()
            self.sigma_w = self.sigma_w_text.text()
            self.acc_bias = self.acc_bias_text.text()
            self.gyr_bias = self.gyr_bias_text.text()

            self.flt_param_file = filename
            self.flt_param_file_text.setText(self.flt_param_file)
            self.out_signals.out_signal1.emit(self.flt_param_file)
            with open(self.flt_param_file, 'w', encoding='utf-8') as f:
                f.write(self.sigma_xy + '\n')
                f.write(self.sigma_v + '\n')
                f.write(self.sigma_a + '\n')
                f.write(self.sigma_w + '\n')
                f.write(self.acc_bias + '\n')
                f.write(self.gyr_bias)
        else:
            return

    def load_file(self):

        with open(self.flt_param_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            self.sigma_xy = lines[0].strip()
            self.sigma_v = lines[1].strip()
            self.sigma_a = lines[2].strip()
            self.sigma_w = lines[3].strip()
            self.acc_bias = lines[4].strip()
            self.gyr_bias = lines[5].strip()

            self.sigma_xy_text.setText(self.sigma_xy)
            self.sigma_v_text.setText(self.sigma_v)
            self.sigma_a_text.setText(self.sigma_a)
            self.sigma_w_text.setText(self.sigma_w)
            self.acc_bias_text.setText(self.acc_bias)
            self.gyr_bias_text.setText(self.gyr_bias)
