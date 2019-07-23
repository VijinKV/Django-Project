from . import views
from django.urls import path

urlpatterns = [
    path('', views.wishListPage,name='wishlist'),
    path('stock_detail', views.stockDetailPage,name='stock-detail'),
    path('about', views.aboutPage,name='blog-about'),
    path('stock_add_menu', views.addStockPage,name='add-stock-page'),
    path('delete_stock', views.deleteStock,name='delete-stock'),
    path('addStock', views.addStock,name='add-stock'),

]
