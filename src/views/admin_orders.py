from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QTableWidgetItem
from PyQt6.uic import loadUi
from datetime import datetime
from src.db import config

class AdminOrders(QtWidgets.QMainWindow):
    def __init__(self):
        super(AdminOrders, self).__init__()
        loadUi("ui/admin_orders.ui", self)
        
        self.loadOrders()
        self.refresh_btn.clicked.connect(self.loadOrders)
        self.back_btn.clicked.connect(self.goBack)
        
    def loadOrders(self):
        orders = config.db.orders.find().sort('created_at', -1)
        self.orders_table.setRowCount(0)
        
        for row, order in enumerate(orders):
            self.orders_table.insertRow(row)
            self.orders_table.setItem(row, 0, QTableWidgetItem(str(order['_id'])))
            self.orders_table.setItem(row, 1, QTableWidgetItem(order['user_id']))
            self.orders_table.setItem(row, 2, QTableWidgetItem(str(order['total_amount'])))
            self.orders_table.setItem(row, 3, QTableWidgetItem(order['status']))
            self.orders_table.setItem(row, 4, QTableWidgetItem(
                order['created_at'].strftime("%Y-%m-%d %H:%M")
            ))
    
    def goBack(self):
        from src.views.dashboard import Dashboard
        dashboard = Dashboard()
        self.widget.addWidget(dashboard)
        self.widget.setCurrentIndex(self.widget.currentIndex()+1) 