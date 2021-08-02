from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

from collections import OrderedDict


param_names = OrderedDict({
    'precision': 'Precision:',
    'sigma': 'Sigma:',
    'sigma_R': 'Sigma Horizontal:',
    'sigma_h': 'Sigma Vertical:',
    'sigma_V': 'Sigma Velocity:',
    'sigma_C': 'Sigma Course:',
    'loss_prob': 'Loss Probability:',
    'NBK_acc_x': 'Acc X NBK:',
    'NBK_acc_y': 'Acc Y NBK:',
    'NBK_acc_z': 'Acc Z NBK:',
    'NBK_gyr_x': 'Gyro X NBK:',
    'NBK_gyr_y': 'Gyro Y NBK:',
    'NBK_gyr_z': 'Gyro Z NBK:',
    'acc_scale': 'Acc Scale:',
    'gyr_scale': 'Gyro Scale:',
    'pitch_prec': 'Pitch precision:',
    'roll_prec': 'Roll precision:',
})
param_names_r = OrderedDict({v: k for k, v in param_names.items()})
sensor_types = OrderedDict({
    'gyrocompass': [param_names['precision']],
    'lag':  [param_names['sigma']],
    'srns': [param_names['sigma_R'], param_names['sigma_h'],
             param_names['loss_prob'],
             param_names['sigma_V'], param_names['sigma_C']],
    'sgs': [param_names['pitch_prec'], param_names['roll_prec'],
            param_names['NBK_acc_x'], param_names['NBK_acc_y'], param_names['acc_scale']],
    'imu': [param_names['NBK_acc_x'], param_names['NBK_acc_y'],
            param_names['NBK_acc_z'], param_names['acc_scale'],
            param_names['NBK_gyr_x'], param_names['NBK_gyr_y'],
            param_names['NBK_gyr_z'], param_names['gyr_scale']]
})


class CfgOutSignals(QtCore.QObject):

    out_signal1 = QtCore.pyqtSignal(dict)


