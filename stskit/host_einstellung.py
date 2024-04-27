"""
Host Einstellungsfenster

- Auswahl des Hostnamens/der IP

"""
import ipaddress
import logging
import re

from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot

from stskit.qt.ui_host_einstellungen import Ui_HostEinstellungenWindow

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

    
class HostEinstellungWindow(QtWidgets.QMainWindow):

    def __init__(self, shared_variables: dict):
        super().__init__()

        self.shared_variables = shared_variables

        self.in_update = True
        self.ui = Ui_HostEinstellungenWindow()
        self.ui.setupUi(self)

        self.setWindowTitle(f"Einstellungen")

        self.ui.hostname_ip.setText(self.shared_variables["host"])
        self.ui.label_falscher_hostname_ip.hide()

        self.in_update = False

    def is_valid_hostname(self):
        hostname = self.ui.hostname_ip.text()
        if hostname[-1] == ".":
            # strip exactly one dot from the right, if present
            hostname = hostname[:-1]
        if len(hostname) > 253:
            return False

        labels = hostname.split(".")

        # the TLD must be not all-numeric
        if re.match(r"[0-9]+$", labels[-1]):
            return False

        allowed = re.compile(r"(?!-)[a-z0-9-]{1,63}(?<!-)$", re.IGNORECASE)
        return all(allowed.match(label) for label in labels)

    @pyqtSlot()
    def apply(self):
        try:
            ipaddress.IPv4Network(self.ui.hostname_ip.text())
        except ValueError:
            if not self.is_valid_hostname():
                self.ui.label_falscher_hostname_ip.show()
                return
        self.shared_variables["host"] = self.ui.hostname_ip.text()
        self.shared_variables["close"] = False
        self.close()

    @pyqtSlot()
    def retry(self):
        self.shared_variables["close"] = False
        self.close()

