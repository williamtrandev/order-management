from PyQt6.QtWidgets import QTableWidgetItem, QMainWindow

from .base_window import BaseWindow
from src.widget import context
from src.db import config

class Dashboard(BaseWindow):
    def __init__(self):
        super(Dashboard, self).__init__("dashboard")
        
        # Setup welcome message
        self.welcome_label.setText(f"Chào mừng, {context.get('user', '')}")
        
        # Setup buttons visibility and connections
        self.setupButtons()
        self.setupNavigationSignals()

    def setupButtons(self):
        """Setup button visibility"""
        # Show all buttons
        self.stats_btn.setVisible(True)
        self.orders_btn.setVisible(True)
        self.users_list_btn.setVisible(True)

    def setupNavigationSignals(self):
        """Connect navigation buttons to their respective views"""
        self.stats_btn.clicked.connect(lambda: self.navigate_to_view('AdminStats'))
        self.orders_btn.clicked.connect(lambda: self.navigate_to_view('AdminOrders'))
        self.users_list_btn.clicked.connect(self.show_customer_list)
        self.logout_btn.clicked.connect(self.logout)

    def navigate_to_view(self, view_name):
        """Dynamic navigation to views"""
        try:
            # Import the view dynamically
            view_module = __import__(f'src.views.{view_name.lower()}', fromlist=[view_name])
            view_class = getattr(view_module, view_name)
            self.navigate_to(view_class)
        except Exception as e:
            print(f"Navigation error to {view_name}: {str(e)}")
            self.show_error("Lỗi chuyển trang. Vui lòng thử lại.")

    def show_customer_list(self):
        """Handle customer list navigation"""
        try:
            from .customer_list import CustomerList
            self.navigate_to(CustomerList)
        except Exception as e:
            print(f"Navigation error: {str(e)}")
            self.show_error("Không thể chuyển trang. Vui lòng thử lại.")

    def logout(self):
        """Handle logout"""
        context['user'] = None
        context['user_id'] = None
        
        from .login import Login
        self.navigate_to(Login)

    def table_view(self):
        products = config.list_product()
        row = 0
        self.tableWidget.setRowCount(len(products))
        for product in products:
            self.tableWidget.setItem(row,0,QTableWidgetItem(product['name']))
            self.tableWidget.setItem(row,1,QTableWidgetItem(product['category']))
            self.tableWidget.setItem(row,2,QTableWidgetItem(str(product['stock'])))
            row+=1
    
    def showchart_by_stock (self):
        from src.views import graph
        self.window = QMainWindow()
        self.ui = graph.Graph1()

    def showchart_by_product (self):
        from src.views import graph
        self.window = QMainWindow()
        self.ui = graph.Graph2()



        





        









    