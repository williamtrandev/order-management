from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QTableWidgetItem
from PyQt6.uic import loadUi
from src.db import config
from src.widget import context

class FavoriteProducts(QtWidgets.QMainWindow):
    def __init__(self):
        super(FavoriteProducts, self).__init__()
        loadUi("ui/favorite_products.ui", self)
        
        self.loadFavorites()
        self.refresh_btn.clicked.connect(self.loadFavorites)
        self.back_btn.clicked.connect(self.goBack)
        
    def loadFavorites(self):
        user_id = context['user_id']
        user = config.db.users.find_one({'_id': user_id})
        favorite_products = user.get('favorite_products', [])
        
        products = config.db.products.find({
            '_id': {'$in': favorite_products}
        })
        
        self.products_table.setRowCount(0)
        for row, product in enumerate(products):
            self.products_table.insertRow(row)
            self.products_table.setItem(row, 0, QTableWidgetItem(product['name']))
            self.products_table.setItem(row, 1, QTableWidgetItem(product['category']))
            self.products_table.setItem(row, 2, QTableWidgetItem(str(product['stock'])))
    
    def goBack(self):
        from src.views.dashboard import Dashboard
        dashboard = Dashboard()
        self.widget.addWidget(dashboard)
        self.widget.setCurrentIndex(self.widget.currentIndex()+1) 