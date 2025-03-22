from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QTableWidgetItem
from PyQt6.uic import loadUi
from src.db import config
from src.widget import context

class CustomerOrders(QtWidgets.QMainWindow):
    def __init__(self):
        super(CustomerOrders, self).__init__()
        loadUi("ui/customer_orders.ui", self)
        
        self.loadMyOrders()
        self.refresh_btn.clicked.connect(self.loadMyOrders)
        self.back_btn.clicked.connect(self.goBack)
        
    def loadMyOrders(self):
        user_id = context['user_id']
        orders = config.db.orders.find({'user_id': user_id}).sort('created_at', -1)
        
        self.orders_table.setRowCount(0)
        total_spent = 0
        
        for row, order in enumerate(orders):
            self.orders_table.insertRow(row)
            self.orders_table.setItem(row, 0, QTableWidgetItem(str(order['_id'])))
            self.orders_table.setItem(row, 1, QTableWidgetItem(str(order['total_amount'])))
            self.orders_table.setItem(row, 2, QTableWidgetItem(order['status']))
            self.orders_table.setItem(row, 3, QTableWidgetItem(
                order['created_at'].strftime("%Y-%m-%d %H:%M")
            ))
            total_spent += order['total_amount']
        
        self.total_spent_label.setText(f"Tổng chi tiêu: {total_spent:,.0f} VND")
    
    def goBack(self):
        from src.views.dashboard import Dashboard
        dashboard = Dashboard()
        self.widget.addWidget(dashboard)
        self.widget.setCurrentIndex(self.widget.currentIndex()+1) 