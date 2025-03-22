from PyQt6 import QtWidgets, QtCore
from datetime import datetime
from .base_window_with_sidebar import BaseWindowWithSidebar
from src.db import config

class CustomerDetail(BaseWindowWithSidebar):
    def __init__(self, customer_id=None):
        super(CustomerDetail, self).__init__("customer_detail")
        self.customer_id = customer_id
        
        # Pagination settings
        self.page_size = 20  # Items per page
        self.current_page = 1
        self.total_items = 0
        
        # Setup UI elements
        self.setupTable()
        self.setupPagination()
        
        # Initial load
        self.loadCustomerInfo()
        self.loadOrders()
        
        # Connect signals
        self.refresh_btn.clicked.connect(self.refreshData)
        self.back_btn.clicked.connect(self.goBack)
        
        # Pagination signals
        self.first_page_btn.clicked.connect(lambda: self.changePage('first'))
        self.prev_page_btn.clicked.connect(lambda: self.changePage('prev'))
        self.next_page_btn.clicked.connect(lambda: self.changePage('next'))
        self.last_page_btn.clicked.connect(lambda: self.changePage('last'))
        self.page_size_combo.currentIndexChanged.connect(self.onPageSizeChanged)

    def setupTable(self):
        # Set table headers
        self.orders_table.setColumnCount(4)
        headers = ["Mã đơn hàng", "Ngày đặt", "Tổng tiền",
                  "Trạng thái"]
        self.orders_table.setHorizontalHeaderLabels(headers)
        
        # Set column widths
        self.orders_table.setColumnWidth(0, 150)  # Order ID
        self.orders_table.setColumnWidth(1, 150)  # Order date
        self.orders_table.setColumnWidth(2, 150)  # Total amount
        self.orders_table.setColumnWidth(3, 100)  # Status

        # Make table read-only
        self.orders_table.setEditTriggers(QtWidgets.QTableWidget.EditTrigger.NoEditTriggers)
        
        # Enable alternating row colors
        self.orders_table.setAlternatingRowColors(True)
        
        # Set selection behavior
        self.orders_table.setSelectionBehavior(QtWidgets.QTableWidget.SelectionBehavior.SelectRows)
        self.orders_table.setSelectionMode(QtWidgets.QTableWidget.SelectionMode.SingleSelection)

    def setupPagination(self):
        # Setup page size combo
        page_sizes = ["20", "50", "100"]
        self.page_size_combo.addItems(page_sizes)
        
        # Initial button states
        self.updatePaginationButtons()

    def updatePaginationButtons(self):
        # Calculate total pages
        total_pages = (self.total_items + self.page_size - 1) // self.page_size
        
        # Update page display
        self.page_label.setText(f"Trang {self.current_page}/{total_pages}")
        
        # Update button states
        self.first_page_btn.setEnabled(self.current_page > 1)
        self.prev_page_btn.setEnabled(self.current_page > 1)
        self.next_page_btn.setEnabled(self.current_page < total_pages)
        self.last_page_btn.setEnabled(self.current_page < total_pages)

    def changePage(self, action):
        total_pages = (self.total_items + self.page_size - 1) // self.page_size
        
        if action == 'first':
            self.current_page = 1
        elif action == 'prev':
            self.current_page = max(1, self.current_page - 1)
        elif action == 'next':
            self.current_page = min(total_pages, self.current_page + 1)
        elif action == 'last':
            self.current_page = total_pages
        
        self.loadOrders()

    def onPageSizeChanged(self):
        self.page_size = int(self.page_size_combo.currentText())
        self.current_page = 1  # Reset to first page
        self.loadOrders()

    def loadCustomerInfo(self):
        try:
            if not self.customer_id:
                return

            # Get customer info from database
            customer = config.get_customer_info(self.customer_id)

            if not customer:
                self.show_error("Không tìm thấy thông tin khách hàng")
                return
                
            # Format date
            date_str = customer['created_at'].strftime("%d/%m/%Y %H:%M")
            
            # Update labels
            self.name_label.setText(f"Họ và tên: {customer['name']}")
            self.email_label.setText(f"Email: {customer['email']}")
            self.phone_label.setText(f"Số điện thoại: {customer['phone']}")
            self.address_label.setText(f"Địa chỉ: {customer['address']}")
            self.created_date_label.setText(f"Ngày tạo: {date_str}")
            self.total_spent_label.setText(f"Tổng chi tiêu: {customer['total_spent']:,.0f} VNĐ")
            
        except Exception as e:
            print("Error loading customer info:", str(e))
            self.show_error("Không thể tải thông tin khách hàng")

    def loadOrders(self):
        try:
            if not self.customer_id:
                return
                
            # Get orders with pagination
            result = config.get_customer_orders(
                self.customer_id,
                page=self.current_page,
                page_size=self.page_size
            )
            
            orders = result['orders']
            self.total_items = result['total_count']
            
            # Clear and setup table
            self.orders_table.setRowCount(0)
            
            # Populate table
            for row, order in enumerate(orders):
                self.orders_table.insertRow(row)
                
                # Format date
                date_str = order['created_at'].strftime("%d/%m/%Y %H:%M")

                # Get status text
                status_text = {
                    'pending': 'Chờ xử lý',
                    'processing': 'Đang xử lý',
                    'completed': 'Hoàn thành',
                    'cancelled': 'Đã hủy'
                }.get(order['status'], order['status'])
                
                # Prepare items with alignment
                items = [
                    (order['id'], QtCore.Qt.AlignmentFlag.AlignCenter),
                    (date_str, QtCore.Qt.AlignmentFlag.AlignCenter),
                    (f"{order['total_price']:,.0f} VNĐ", QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter),
                    (status_text, QtCore.Qt.AlignmentFlag.AlignCenter)
                ]
                
                # Set table items with alignment
                for col, (item, alignment) in enumerate(items):
                    table_item = QtWidgets.QTableWidgetItem(str(item))
                    table_item.setTextAlignment(alignment)
                    self.orders_table.setItem(row, col, table_item)
            
            # Auto-resize rows
            self.orders_table.resizeRowsToContents()
            
            # Update pagination
            self.updatePaginationButtons()
            
            # Update status with pagination info
            start_item = (self.current_page - 1) * self.page_size + 1
            end_item = min(start_item + self.page_size - 1, self.total_items)
            self.status_label.setText(
                f"Hiển thị {start_item:,}-{end_item:,} trên tổng số {self.total_items:,} đơn hàng"
            )
            
        except Exception as e:
            print("Error loading orders:", str(e))
            self.show_error("Không thể tải danh sách đơn hàng")

    def refreshData(self):
        """Refresh both customer info and orders"""
        self.loadCustomerInfo()
        self.loadOrders()

    def goBack(self):
        from .customer_list import CustomerList
        self.navigate_to(CustomerList) 