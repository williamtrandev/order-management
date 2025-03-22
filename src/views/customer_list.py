from PyQt6 import QtWidgets, QtCore
from datetime import datetime
from .base_window_with_sidebar import BaseWindowWithSidebar
from src.db import config

class CustomerList(BaseWindowWithSidebar):
    def __init__(self):
        super(CustomerList, self).__init__("customer_list")
        
        # Pagination settings
        self.page_size = 20  # Items per page
        self.current_page = 1
        self.total_items = 0
        
        # Setup UI elements
        self.setupTable()
        self.setupSearchAndFilter()
        self.setupPagination()
        
        # Initial load
        self.loadCustomers()
        
        # Connect signals
        self.search_input.textChanged.connect(self.onSearchChanged)
        self.search_by_combo.currentIndexChanged.connect(self.onSearchChanged)
        self.sort_order_combo.currentIndexChanged.connect(self.loadCustomers)
        self.refresh_btn.clicked.connect(self.loadCustomers)
        
        # Pagination signals
        self.prev_page_btn.clicked.connect(lambda: self.changePage('prev'))
        self.next_page_btn.clicked.connect(lambda: self.changePage('next'))
        self.page_size_combo.currentIndexChanged.connect(self.onPageSizeChanged)
        
        # Connect double-click signal
        self.customers_table.itemDoubleClicked.connect(self.onCustomerDoubleClicked)

    def setupTable(self):
        # Set table headers
        self.customers_table.setColumnCount(7)
        headers = ["ID", "Họ và tên", "Email", "Số điện thoại",
                  "Địa chỉ", "Ngày tạo", "Tổng chi tiêu"]
        self.customers_table.setHorizontalHeaderLabels(headers)
        
        # Set column widths
        self.customers_table.setColumnWidth(0, 100)  # ID
        self.customers_table.setColumnWidth(1, 200)  # Username
        self.customers_table.setColumnWidth(2, 250)  # Email
        self.customers_table.setColumnWidth(3, 150)  # Phone
        self.customers_table.setColumnWidth(4, 300)  # Address
        self.customers_table.setColumnWidth(5, 150)  # Created date
        self.customers_table.setColumnWidth(6, 180)  # Total spent

        # Hide ID column
        self.customers_table.setColumnHidden(0, True)

        # Make table read-only
        self.customers_table.setEditTriggers(QtWidgets.QTableWidget.EditTrigger.NoEditTriggers)
        
        # Enable alternating row colors
        self.customers_table.setAlternatingRowColors(True)
        
        # Set selection behavior
        self.customers_table.setSelectionBehavior(QtWidgets.QTableWidget.SelectionBehavior.SelectRows)
        self.customers_table.setSelectionMode(QtWidgets.QTableWidget.SelectionMode.SingleSelection)

    def setupSearchAndFilter(self):
        # Setup search by combo box
        search_options = ["Họ và tên", "Email", "Số điện thoại", "Địa chỉ"]
        self.search_by_combo.addItems(search_options)
        
        # Setup sort order combo box
        sort_options = ["Mới nhất", "Cũ nhất"]
        self.sort_order_combo.addItems(sort_options)

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
        
        self.loadCustomers()

    def onPageSizeChanged(self):
        self.page_size = int(self.page_size_combo.currentText())
        self.current_page = 1  # Reset to first page
        self.loadCustomers()

    def loadCustomers(self):
        try:
            # Build query
            query = {}
            search_text = self.search_input.text().strip()
            
            if search_text:
                search_field = {
                    'Họ và tên': 'name',
                    'Email': 'email',
                    'Số điện thoại': 'phone',
                    'Địa chỉ': 'address'
                }[self.search_by_combo.currentText()]
                
                query[search_field] = {'$regex': search_text, '$options': 'i'}
            
            # Get total count for pagination
            self.total_items = config.db.customers.count_documents(query)
            
            # Sort order
            sort_order = -1 if self.sort_order_combo.currentText() == "Mới nhất" else 1
            
            # Calculate skip for pagination
            skip = (self.current_page - 1) * self.page_size
            
            # Get customers with pagination
            users = config.db.customers.find(query) \
                .sort('created_at', sort_order) \
                .skip(skip) \
                .limit(self.page_size)
            
            # Clear and setup table
            self.customers_table.setRowCount(0)
            
            # Populate table
            for row, user in enumerate(users):
                self.customers_table.insertRow(row)
                
                # Format date
                created_date = user.get('created_at', datetime.now())
                date_str = created_date.strftime("%d/%m/%Y %H:%M")
                
                # Calculate total spent from orders
                total_spent = 0
                orders = config.db.orders.find({'user_id': str(user['_id'])})
                for order in orders:
                    total_spent += order.get('total_amount', 0)
                
                # Prepare items with alignment
                items = [
                    (user.get('customer_id', ''), QtCore.Qt.AlignmentFlag.AlignCenter),
                    (user.get('name', ''), QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter),
                    (user.get('email', ''), QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter),
                    (user.get('phone', ''), QtCore.Qt.AlignmentFlag.AlignCenter),
                    (user.get('address', ''), QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter),
                    (date_str, QtCore.Qt.AlignmentFlag.AlignCenter),
                    (f"{total_spent:,.0f} VNĐ", QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter)
                ]
                
                # Set table items with alignment
                for col, (item, alignment) in enumerate(items):
                    table_item = QtWidgets.QTableWidgetItem(str(item))
                    table_item.setTextAlignment(alignment)
                    self.customers_table.setItem(row, col, table_item)
            
            # Auto-resize rows
            self.customers_table.resizeRowsToContents()
            
            # Update pagination
            self.updatePaginationButtons()
            
            # Update status with pagination info
            start_item = (self.current_page - 1) * self.page_size + 1
            end_item = min(start_item + self.page_size - 1, self.total_items)
            self.status_label.setText(
                f"Hiển thị {start_item:,}-{end_item:,} trên tổng số {self.total_items:,} người dùng"
            )
            
        except Exception as e:
            print("Error loading users:", str(e))
            self.show_error("Không thể tải danh sách người dùng")

    def onCustomerDoubleClicked(self, item):
        # Lấy customer_id từ cột đầu tiên
        row = item.row()
        customer_id = self.customers_table.item(row, 0).text()
        
        # Mở trang chi tiết
        from .customer_detail import CustomerDetail
        self.navigate_to(CustomerDetail, customer_id=customer_id)

    def onSearchChanged(self):
        """Debounced search"""
        QtCore.QTimer.singleShot(300, self.loadCustomers)

    def goBack(self):
        from .dashboard import Dashboard
        self.navigate_to(Dashboard) 