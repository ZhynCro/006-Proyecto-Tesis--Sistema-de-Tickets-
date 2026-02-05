from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, name='main'),

]

"""     path('create/', views.crearUsuario, name='crear_usuario'),
    path('login/', views.loginUsuario, name='login_usuario'), """