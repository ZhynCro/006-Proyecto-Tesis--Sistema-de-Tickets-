from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render

# Create your views here.

def main(request):
    return render(request, 'base.html')

def login_vista(request):
    if request.method == 'POST':
        id_empleado = request.POST.get('ID_empleado', '').strip()

        if not id_empleado:
            messages.error(request, 'Debes ingresar un ID de empleado.')
            return render(request, 'login.html')

        request.session['ID_empleado'] = id_empleado
        messages.success(request, 'ID de empleado registrado correctamente.')
        return redirect('main')
    return render(request, 'login.html')

def admin_login_vista(request):
    if request.method == 'POST':
        id_empleado = request.POST.get('ID_empleado', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, ID_empleado=id_empleado, password=password)

        if user is None:
            messages.error(request, 'Credenciales administrativas inválidas.')
            return render(request, 'login_admin.html')

        login(request, user)
        messages.success(request, 'Inicio de sesión administrativo exitoso.')
        return redirect('main')

    return render(request, 'login_admin.html')