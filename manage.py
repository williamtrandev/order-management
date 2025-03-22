import sys
from PyQt6 import QtWidgets
from src.views.login import Login
from src.widget import widget

app = QtWidgets.QApplication(sys.argv)

# Initialize first screen
mainwindow = Login()
widget.addWidget(mainwindow)
widget.show()

try:
    sys.exit(app.exec())
except:
    print("Exiting")