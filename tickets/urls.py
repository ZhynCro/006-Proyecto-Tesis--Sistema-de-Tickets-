from django.urls import path
from . import views

urlpatterns = [
    path('view/', views.tickets_view, name='tickets_view'),
    path('my_tickets/', views.tickets_view_self, name='tickets_view_self'),
    path('pending/', views.tickets_view_pending, name='tickets_view_pending'),
    path('create/', views.tickets_create, name='tickets_create'),
    path('view/<int:ticket_id>/edit/', views.tickets_edit, name='tickets_edit'),
    path('delete/', views.tickets_delete, name='tickets_delete'),
]