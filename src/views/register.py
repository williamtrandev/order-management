from PyQt6 import QtWidgets
from src.db import config
from .base_window import BaseWindow

class CreateAccount(BaseWindow):
    def __init__(self):
        super(CreateAccount, self).__init__("register")
        
        # Setup UI elements
        self.password.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.confirm_password.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        
        # Connect signals
        self.create_button.clicked.connect(self.createAccountFunction)
        self.back_button.clicked.connect(self.goBackToLogin)
        self.username.textChanged.connect(self.clear_error)
        self.password.textChanged.connect(self.clear_error)
        self.confirm_password.textChanged.connect(self.clear_error)

    def clear_error(self):
        self.error_label.setText("")
        self.error_label.setStyleSheet("color: #d93025;")

    def createAccountFunction(self):
        try:
            username = self.username.text().strip()
            password = self.password.text().strip()
            confirm_pass = self.confirm_password.text().strip()
            
            if not username or not password or not confirm_pass:
                self.show_error("Vui lòng nhập đầy đủ thông tin!")
                return
                
            if len(username) < 4:
                self.show_error("Tên đăng nhập phải có ít nhất 4 ký tự!")
                return
                
            if len(password) < 6:
                self.show_error("Mật khẩu phải có ít nhất 6 ký tự!")
                return
            
            if password != confirm_pass:
                self.show_error("Mật khẩu xác nhận không khớp!")
                return
            
            # Check if username exists
            existing_user = config.db.users.find_one({'username': username})
            if existing_user:
                self.show_error("Tên đăng nhập đã tồn tại!")
                return
            
            # Create new account
            config.create_user(username=username, password=password, role='customer')
            
            # Show success message
            QtWidgets.QMessageBox.information(
                self,
                "Thành công",
                "Tạo tài khoản thành công! Vui lòng đăng nhập."
            )
            
            # Go back to login
            self.goBackToLogin()
            
        except Exception as e:
            print("Create account error:", str(e))
            self.show_error("Có lỗi xảy ra. Vui lòng thử lại sau.")

    def goBackToLogin(self):
        from .login import Login
        self.navigate_to(Login)