from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, name='main'),
    path('login/', views.login_vista, name='login'),
    path('admin-login/', views.admin_login_vista, name='admin_login'),
]

"""     path('create/', views.crearUsuario, name='crear_usuario'),
    path('login/', views.loginUsuario, name='login_usuario'), """