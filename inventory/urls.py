from django.urls import path

from . import views

urlpatterns = [
    path('view/', views.inventory_view, name='inventory_view'),
    path('create/', views.inventory_create, name='inventory_create'),
    path('view/<str:activo_codigo>/edit/', views.inventory_edit, name='inventory_edit'),
    path('view/delete/', views.inventory_delete, name='inventory_delete'),
]