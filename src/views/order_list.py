from PyQt6 import QtWidgets, QtCore
from datetime import datetime
from .base_window_with_sidebar import BaseWindowWithSidebar
from src.db import config

class OrderList(BaseWindowWithSidebar):
    def __init__(self):
        super(OrderList, self).__init__("order_list")
        
        # Pagination settings
        self.page_size = 20  # Items per page
        self.current_page = 1
        self.total_items = 0
        
        # Setup UI elements
        self.setupTable()
        self.setupSearchAndFilter()
        self.setupPagination()
        
        # Initial load
        self.loadOrders()
        
        # Connect signals
        self.search_input.textChanged.connect(self.onSearchChanged)
        self.search_by_combo.currentIndexChanged.connect(self.onSearchChanged)
        self.sort_order_combo.currentIndexChanged.connect(self.loadOrders)
        self.status_combo.currentIndexChanged.connect(self.loadOrders)
        self.refresh_btn.clicked.connect(self.loadOrders)
        
        # Pagination signals
        self.prev_page_btn.clicked.connect(lambda: self.changePage('prev'))
        self.next_page_btn.clicked.connect(lambda: self.changePage('next'))
        self.page_size_combo.currentIndexChanged.connect(self.onPageSizeChanged)
        
        # Connect double-click signal
        self.orders_table.itemDoubleClicked.connect(self.onOrderDoubleClicked)

    def setupTable(self):
        # Set table headers
        self.orders_table.setColumnCount(6)
        headers = ["ID", "Mã đơn hàng", "Khách hàng", "Ngày đặt",
                  "Tổng tiền", "Trạng thái"]
        self.orders_table.setHorizontalHeaderLabels(headers)
        
        # Set column widths
        self.orders_table.setColumnWidth(0, 100)  # ID
        self.orders_table.setColumnWidth(1, 150)  # Order ID
        self.orders_table.setColumnWidth(2, 200)  # Customer name
        self.orders_table.setColumnWidth(3, 150)  # Order date
        self.orders_table.setColumnWidth(4, 150)  # Total amount
        self.orders_table.setColumnWidth(5, 100)  # Status

        # Hide ID column
        self.orders_table.setColumnHidden(0, True)

        # Make table read-only
        self.orders_table.setEditTriggers(QtWidgets.QTableWidget.EditTrigger.NoEditTriggers)
        
        # Enable alternating row colors
        self.orders_table.setAlternatingRowColors(True)
        
        # Set selection behavior
        self.orders_table.setSelectionBehavior(QtWidgets.QTableWidget.SelectionBehavior.SelectRows)
        self.orders_table.setSelectionMode(QtWidgets.QTableWidget.SelectionMode.SingleSelection)

    def setupSearchAndFilter(self):
        # Setup search by combo box
        search_options = ["Mã đơn hàng", "Tên khách hàng", "Số điện thoại"]
        self.search_by_combo.addItems(search_options)
        
        # Setup sort order combo box
        sort_options = ["Mới nhất", "Cũ nhất"]
        self.sort_order_combo.addItems(sort_options)
        
        # Setup status filter combo box
        status_options = ["Tất cả", "Chờ xử lý", "Đang xử lý", "Hoàn thành", "Đã hủy"]
        self.status_combo.addItems(status_options)

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
        self.prev_page_btn.setEnabled(self.current_page > 1)
        self.next_page_btn.setEnabled(self.current_page < total_pages)

    def changePage(self, action):
        total_pages = (self.total_items + self.page_size - 1) // self.page_size
        
        if action == 'prev':
            self.current_page = max(1, self.current_page - 1)
        elif action == 'next':
            self.current_page = min(total_pages, self.current_page + 1)
        
        self.loadOrders()

    def onPageSizeChanged(self):
        self.page_size = int(self.page_size_combo.currentText())
        self.current_page = 1  # Reset to first page
        self.loadOrders()

    def loadOrders(self):
        try:
            # Build query
            query = {}
            search_text = self.search_input.text().strip()
            
            if search_text:
                search_field = {
                    'Mã đơn hàng': 'order_id',
                    'Tên khách hàng': 'customer_name',
                    'Số điện thoại': 'customer_phone'
                }[self.search_by_combo.currentText()]
                
                query[search_field] = {'$regex': search_text, '$options': 'i'}
            
            # Add status filter
            status_text = self.status_combo.currentText()
            if status_text != "Tất cả":
                status_map = {
                    "Chờ xử lý": "pending",
                    "Đang xử lý": "processing",
                    "Hoàn thành": "completed",
                    "Đã hủy": "cancelled"
                }
                query['status'] = status_map[status_text]
            
            # Get total count for pagination
            self.total_items = config.db.orders.count_documents(query)
            
            # Sort order
            sort_order = -1 if self.sort_order_combo.currentText() == "Mới nhất" else 1
            
            # Calculate skip for pagination
            skip = (self.current_page - 1) * self.page_size
            
            # Get orders with pagination
            orders = config.db.orders.find(query) \
                .sort('created_at', sort_order) \
                .skip(skip) \
                .limit(self.page_size)
            
            # Clear and setup table
            self.orders_table.setRowCount(0)
            
            # Populate table
            for row, order in enumerate(orders):
                self.orders_table.insertRow(row)
                
                # Format date
                date_str = order.get('created_at', datetime.now()).strftime("%d/%m/%Y %H:%M")
                
                # Get status text
                status_text = {
                    'pending': 'Chờ xử lý',
                    'processing': 'Đang xử lý',
                    'completed': 'Hoàn thành',
                    'cancelled': 'Đã hủy'
                }.get(order.get('status', ''), order.get('status', ''))
                
                # Get customer info
                customer = config.get_customer_info(order.get('customer_id'))
                customer_name = customer.get('name', '') if customer else ''
                
                # Prepare items with alignment
                items = [
                    (order.get('_id', ''), QtCore.Qt.AlignmentFlag.AlignCenter),
                    (order.get('order_id', ''), QtCore.Qt.AlignmentFlag.AlignCenter),
                    (customer_name, QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter),
                    (date_str, QtCore.Qt.AlignmentFlag.AlignCenter),
                    (f"{order.get('total_price', 0):,.0f} VNĐ", QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter),
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

    def onOrderDoubleClicked(self, item):
        # Lấy order_id từ cột đầu tiên
        row = item.row()
        order_id = self.orders_table.item(row, 1).text()
        
        # Mở trang chi tiết
        from .order_detail import OrderDetail
        self.navigate_to(OrderDetail, order_id=order_id)

    def onSearchChanged(self):
        """Debounced search"""
        QtCore.QTimer.singleShot(300, self.loadOrders)

    def goBack(self):
        from .dashboard import Dashboard
        self.navigate_to(Dashboard) 