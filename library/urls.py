from django.urls import path

from . import views

urlpatterns = [
    path('view/', views.library_view, name='library_view'),
    path('create/', views.library_create, name='library_create'),
    path('view/<int:tutorial_id>/edit/', views.library_edit, name='library_edit'),
    path('view/delete/', views.library_delete, name='library_delete'),
    path('view/<int:tutorial_id>/download/', views.library_download, name='library_download'),
]
