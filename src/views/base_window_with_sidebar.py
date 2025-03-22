from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.uic import loadUi
from .base_window import BaseWindow

class BaseWindowWithSidebar(BaseWindow):
    def __init__(self, ui_name):
        # Load base sidebar UI first
        super(BaseWindow, self).__init__()
        loadUi("ui/base_with_sidebar.ui", self)
        
        # Then load content UI into content_layout
        self.content_widget = QtWidgets.QWidget()
        loadUi(f"ui/{ui_name}.ui", self.content_widget)
        self.content_layout.addWidget(self.content_widget)
        
        # Copy all widgets from content_widget to self for easy access
        for widget_name in self.content_widget.__dict__:
            if not widget_name.startswith('_'):  # Skip private attributes
                setattr(self, widget_name, getattr(self.content_widget, widget_name))
        
        # Setup sidebar
        self.setupSidebar()
        self.connectSidebarSignals()
        
        # Highlight current menu
        self.highlightCurrentMenu()

    def setupSidebar(self):
        # Set icon size
        self.sidebar_list.setIconSize(QtCore.QSize(24, 24))
        
        # Add menu items
        menu_items = [
            {
                'icon': 'icons/dashboard.png',
                'text': 'Tổng quan',
                'view': 'Dashboard'
            },
            {
                'icon': 'icons/users.png',
                'text': 'Người dùng',
                'view': 'CustomerList'
            },
            {
                'icon': 'icons/orders.png',
                'text': 'Đơn hàng',
                'view': 'OrderList'
            },
        ]
        
        for item in menu_items:
            list_item = QtWidgets.QListWidgetItem()
            list_item.setIcon(QtGui.QIcon(item['icon']))
            list_item.setText(item['text'])
            list_item.setData(QtCore.Qt.ItemDataRole.UserRole, item['view'])
            self.sidebar_list.addItem(list_item)
            
        # Update user info
        from src.widget import context
        user = context.get('user', 'Unknown User')
        self.user_name.setText(user)
        self.user_role.setText('Administrator')  # or get from context if you have roles

    def connectSidebarSignals(self):
        self.sidebar_list.itemClicked.connect(self.onMenuItemClicked)
        self.logout_btn.clicked.connect(self.logout)

    def highlightCurrentMenu(self):
        # Get current view name
        current_view = self.__class__.__name__
        
        # Find and highlight the matching item
        for i in range(self.sidebar_list.count()):
            item = self.sidebar_list.item(i)
            if item.data(QtCore.Qt.ItemDataRole.UserRole) == current_view:
                item.setSelected(True)
                break

    def onMenuItemClicked(self, item):
        view_name = item.data(QtCore.Qt.ItemDataRole.UserRole)
        
        # Import the view dynamically
        try:
            if view_name == self.__class__.__name__:
                return  # Already on this view
                
            if view_name == 'Dashboard':
                from .dashboard import Dashboard
                self.navigate_to(Dashboard)
            elif view_name == 'CustomerList':
                from .customer_list import CustomerList
                self.navigate_to(CustomerList)
            elif view_name == 'OrderList':
                from .order_list import OrderList
                self.navigate_to(OrderList)
                
        except Exception as e:
            print(f"Navigation error: {str(e)}")
            self.show_error("Không thể chuyển trang. Vui lòng thử lại.")

    def logout(self):
        from src.widget import context
        context['user'] = None
        context['user_id'] = None
        
        from .login import Login
        self.navigate_to(Login)

    def navigate_to(self, window_class, *args, **kwargs):
        """Safe navigation between windows"""
        try:
            next_window = window_class(*args, **kwargs)
            from src.widget import widget
            widget.addWidget(next_window)
            widget.setCurrentIndex(widget.currentIndex() + 1)
        except Exception as e:
            print(f"Navigation error to {window_class.__name__}: {str(e)}")
            self.show_error("Lỗi chuyển trang. Vui lòng thử lại.") 