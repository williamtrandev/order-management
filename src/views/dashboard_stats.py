from PyQt6 import QtWidgets, QtCore
from .base_window_with_sidebar import BaseWindowWithSidebar
from src.db import config
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import calendar
from bson import ObjectId

class DashboardStats(BaseWindowWithSidebar):
    def __init__(self):
        super(DashboardStats, self).__init__("dashboard_stats")
        
        # Setup refresh timer (auto refresh every 5 minutes)
        self.refresh_timer = QtCore.QTimer()
        self.refresh_timer.timeout.connect(self.loadStats)
        self.refresh_timer.start(300000)  # 5 minutes
        
        # Connect signals
        self.refresh_btn.clicked.connect(self.loadStats)
        self.back_btn.clicked.connect(self.goBack)
        
        # Initial load
        self.loadStats()

    def loadStats(self):
        try:
            current_year = datetime.now().year
            current_month = datetime.now().month
            
            # Revenue Statistics
            self.loadRevenueStats(current_year)
            
            # Age Demographics
            self.loadAgeDemographics()
            
            # Top Products
            self.loadTopProducts()
            
            # Order Statistics
            self.loadOrderStats(current_year)
            
            # Update last refresh time
            self.last_refresh_label.setText(
                f"Cập nhật lúc: {datetime.now().strftime('%H:%M:%S %d/%m/%Y')}"
            )
            
        except Exception as e:
            print("Error loading stats:", str(e))
            self.show_error("Không thể tải dữ liệu thống kê")

    def loadRevenueStats(self, year):
        try:
            # Get monthly revenue
            monthly_revenue = [0] * 12
            total_revenue = 0
            
            pipeline = [
                {
                    '$match': {
                        'created_at': {
                            '$gte': datetime(year, 1, 1),
                            '$lte': datetime(year, 12, 31, 23, 59, 59)
                        }
                    }
                },
                {
                    '$group': {
                        '_id': {'$month': '$created_at'},
                        'revenue': {'$sum': '$total_amount'}
                    }
                }
            ]
            
            results = list(config.db.orders.aggregate(pipeline))
            for result in results:
                month_index = result['_id'] - 1
                revenue = result['revenue']
                monthly_revenue[month_index] = revenue
                total_revenue += revenue
            
            # Update total revenue label
            self.total_revenue_label.setText(f"{total_revenue:,.0f} VNĐ")
            
            # Create revenue chart
            fig_revenue = plt.figure(figsize=(8, 4))
            ax_revenue = fig_revenue.add_subplot(111)
            
            months = calendar.month_abbr[1:]
            ax_revenue.bar(months, monthly_revenue, color='#1a73e8')
            ax_revenue.set_title('Doanh thu theo tháng')
            ax_revenue.set_ylabel('Doanh thu (VNĐ)')
            plt.xticks(rotation=45)
            
            # Add value labels on top of bars
            for i, v in enumerate(monthly_revenue):
                ax_revenue.text(i, v, f'{v:,.0f}', ha='center', va='bottom')
            
            # Update revenue chart widget
            self.revenue_chart.setParent(None)
            self.revenue_chart = FigureCanvas(fig_revenue)
            self.revenue_chart_layout.addWidget(self.revenue_chart)
            
        except Exception as e:
            print("Error loading revenue stats:", str(e))
            raise

    def loadAgeDemographics(self):
        try:
            # Get age groups
            now = datetime.now()
            age_groups = {
                '<25': 0,
                '25-35': 0,
                '>35': 0
            }
            
            users = config.db.users.find({'birthdate': {'$exists': True}})
            for user in users:
                birthdate = user.get('birthdate')
                if birthdate:
                    age = (now - birthdate).days // 365
                    if age < 25:
                        age_groups['<25'] += 1
                    elif age <= 35:
                        age_groups['25-35'] += 1
                    else:
                        age_groups['>35'] += 1
            
            # Create age demographics pie chart
            fig_age = plt.figure(figsize=(6, 6))
            ax_age = fig_age.add_subplot(111)
            
            colors = ['#1a73e8', '#34a853', '#fbbc04']
            wedges, texts, autotexts = ax_age.pie(
                age_groups.values(),
                labels=age_groups.keys(),
                colors=colors,
                autopct='%1.1f%%'
            )
            ax_age.set_title('Phân bố độ tuổi khách hàng')
            
            # Update age chart widget
            self.age_chart.setParent(None)
            self.age_chart = FigureCanvas(fig_age)
            self.age_chart_layout.addWidget(self.age_chart)
            
        except Exception as e:
            print("Error loading age demographics:", str(e))
            raise

    def loadTopProducts(self):
        try:
            # Get top 5 products
            pipeline = [
                {
                    '$unwind': '$items'
                },
                {
                    '$group': {
                        '_id': '$items.product_id',
                        'total_quantity': {'$sum': '$items.quantity'},
                        'total_revenue': {'$sum': {'$multiply': ['$items.price', '$items.quantity']}}
                    }
                },
                {
                    '$sort': {'total_quantity': -1}
                },
                {
                    '$limit': 5
                }
            ]
            
            top_products = list(config.db.orders.aggregate(pipeline))
            
            # Clear current table
            self.top_products_table.setRowCount(0)
            
            # Populate table
            for row, product in enumerate(top_products):
                self.top_products_table.insertRow(row)
                
                # Get product details
                product_id = ObjectId(product['_id'])
                product_details = config.db.products.find_one({'_id': product_id})
                
                if product_details:
                    items = [
                        (product_details.get('name', 'Unknown'), QtCore.Qt.AlignmentFlag.AlignLeft),
                        (f"{product['total_quantity']:,}", QtCore.Qt.AlignmentFlag.AlignRight),
                        (f"{product['total_revenue']:,.0f} VNĐ", QtCore.Qt.AlignmentFlag.AlignRight)
                    ]
                    
                    for col, (item, alignment) in enumerate(items):
                        table_item = QtWidgets.QTableWidgetItem(str(item))
                        table_item.setTextAlignment(alignment)
                        self.top_products_table.setItem(row, col, table_item)
            
        except Exception as e:
            print("Error loading top products:", str(e))
            raise

    def loadOrderStats(self, year):
        try:
            # Get monthly orders
            monthly_orders = [0] * 12
            total_orders = 0
            
            pipeline = [
                {
                    '$match': {
                        'created_at': {
                            '$gte': datetime(year, 1, 1),
                            '$lte': datetime(year, 12, 31, 23, 59, 59)
                        }
                    }
                },
                {
                    '$group': {
                        '_id': {'$month': '$created_at'},
                        'count': {'$sum': 1}
                    }
                }
            ]
            
            results = list(config.db.orders.aggregate(pipeline))
            for result in results:
                month_index = result['_id'] - 1
                count = result['count']
                monthly_orders[month_index] = count
                total_orders += count
            
            # Update total orders label
            self.total_orders_label.setText(f"{total_orders:,}")
            
            # Create orders chart
            fig_orders = plt.figure(figsize=(8, 4))
            ax_orders = fig_orders.add_subplot(111)
            
            months = calendar.month_abbr[1:]
            ax_orders.plot(months, monthly_orders, marker='o', color='#34a853')
            ax_orders.set_title('Số đơn hàng theo tháng')
            ax_orders.set_ylabel('Số đơn hàng')
            plt.xticks(rotation=45)
            
            # Add value labels on points
            for i, v in enumerate(monthly_orders):
                ax_orders.text(i, v, str(v), ha='center', va='bottom')
            
            # Update orders chart widget
            self.orders_chart.setParent(None)
            self.orders_chart = FigureCanvas(fig_orders)
            self.orders_chart_layout.addWidget(self.orders_chart)
            
        except Exception as e:
            print("Error loading order stats:", str(e))
            raise

    def goBack(self):
        from .dashboard import Dashboard
        self.navigate_to(Dashboard) 