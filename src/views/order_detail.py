from PyQt6 import QtWidgets, QtCore
from datetime import datetime
from .base_window_with_sidebar import BaseWindowWithSidebar
from src.db import config

class OrderDetail(BaseWindowWithSidebar):
    def __init__(self, order_id=None):
        super(OrderDetail, self).__init__("order_detail")
        self.order_id = order_id
        
        # Setup UI elements
        self.setupTable()
        
        # Initial load
        self.loadOrderInfo()
        self.loadOrderItems()
        
        # Connect signals
        self.back_btn.clicked.connect(self.goBack)

    def setupTable(self):
        # Set table headers
        self.items_table.setColumnCount(5)
        headers = ["Mã sản phẩm", "Tên sản phẩm", "Số lượng",
                  "Đơn giá", "Thành tiền"]
        self.items_table.setHorizontalHeaderLabels(headers)
        
        # Set column widths
        self.items_table.setColumnWidth(0, 150)  # Product ID
        self.items_table.setColumnWidth(1, 300)  # Product name
        self.items_table.setColumnWidth(2, 100)  # Quantity
        self.items_table.setColumnWidth(3, 150)  # Unit price
        self.items_table.setColumnWidth(4, 150)  # Total price

        # Make table read-only
        self.items_table.setEditTriggers(QtWidgets.QTableWidget.EditTrigger.NoEditTriggers)
        
        # Enable alternating row colors
        self.items_table.setAlternatingRowColors(True)
        
        # Set selection behavior
        self.items_table.setSelectionBehavior(QtWidgets.QTableWidget.SelectionBehavior.SelectRows)
        self.items_table.setSelectionMode(QtWidgets.QTableWidget.SelectionMode.SingleSelection)

    def loadOrderInfo(self):
        try:
            if not self.order_id:
                return

            # Get order info from database
            order = config.get_order_info(self.order_id)

            if not order:
                self.show_error("Không tìm thấy thông tin đơn hàng")
                return
                
            # Format date
            date_str = order['created_at'].strftime("%d/%m/%Y %H:%M")
            
            # Get status text
            status_text = {
                'pending': 'Chờ xử lý',
                'processing': 'Đang xử lý',
                'completed': 'Hoàn thành',
                'cancelled': 'Đã hủy'
            }.get(order['status'], order['status'])
            
            # Update labels
            self.order_id_label.setText(f"Mã đơn hàng: {order['id']}")
            self.order_date_label.setText(f"Ngày đặt: {date_str}")
            self.customer_name_label.setText(f"Khách hàng: {order['customer_name']}")
            self.status_label.setText(f"Trạng thái: {status_text}")
            self.total_amount_label.setText(f"Tổng tiền: {order['total_price']:,.0f} VNĐ")
            self.note_label.setText(f"Ghi chú: {order.get('note', '')}")
            
        except Exception as e:
            print("Error loading order info:", str(e))
            self.show_error("Không thể tải thông tin đơn hàng")

    def loadOrderItems(self):
        try:
            if not self.order_id:
                return
                
            # Get order items
            items = config.get_order_items(self.order_id)
            
            # Clear and setup table
            self.items_table.setRowCount(0)
            
            # Populate table
            for row, item in enumerate(items):
                self.items_table.insertRow(row)
                
                # Calculate total price
                total_price = item['quantity'] * item['unit_price']
                
                # Prepare items with alignment
                items = [
                    (item['product_id'], QtCore.Qt.AlignmentFlag.AlignCenter),
                    (item['product_name'], QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter),
                    (str(item['quantity']), QtCore.Qt.AlignmentFlag.AlignCenter),
                    (f"{item['unit_price']:,.0f} VNĐ", QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter),
                    (f"{total_price:,.0f} VNĐ", QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter)
                ]
                
                # Set table items with alignment
                for col, (item_text, alignment) in enumerate(items):
                    table_item = QtWidgets.QTableWidgetItem(str(item_text))
                    table_item.setTextAlignment(alignment)
                    self.items_table.setItem(row, col, table_item)
            
            # Auto-resize rows
            self.items_table.resizeRowsToContents()
            
        except Exception as e:
            print("Error loading order items:", str(e))
            self.show_error("Không thể tải danh sách sản phẩm")

    def goBack(self):
        from .order_list import OrderList
        self.navigate_to(OrderList) 