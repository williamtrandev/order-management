from PyQt6 import QtWidgets
from PyQt6.uic import loadUi
from src.widget import widget, context

class BaseWindow(QtWidgets.QMainWindow):
    def __init__(self, ui_file):
        super(BaseWindow, self).__init__()
        self.widget = widget
        try:
            loadUi(f"ui/{ui_file}.ui", self)
        except Exception as e:
            print(f"Error loading UI {ui_file}: {str(e)}")
            raise

    def navigate_to(self, window_class):
        """Safe navigation between windows"""
        try:
            next_window = window_class()
            self.widget.addWidget(next_window)
            self.widget.setCurrentIndex(self.widget.currentIndex() + 1)
        except Exception as e:
            print(f"Navigation error to {window_class.__name__}: {str(e)}")
            self.show_error("Lỗi chuyển trang. Vui lòng thử lại.")

    def show_error(self, message, is_warning=False):
        """Unified error display"""
        if hasattr(self, 'error_label'):
            self.error_label.setText(message)
            color = "#f4b400" if is_warning else "#d93025"
            self.error_label.setStyleSheet(f"color: {color};") 