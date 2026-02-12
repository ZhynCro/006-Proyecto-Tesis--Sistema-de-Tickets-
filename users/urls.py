from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('admin-login/', views.admin_login_view, name='admin_login'),
    path('logout/', views.logout_view, name='logout'),
    path('create/', views.user_create, name='user_create'),
    path('view/', views.user_view, name='user_view'),
    path('view/<int:user_id>/edit/', views.user_edit, name='user_edit'),
    path('view/delete/', views.user_delete, name='user_delete'),
    ]