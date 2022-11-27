from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page),
    path('user/login/', views.login_page),
    path('user/create_user/', views.register),
    path('user/logout', views.logout_page),
    path('user/account', views.account),
    path('user/delete', views.remove_account)
]