class SensorCfgWindow(QtWidgets.QWidget):

    def __init__(self):

        super().__init__()

        self.h = 300
        self.w = 300
        self.x = 150
        self.y = 150

        self.setFixedWidth(self.w)
        self.move(self.x, self.y)
        self.setWindowTitle('Sensor Configuration')
        self.layout = QtWidgets.QGridLayout(self)

        self.name_text = QtWidgets.QLineEdit()
        self.type_select = QtWidgets.QComboBox()
        self.pos_x_text = QtWidgets.QLineEdit()
        self.pos_y_text = QtWidgets.QLineEdit()
        self.pos_z_text = QtWidgets.QLineEdit()
        self.dt_text = QtWidgets.QLineEdit()

        self.sensor = dict()
        self.out_signals = CfgOutSignals()

        self.param_set = []

        self.sensor_configuration_layout()

    def sensor_configuration_layout(self):

        dummy_label = QtWidgets.QLabel('', self)
        dummy_label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignBottom)
        label_color = dummy_label.palette().color(QtGui.QPalette.Background)
        text_palette = dummy_label.palette()
        text_palette.setColor(dummy_label.backgroundRole(), label_color)

        name_label = QtWidgets.QLabel('Sensor Name:', self)
        name_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)

        self.name_text.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.name_text.setText('noname')

        type_label = QtWidgets.QLabel('Sensor Type:', self)
        type_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)

        for t in sensor_types.keys():
            self.type_select.addItem(t)
        select_type_func = lambda: self.select_type_lambda()
        self.type_select.currentIndexChanged.connect(select_type_func)

        position_label = QtWidgets.QLabel('Position:', self)
        position_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)

        pos_x_label = QtWidgets.QLabel('X:', self)
        pos_x_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)

        pos_y_label = QtWidgets.QLabel('Y:', self)
        pos_y_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)

        pos_z_label = QtWidgets.QLabel('Z:', self)
        pos_z_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)

        self.pos_x_text.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.pos_x_text.setText('0.0')

        self.pos_y_text.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.pos_y_text.setText('0.0')

        self.pos_z_text.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.pos_z_text.setText('0.0')

        dt_label = QtWidgets.QLabel('Time Interval:', self)
        dt_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)

        self.dt_text.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.dt_text.setText('1')

        max_param_len = max([len(v) for v in sensor_types.values()])
        for i in range(max_param_len):
            l = QtWidgets.QLabel('', self)
            e = QtWidgets.QLineEdit()
            l.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
            e.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
            e.setText('0.0')
            l.setVisible(False)
            e.setVisible(False)
            self.param_set.append((l, e))

        ok_button = QtWidgets.QPushButton('Ok')
        ok_func = lambda: self.ok_lambda()
        ok_button.clicked.connect(ok_func)

        cancel_button = QtWidgets.QPushButton('Cancel')
        cancel_func = lambda: self.cancel_lambda()
        cancel_button.clicked.connect(cancel_func)

        self.layout.addWidget(name_label, 0, 0, 1, 3)
        self.layout.addWidget(self.name_text, 0, 3, 1, 3)
        self.layout.addWidget(type_label, 1, 0, 1, 3)
        self.layout.addWidget(self.type_select, 1, 3, 1, 3)
        self.layout.addWidget(position_label, 2, 0, 1, 6)
        self.layout.addWidget(pos_x_label, 3, 0, 1, 1)
        self.layout.addWidget(self.pos_x_text, 3, 1, 1, 1)
        self.layout.addWidget(pos_y_label, 3, 2, 1, 1)
        self.layout.addWidget(self.pos_y_text, 3, 3, 1, 1)
        self.layout.addWidget(pos_z_label, 3, 4, 1, 1)
        self.layout.addWidget(self.pos_z_text, 3, 5, 1, 1)
        self.layout.addWidget(dt_label, 4, 0, 1, 4)
        self.layout.addWidget(self.dt_text, 4, 4, 1, 2)

        for i, (l, e) in enumerate(self.param_set):
            self.layout.addWidget(l, 5+i, 0, 1, 3)
            self.layout.addWidget(e, 5+i, 3, 1, 3)

        self.layout.addWidget(cancel_button, 5+len(self.param_set), 0, 1, 3)
        self.layout.addWidget(ok_button, 5 + len(self.param_set), 3, 1, 3)
        self.select_type_lambda()
        self.show()

    def select_type_lambda(self):

        type_ = self.type_select.currentText()
        self.set_visibility(type_)

    def set_visibility(self, type_):

        for (l, e) in self.param_set:
            l.setVisible(False)
            e.setVisible(False)
        for i, p in enumerate(sensor_types[type_]):
            self.param_set[i][0].setText(p)
            if 'NBK' in self.param_set[i][0].text():
                self.param_set[i][1].setText('0.0,0.0,0.0')
            else:
                self.param_set[i][1].setText('0.0')
            self.param_set[i][0].setVisible(True)
            self.param_set[i][1].setVisible(True)

    def ok_lambda(self):

        self.sensor['name'] = self.name_text.text()
        self.sensor['type'] = self.type_select.currentText()
        self.sensor['position'] = OrderedDict({'x': self.pos_x_text.text(),
                                               'y': self.pos_y_text.text(),
                                               'z': self.pos_z_text.text(), })
        self.sensor['dt'] = self.dt_text.text()
        for (l, e) in self.param_set:
            if l.isVisible():
                if 'NBK' in l.text():
                    nbk = OrderedDict({p: v.strip() for p, v in zip('NBK', e.text().strip().split(','))})
                    self.sensor[param_names_r[l.text()]] = nbk
                else:
                    self.sensor[param_names_r[l.text()]] = e.text()

        self.out_signals.out_signal1.emit(self.sensor)
        self.close()

    def cancel_lambda(self):

        self.close()

    def sensors_out_signal2_response(self, msg):

        self.sensor = msg

        self.name_text.setText(self.sensor['name'])
        type_idx = self.type_select.findText(self.sensor['type'],
                                             QtCore.Qt.MatchFixedString)
        if type_idx >= 0:
            self.type_select.setCurrentIndex(type_idx)
        else:
            err = QtWidgets.QMessageBox()
            err.setIcon(QtWidgets.QMessageBox.Critical)
            err.setText('Unknown Type!')
            err.setWindowTitle('Error')
            err.exec_()
            return
        self.pos_x_text.setText(self.sensor['position']['x'])
        self.pos_y_text.setText(self.sensor['position']['y'])
        self.pos_z_text.setText(self.sensor['position']['z'])
        self.dt_text.setText(self.sensor['dt'])

        param_keys = sensor_types[self.sensor['type']]
        self.set_visibility(self.sensor['type'])
        for i, p in enumerate(param_keys):
            try:
                self.param_set[i][1].setText(self.sensor[param_names_r[p]])
            except Exception:
                param_array = ','.join([v for v in self.sensor[param_names_r[p]].values()])
                self.param_set[i][1].setText(param_array)
