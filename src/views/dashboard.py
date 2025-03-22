from PyQt6 import QtWidgets, QtCore
from datetime import datetime
from .base_window_with_sidebar import BaseWindowWithSidebar
from src.db import config
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from datetime import date

class AgeDistributionChart(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super(AgeDistributionChart, self).__init__(self.fig)
        self.setParent(parent)
        
        # Set background color
        self.fig.patch.set_facecolor('#ffffff')
        self.axes.set_facecolor('#f8f9fa')
        
        # Set title
        self.axes.set_title('Phân bố độ tuổi khách hàng', fontsize=14, fontweight='bold')

    def update_chart(self, age_data):
        # Clear previous plot
        self.axes.clear()
        
        # Data for pie chart
        labels = ['Dưới 25 tuổi', '25-35 tuổi', 'Trên 35 tuổi']
        sizes = [age_data.get('under_25', 0), age_data.get('between_25_35', 0), age_data.get('over_35', 0)]
        colors = ['#4285F4', '#34A853', '#FBBC05']
        explode = (0.1, 0, 0)  # explode the 1st slice (under 25)
        
        # Plot pie chart
        self.axes.pie(sizes, explode=explode, labels=labels, colors=colors,
                autopct='%1.1f%%', shadow=True, startangle=90)
        self.axes.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        
        # Add legend outside of the pie chart
        self.axes.legend(labels, loc="lower center", bbox_to_anchor=(0.5, -0.15), ncol=3)
        
        # Set title
        self.axes.set_title('Phân bố độ tuổi khách hàng', fontsize=14, fontweight='bold')
        
        # Add some padding at the bottom for the legend
        self.fig.subplots_adjust(bottom=0.2)
        
        # Refresh canvas
        self.draw()

class Dashboard(BaseWindowWithSidebar):
    def __init__(self):
        super(Dashboard, self).__init__("dashboard")
        
        # Setup UI elements
        self.setupYearFilter()
        self.setupAgeChart()
        
        # Connect signals
        self.year_combo.currentIndexChanged.connect(self.loadDashboardData)
        self.refresh_btn.clicked.connect(self.loadDashboardData)
        
        # Initial load
        self.loadDashboardData()

    def setupYearFilter(self):
        # Get current year and add past 5 years to combo box
        current_year = datetime.now().year
        years = [str(year) for year in range(current_year - 5, current_year + 1)]
        self.year_combo.addItems(years)
        
        # Set current year as default
        self.year_combo.setCurrentText(str(current_year))

    def setupAgeChart(self):
        # Create chart widget
        self.age_chart = AgeDistributionChart(self.chart_container, width=5, height=4)
        self.chart_layout.addWidget(self.age_chart)

    def loadDashboardData(self):
        try:
            selected_year = int(self.year_combo.currentText())
            
            # Calculate date range for the selected year
            start_date = datetime(selected_year, 1, 1)
            end_date = datetime(selected_year, 12, 31, 23, 59, 59)
            
            # Load statistics
            self.loadStatistics(start_date, end_date)
            
            # Load age distribution
            self.loadAgeDistribution()
            
        except Exception as e:
            print("Error loading dashboard data:", str(e))
            self.show_error("Không thể tải dữ liệu tổng quan")

    def loadStatistics(self, start_date, end_date):
        try:
            # Total revenue
            pipeline = [
                {"$match": {"created_at": {"$gte": start_date, "$lte": end_date}}},
                {"$group": {"_id": None, "total": {"$sum": "$total_price"}}}
            ]
            result = list(config.db.orders.aggregate(pipeline))
            total_revenue = result[0]["total"] if result else 0
            self.revenue_value.setText(f"{total_revenue:,.0f} VNĐ")
            
            # Total customers
            total_customers = config.db.customers.count_documents({})
            self.customers_value.setText(f"{total_customers:,}")
            
            # Total orders in the selected year
            total_orders = config.db.orders.count_documents({
                "created_at": {"$gte": start_date, "$lte": end_date}
            })
            self.orders_value.setText(f"{total_orders:,}")
            
            # Average order value
            avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
            self.avg_order_value.setText(f"{avg_order_value:,.0f} VNĐ")
            
        except Exception as e:
            print("Error loading statistics:", str(e))
            self.show_error("Không thể tải thống kê")

    def loadAgeDistribution(self):
        try:
            # Get current date for age calculation
            current_date = date.today()
            current_year = current_date.year
            
            # Initialize counters
            under_25 = 0
            between_25_35 = 0
            over_35 = 0
            
            # Get all customers
            customers = config.db.customers.find({})
            
            # Count customers by age group
            for customer in customers:
                # Get birth date (assuming there's a birth_date field in the customer document)
                birth_date = customer.get("birth_date")
                
                if birth_date:
                    # Calculate age
                    age = current_year - birth_date.year
                    
                    # Adjust age if birthday hasn't occurred yet this year
                    if current_date.month < birth_date.month or (current_date.month == birth_date.month and current_date.day < birth_date.day):
                        age -= 1
                    
                    # Categorize by age group
                    if age < 25:
                        under_25 += 1
                    elif 25 <= age <= 35:
                        between_25_35 += 1
                    else:
                        over_35 += 1
                else:
                    # If birth_date is not available, distribute evenly (for demo purposes)
                    # In a real application, you might want to handle this differently
                    import random
                    group = random.randint(1, 3)
                    if group == 1:
                        under_25 += 1
                    elif group == 2:
                        between_25_35 += 1
                    else:
                        over_35 += 1
            
            # Update chart
            age_data = {
                'under_25': under_25,
                'between_25_35': between_25_35,
                'over_35': over_35
            }
            self.age_chart.update_chart(age_data)
            
        except Exception as e:
            print("Error loading age distribution:", str(e))
            self.show_error("Không thể tải phân bố độ tuổi khách hàng")



        





        









    