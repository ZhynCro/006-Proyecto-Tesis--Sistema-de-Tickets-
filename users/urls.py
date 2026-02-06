from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, name='main'),
    path('login/', views.login_view, name='login'),
    path('admin-login/', views.admin_login_view, name='admin_login'),
    path('logout/', views.logout_view, name='logout'),
    path('create/', views.user_create, name='user_create'),
    path('view/', views.user_view, name='user_view'),
    path('view/<int:user_id>/edit/', views.user_edit, name='user_edit'),
    ]