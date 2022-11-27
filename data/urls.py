from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('api', views.manage_requests),
    path('admin', views.get_admin_data),
    path('normal_user/', views.get_normal_user_data),
    path('set_value', views.set_value_transaction),
    path('blockchain/', views.get_blockchain_data)
]