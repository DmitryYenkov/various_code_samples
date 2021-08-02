from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui

from collections import OrderedDict
import copy

from sea_widget_user_cfg import UserCfgWindow


class UsersTabOutSignals(QtCore.QObject):

    out_signal1 = QtCore.pyqtSignal(dict)
    out_signal2 = QtCore.pyqtSignal(dict)


class UsersSettingsTab(QtWidgets.QWidget):

    def __init__(self, parent):

        super().__init__(parent)

        self.user_points = dict()
        self.user_points_backup = dict()

        self.table_widget = QtWidgets.QTableWidget(14, 1)

        self.out_signals = UsersTabOutSignals()

        self.users_settings_tab_layout(parent)

    def users_settings_tab_layout(self, parent):

        layout = QtWidgets.QGridLayout(parent)
        layout.setSpacing(5)

        dummy_label = QtWidgets.QLabel('', parent)
        label_color = dummy_label.palette().color(QtGui.QPalette.Background)
        text_palette = dummy_label.palette()
        text_palette.setColor(dummy_label.backgroundRole(), label_color)
        bold_font = QtGui.QFont()
        bold_font.setBold(True)

        self.table_widget.setHorizontalHeaderLabels(['Name'])
        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)

        add_button = QtWidgets.QPushButton('Add')
        add_func = lambda: self.add_lambda()
        add_button.clicked.connect(add_func)

        edit_button = QtWidgets.QPushButton('Edit')
        edit_func = lambda: self.edit_lambda()
        edit_button.clicked.connect(edit_func)

        delete_button = QtWidgets.QPushButton('Delete')
        delete_func = lambda: self.delete_lambda()
        delete_button.clicked.connect(delete_func)

        revert_button = QtWidgets.QPushButton('Revert')
        revert_func = lambda: self.revert_lambda()
        revert_button.clicked.connect(revert_func)

        layout.addWidget(self.table_widget, 0, 0, 12, 6)
        layout.addWidget(add_button, 0, 7, 1, 1)
        layout.addWidget(edit_button, 1, 7, 1, 1)
        layout.addWidget(delete_button, 2, 7, 1, 1)
        layout.addWidget(revert_button, 3, 7, 1, 1)

        parent.setLayout(layout)

    def add_lambda(self):

        add_dialog = UserCfgWindow()
        add_dialog.out_signals.out_signal1.connect(self.cfg_out_signal1_response)

    def edit_lambda(self):

        rows = [s.row() for s in self.table_widget.selectedItems()]
        if not rows:
            return

        edit_dialog = UserCfgWindow()
        self.out_signals.out_signal2.connect(edit_dialog.users_out_signal2_response)
        edit_dialog.out_signals.out_signal1.connect(self.cfg_out_signal2_response)

        name = self.table_widget.item(rows[0], 0).text()
        self.out_signals.out_signal2.emit(self.user_points[name])

        self.out_signals.out_signal2.disconnect()

    def delete_lambda(self):

        selected = self.table_widget.selectedItems()
        if not selected:
            return
        rows = [s.row() for s in self.table_widget.selectedItems()]
        names = [self.table_widget.item(row, 0).text() for row in rows]
        for name in names:
            del self.user_points[name]
        self.update_table()

    def revert_lambda(self):

        self.user_points = copy.deepcopy(self.user_points_backup)
        self.update_table()

    def update_table(self):

        self.table_widget.clear()
        for i, k in enumerate(self.user_points.keys()):
            item = QtWidgets.QTableWidgetItem(k)
            self.table_widget.setItem(i, 0, item)

        self.table_widget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.out_signals.out_signal1.emit(self.user_points)

    def settings_tab_out_signal1_response(self, msg):

        for k, v in msg.items():
            if v['type'] == 'user':
                self.user_points[k] = v

        self.user_points_backup = copy.deepcopy(self.user_points)
        self.update_table()

    def cfg_out_signal1_response(self, msg):

        if msg['name'] in self.user_points.keys():
            err = QtWidgets.QMessageBox()
            err.setIcon(QtWidgets.QMessageBox.Critical)
            err.setText('This name already exists! Entry will be overwritten')
            err.setWindowTitle('Error')
            err.exec_()
        else:
            self.cfg_out_signal2_response(msg)

    def cfg_out_signal2_response(self, msg):

        new_msg = OrderedDict([('name', msg['name']),
                               ('type', 'user'),
                               ('position', msg['position']),
                               ('dt', msg['dt']),
                               ('time_shift', msg['time_shift'])])
        self.user_points[msg['name']] = new_msg
        self.update_table()
