from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import uic

from copy import deepcopy

from dfs_gui_sensor_cfg import SensorsCfgOutSignals
from dfs_gui_sensor_cfg import UserCfgGui


class UsersTableGui(QtWidgets.QDialog):

    def __init__(self, x, y, users):

        super().__init__()
        uic.loadUi('ui/Users.ui', self)

        self.out_signals = SensorsCfgOutSignals()
        self.users_ = users
        self.users = deepcopy(self.users_)

        self.add_button.clicked.connect(self.add)
        self.edit_button.clicked.connect(self.edit)
        self.revert_button.clicked.connect(self.revert)
        self.delete_button.clicked.connect(self.delete)

        self.user_cfg = None

        self.update_table()

        self.move(x - 50, y + 50)

        self.show()

    def update_table(self):

        self.table.clearContents()
        self.table.setRowCount(len(self.users))
        for i, (k, v) in enumerate(self.users.items()):
            item = QtWidgets.QTableWidgetItem(v['name'])
            self.table.setItem(i, 0, item)
        self.out_signals.out_sensors_dict.emit(self.users)

    def add(self):

        names = [v['name'] for v in self.users.values()]
        new_name = self.user_name_line.text()
        if new_name == '' or new_name in names:
            msg = QtWidgets.QMessageBox()
            msg.setInformativeText('No name or existing name!')
            msg.setWindowTitle('Error')
            msg.exec_()
        else:
            self.setWindowModality(QtCore.Qt.NonModal)
            self.user_cfg = UserCfgGui(self.geometry().x(), self.geometry().y(),
                                       name=new_name)
            self.user_cfg.out_signals.out_sensors_dict.connect(self.add_user)
            self.user_cfg.out_signals.out_sensors_name.connect(self.delete_user)
            self.user_cfg.setWindowModality(QtCore.Qt.ApplicationModal)

    def add_user(self, msg):

        self.users[msg['name']] = msg
        self.update_table()

    def delete_user(self, name):
        del self.users[name]
        self.update_table()

    def edit(self):
        row = self.table.currentRow()
        if row < 0:
            msg = QtWidgets.QMessageBox()
            msg.setInformativeText('Sensor not selected!')
            msg.setWindowTitle('Error')
            msg.exec_()
        else:
            self.setWindowModality(QtCore.Qt.NonModal)
            name = self.table.item(row, 0).text()
            self.user_cfg = UserCfgGui(self.geometry().x(), self.geometry().y(),
                                       sdict=self.users[name])
            self.user_cfg.out_signals.out_sensors_dict.connect(self.add_user)
            self.user_cfg.out_signals.out_sensors_name.connect(self.delete_user)
            self.user_cfg.setWindowModality(QtCore.Qt.ApplicationModal)

    def revert(self):

        self.users = deepcopy(self.users_)
        self.update_table()

    def delete(self):

        row = self.table.currentRow()
        col = self.table.currentColumn()
        name = self.table.item(row, 0).text()
        self.delete_user(name)
        if row < self.table.rowCount():
            self.table.setCurrentCell(row, col)

    def closeEvent(self, event):

        if self.user_cfg is not None:
            self.user_cfg.setWindowModality(QtCore.Qt.NonModal)
            self.setWindowModality(QtCore.Qt.ApplicationModal)
