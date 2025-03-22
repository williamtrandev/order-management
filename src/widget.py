import sys
from PyQt6 import QtWidgets

app=QtWidgets.QApplication(sys.argv)

# Global widget for navigation
class GlobalWidget:
    def __init__(self):
        self.widget = QtWidgets.QStackedWidget()
        self.widget.setFixedWidth(800)
        self.widget.setFixedHeight(600)

    def get_widget(self):
        return self.widget

# Create global instance
global_widget = GlobalWidget()
widget = global_widget.get_widget()

context = {
    'user': None,
    'role': None,
    'user_id': None
}