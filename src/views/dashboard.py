from PyQt6.QtWidgets import QTableWidgetItem, QMainWindow

from .base_window import BaseWindow
from src.widget import context
from src.db import config

class Dashboard(BaseWindow):
    def __init__(self):
        super(Dashboard, self).__init__("dashboard")
        
        # Setup based on user role
        self.user_role = context.get('role', 'customer')
        self.welcome_label.setText(f"Chào mừng, {context.get('user', '')}")
        
        if self.user_role == 'admin':
            self.setupAdminView()
        else:
            self.setupCustomerView()
            
        # Connect signals
        self.logout_btn.clicked.connect(self.logout)
        self.setupNavigationSignals()

    def setupAdminView(self):
        """Show admin specific buttons and stats"""
        self.admin_stats_btn.setVisible(True)
        self.order_management_btn.setVisible(True)
        self.my_orders_btn.setVisible(False)
        self.favorite_products_btn.setVisible(False)

    def setupCustomerView(self):
        """Show customer specific elements"""
        self.admin_stats_btn.setVisible(False)
        self.order_management_btn.setVisible(False)
        self.my_orders_btn.setVisible(True)
        self.favorite_products_btn.setVisible(True)

    def setupNavigationSignals(self):
        """Connect navigation buttons to their respective views"""
        if self.user_role == 'admin':
            self.admin_stats_btn.clicked.connect(lambda: self.navigate_to_view('AdminStats'))
            self.order_management_btn.clicked.connect(lambda: self.navigate_to_view('AdminOrders'))
        else:
            self.my_orders_btn.clicked.connect(lambda: self.navigate_to_view('CustomerOrders'))
            self.favorite_products_btn.clicked.connect(lambda: self.navigate_to_view('FavoriteProducts'))

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

    def logout(self):
        """Handle logout"""
        context['user'] = None
        context['role'] = None
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



        





        









    