import os
import json
import subprocess
from PyQt5 import QtWidgets


root_folder = os.path.split(os.path.split(os.path.split(os.getcwd())[0])[0])[0]
cfg_filename = 'cfg_gui.json'


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


def clean(item):
    """Clean up the memory by closing and deleting the item if possible."""
    if isinstance(item, list) or isinstance(item, dict):
        for _ in range(len(item)):
            clean(list(item).pop())
    else:
        try:
            item.close()
        except (RuntimeError, AttributeError):  # deleted or no close method
            try:
                item.deleteLater()
            except (RuntimeError, AttributeError):  # deleted or no deleteLater method
                pass


def clean_up(obj):
    # Clean up everything
    for i in obj.__dict__:
        item = obj.__dict__[i]
        clean(item)


def join(*args):
    return os.path.join(*args).replace('\\', '/')


def save_cfg(paths):
    with open(cfg_filename, 'w') as cfg:
        json.dump(paths, cfg)
