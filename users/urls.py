from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, name='main'),
    path('login/', views.login_view, name='login'),
]

"""     path('create/', views.crearUsuario, name='crear_usuario'),
    path('login/', views.loginUsuario, name='login_usuario'), """