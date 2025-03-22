from PyQt6 import QtWidgets
from PyQt6.uic import loadUi
from src.db import config
from datetime import datetime, timedelta

class AdminStats(QtWidgets.QMainWindow):
    def __init__(self):
        super(AdminStats, self).__init__()
        loadUi("ui/admin_stats.ui", self)
        
        self.loadStats()
        self.refresh_btn.clicked.connect(self.loadStats)
        self.back_btn.clicked.connect(self.goBack)
        
    def loadStats(self):
        # Thống kê trong tháng hiện tại
        start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0)
        
        # Tổng doanh thu
        monthly_revenue = config.db.orders.aggregate([
            {
                '$match': {
                    'created_at': {'$gte': start_of_month}
                }
            },
            {
                '$group': {
                    '_id': None,
                    'total': {'$sum': '$total_amount'}
                }
            }
        ]).next()['total']
        
        # Số đơn hàng
        order_count = config.db.orders.count_documents({
            'created_at': {'$gte': start_of_month}
        })
        
        # Top 5 khách hàng chi tiêu nhiều nhất
        top_customers = config.db.users.find(
            {'role': 'customer'}
        ).sort('total_spent', -1).limit(5)
        
        # Cập nhật UI
        self.revenue_label.setText(f"Doanh thu tháng: {monthly_revenue:,.0f} VND")
        self.orders_label.setText(f"Số đơn hàng: {order_count}")
        
        # Hiển thị top khách hàng
        self.customers_table.setRowCount(0)
        for row, customer in enumerate(top_customers):
            self.customers_table.insertRow(row)
            self.customers_table.setItem(row, 0, QTableWidgetItem(customer['username']))
            self.customers_table.setItem(row, 1, QTableWidgetItem(f"{customer['total_spent']:,.0f}"))
    
    def goBack(self):
        from src.views.dashboard import Dashboard
        dashboard = Dashboard()
        self.widget.addWidget(dashboard)
        self.widget.setCurrentIndex(self.widget.currentIndex()+1) 