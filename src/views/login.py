from PyQt6 import QtCore
from PyQt6 import QtWidgets
from datetime import datetime, timedelta
from src.db import config
from src.widget import context
from .base_window import BaseWindow

class Login(BaseWindow):
    def __init__(self):
        super(Login, self).__init__("login")
        
        # Setup UI elements
        self.password.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        
        # Connect signals
        self.loginbutton.clicked.connect(self.loginfunction)
        self.createaccbutton.clicked.connect(self.gotocreate)
        self.username.textChanged.connect(self.clear_error)
        self.password.textChanged.connect(self.clear_error)
        self.username.returnPressed.connect(self.loginfunction)
        self.password.returnPressed.connect(self.loginfunction)

        # Login attempt tracking
        self.login_attempts = 0
        self.last_attempt_time = None
        self.lockout_until = None

    def clear_error(self):
        self.error_label.setText("")
        self.error_label.setStyleSheet("color: #d93025;")

    def show_error(self, message, is_warning=False):
        self.error_label.setText(message)
        if is_warning:
            self.error_label.setStyleSheet("color: #f4b400;") # Yellow for warnings
        else:
            self.error_label.setStyleSheet("color: #d93025;") # Red for errors

    def check_lockout(self):
        if self.lockout_until and datetime.now() < self.lockout_until:
            remaining = (self.lockout_until - datetime.now()).seconds
            self.show_error(f"Tài khoản tạm khóa. Vui lòng thử lại sau {remaining} giây", True)
            return True
        return False

    def handle_failed_attempt(self):
        self.login_attempts += 1
        self.last_attempt_time = datetime.now()

        if self.login_attempts >= 5:  # 5 lần thử không thành công
            self.lockout_until = datetime.now() + timedelta(minutes=5)  # Khóa 5 phút
            self.show_error("Quá nhiều lần thử. Tài khoản bị khóa trong 5 phút", True)
            self.loginbutton.setEnabled(False)
            QtCore.QTimer.singleShot(300000, self.reset_lockout)  # 5 phút = 300000ms
        else:
            remaining_attempts = 5 - self.login_attempts
            self.show_error(f"Sai mật khẩu. Còn {remaining_attempts} lần thử")

    def reset_lockout(self):
        self.login_attempts = 0
        self.last_attempt_time = None
        self.lockout_until = None
        self.loginbutton.setEnabled(True)
        self.clear_error()

    def loginfunction(self):
        try:
            if self.check_lockout():
                return

            username = self.username.text().strip()
            password = self.password.text().strip()
            
            if not username or not password:
                self.show_error("Vui lòng nhập đầy đủ thông tin!")
                return
                
            user = config.find_user(username=username, password=password)
            if user:
                self.reset_lockout()
                context['user'] = user['username']
                context['role'] = user['role']
                context['user_id'] = user['id']
                
                from .dashboard import Dashboard
                self.navigate_to(Dashboard)
            else:
                self.password.setText("")
                self.handle_failed_attempt()

        except Exception as e:
            print("Login error:", str(e))
            self.show_error("Có lỗi xảy ra. Vui lòng thử lại sau.")

    def gotocreate(self):
        from .register import CreateAccount
        self.navigate_to(CreateAccount)



