from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

from collections import OrderedDict


class CfgOutSignals(QtCore.QObject):

    out_signal1 = QtCore.pyqtSignal(dict)


class UserCfgWindow(QtWidgets.QWidget):

    def __init__(self):

        super().__init__()

        self.h = 300
        self.w = 300
        self.x = 150
        self.y = 150

        self.setFixedWidth(self.w)
        self.move(self.x, self.y)
        self.setWindowTitle('User Configuration')
        self.layout = QtWidgets.QGridLayout(self)

        self.name_text = QtWidgets.QLineEdit()
        self.pos_x_text = QtWidgets.QLineEdit()
        self.pos_y_text = QtWidgets.QLineEdit()
        self.pos_z_text = QtWidgets.QLineEdit()
        self.dt_text = QtWidgets.QLineEdit()
        self.ts_text = QtWidgets.QLineEdit()

        self.user = dict()
        self.out_signals = CfgOutSignals()

        self.user_configuration_layout()

    def user_configuration_layout(self):

        dummy_label = QtWidgets.QLabel('', self)
        dummy_label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignBottom)
        label_color = dummy_label.palette().color(QtGui.QPalette.Background)
        text_palette = dummy_label.palette()
        text_palette.setColor(dummy_label.backgroundRole(), label_color)

        name_label = QtWidgets.QLabel('User Name:', self)
        name_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)

        self.name_text.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.name_text.setText('noname')

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

        ts_label = QtWidgets.QLabel('Time Shift:', self)
        ts_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)

        self.ts_text.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.ts_text.setText('0')

        ok_button = QtWidgets.QPushButton('Ok')
        ok_func = lambda: self.ok_lambda()
        ok_button.clicked.connect(ok_func)

        cancel_button = QtWidgets.QPushButton('Cancel')
        cancel_func = lambda: self.cancel_lambda()
        cancel_button.clicked.connect(cancel_func)

        self.layout.addWidget(name_label, 0, 0, 1, 3)
        self.layout.addWidget(self.name_text, 0, 3, 1, 3)
        self.layout.addWidget(position_label, 1, 0, 1, 6)
        self.layout.addWidget(pos_x_label, 2, 0, 1, 1)
        self.layout.addWidget(self.pos_x_text, 2, 1, 1, 1)
        self.layout.addWidget(pos_y_label, 2, 2, 1, 1)
        self.layout.addWidget(self.pos_y_text, 2, 3, 1, 1)
        self.layout.addWidget(pos_z_label, 2, 4, 1, 1)
        self.layout.addWidget(self.pos_z_text, 2, 5, 1, 1)
        self.layout.addWidget(dt_label, 3, 0, 1, 4)
        self.layout.addWidget(self.dt_text, 3, 4, 1, 2)
        self.layout.addWidget(ts_label, 4, 0, 1, 4)
        self.layout.addWidget(self.ts_text, 4, 4, 1, 2)

        self.layout.addWidget(cancel_button, 5, 0, 1, 3)
        self.layout.addWidget(ok_button, 5, 3, 1, 3)
        self.show()

    def ok_lambda(self):

        self.user['name'] = self.name_text.text()
        self.user['position'] = OrderedDict({'x': self.pos_x_text.text(),
                                             'y': self.pos_y_text.text(),
                                             'z': self.pos_z_text.text(),})
        self.user['dt'] = self.dt_text.text()
        self.user['time_shift'] = self.ts_text.text()

        self.out_signals.out_signal1.emit(self.user)
        self.close()

    def cancel_lambda(self):

        self.close()

    def users_out_signal2_response(self, msg):

        self.user = msg

        self.name_text.setText(self.user['name'])
        self.pos_x_text.setText(self.user['position']['x'])
        self.pos_y_text.setText(self.user['position']['y'])
        self.pos_z_text.setText(self.user['position']['z'])
        self.dt_text.setText(self.user['dt'])
        self.ts_text.setText(self.user['time_shift'])
