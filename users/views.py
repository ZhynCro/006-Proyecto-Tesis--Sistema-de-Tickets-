from django.contrib import messages
from django.contrib.auth import authenticate, login, get_user_model, logout
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.core.paginator import Paginator

from users.forms import UsuarioCreationForm, UsuarioUpdateForm
from .models import usuario

# Create your views here.

def index(request):
    if request.user.is_authenticated:
        return redirect('user_view') # Nombre de tu ruta de inicio
    return redirect('login')

@login_required
def logout_view(request):
    try:
        del request.session['ID_empleado']
    except KeyError:
        pass
    
    request.session.pop('admin_login', None)
    logout(request)
    return redirect('login')


def login_view(request):
    if request.method == 'POST':
        id_empleado = request.POST.get('ID_empleado', '').strip()

        if not id_empleado:
            messages.error(request, 'Debes ingresar un ID de empleado.')
            return render(request, 'login.html')

        if usuario.objects.filter(ID_empleado=id_empleado).exists():
            request.session['ID_empleado'] = id_empleado
            request.session['admin_login'] = False
            return redirect('tickets_create')
        else:
            messages.error(request, 'ID de empleado no encontrado. Verifique la información ingresada.')
            return render(request, 'login.html')

    return render(request, 'login.html')

def admin_login_view(request):
    if request.method == 'POST':
        id_empleado = request.POST.get('ID_empleado', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, ID_empleado=id_empleado, password=password)

        if user is None:
            messages.error(request, 'Usuario o clave invalido.')
            return render(request, 'login_admin.html')

        login(request, user)
        request.session['admin_login'] = True
        return redirect('dashboard_view')

    return render(request, 'login_admin.html')

@login_required
def user_create (request):
    if request.method == 'POST':
        form = UsuarioCreationForm(request.POST)
        if form.is_valid():
            try:
                form.save()
            except IntegrityError:
                form.add_error('ID_empleado', 'Ya existe un usuario con este ID de empleado.')
            else:
                messages.success(request, 'Usuario creado correctamente.')
                return redirect('user_view')
    else:
        form = UsuarioCreationForm()

    return render(request, 'user_create.html', {'form': form})

@login_required
def user_view(request):
    user_model = get_user_model()
    usuarios = (
        user_model.objects.select_related('departamento', 'sede')
        .prefetch_related('groups')
        .filter(is_active=True)
        .order_by('ID_empleado')
    )
    paginator = Paginator(usuarios, 50)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'user_view.html', {'usuarios': page_obj, 'page_obj': page_obj})

@login_required
def user_edit(request, user_id):
    user_model = get_user_model()
    usuario = get_object_or_404(user_model, pk=user_id)

    if request.method == 'POST':
        form = UsuarioUpdateForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario actualizado correctamente.')
            return redirect('user_view')
    else:
        form = UsuarioUpdateForm(instance=usuario)

    return render(request, 'user_edit.html', {'form': form, 'usuario': usuario})

@login_required
def user_delete(request):
    if request.method != 'POST':
        return redirect('user_view')
    
    usuarios_seleccionados = request.POST.getlist('usuarios_seleccionados')

    if not usuarios_seleccionados:
        messages.error(request, 'No se seleccionó ningún usuario para eliminar.')
        return redirect('user_view')
    
    user_model = get_user_model()
    filas_borradas = user_model.objects.filter(id__in=usuarios_seleccionados).update(is_active=False)

    if filas_borradas > 0:
        messages.success(request, 'Usuarios eliminados correctamente.')
    else:
        messages.error(request, 'No se encontraron usuarios para borrar.')

    return redirect('user_view')

