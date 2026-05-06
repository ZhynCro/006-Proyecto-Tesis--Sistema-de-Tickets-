from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.conf import settings

from inventory.forms import ActivoCreationForm, ActivoUpdateForm
from inventory.models import activos, activos_categoria
from users.models import usuario, sede, departamento


@login_required
def inventory_view(request):
    q = request.GET.get('q', '').strip()
    modelo = request.GET.get('modelo', '').strip()
    usuario_filtro = request.GET.get('usuario', '').strip()
    categoria_filtro = request.GET.get('categoria', '').strip()
    sede_filtro = request.GET.get('sede', '').strip()
    departamento_filtro = request.GET.get('departamento', '').strip()

    activos_list = (
        activos.objects
        .select_related('categoria', 'sede', 'usuario_asignado', 'departamento')
        .filter(estado__iexact='activo')
        .order_by('codigo')
    )

    if q:
        activos_list = activos_list.filter(
            Q(codigo__icontains=q) | Q(serial__icontains=q)
        )

    if modelo:
        activos_list = activos_list.filter(modelo=modelo)

    if usuario_filtro:
        activos_list = activos_list.filter(usuario_asignado_id=usuario_filtro)

    if categoria_filtro:
        activos_list = activos_list.filter(categoria__nombre=categoria_filtro)

    if sede_filtro:
        activos_list = activos_list.filter(sede__codigo=sede_filtro)

    if departamento_filtro:
        activos_list = activos_list.filter(departamento__codigo=departamento_filtro)

    modelos = activos.objects.values_list('modelo', flat=True).distinct().order_by()
    usuarios = usuario.objects.filter(is_active=True).order_by('first_name', 'last_name', 'ID_empleado')
    categorias = activos_categoria.objects.order_by('nombre')
    sedes = sede.objects.order_by('nombre')
    departamentos = departamento.objects.order_by('nombre')

    filtros_activos = sum([1 for x in [q, modelo, usuario_filtro, categoria_filtro, sede_filtro, departamento_filtro] if x])

    filtros = {
        'q': q,
        'modelo': modelo,
        'usuario': usuario_filtro,
        'categoria': categoria_filtro,
        'sede': sede_filtro,
        'departamento': departamento_filtro,
    }

    paginator = Paginator(activos_list, settings.PAGINATION_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'inventory_view.html', {
        'activos': page_obj,
        'page_obj': page_obj,
        'modelos': modelos,
        'usuarios': usuarios,
        'categorias': categorias,
        'sedes': sedes,
        'departamentos': departamentos,
        'filtros': filtros,
        'filtros_activos': filtros_activos,
    })

@login_required
def inventory_create(request):
    if request.method == 'POST':
        form = ActivoCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Activo creado correctamente.')
            return redirect('inventory_view')
    else:
        form = ActivoCreationForm()

    return render(request, 'inventory_create.html', {'form': form})

@login_required
def inventory_edit(request, activo_codigo):
    activo = get_object_or_404(activos, pk=activo_codigo)

    if request.method == 'POST':
        form = ActivoUpdateForm(request.POST, instance=activo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Activo actualizado correctamente.')
            return redirect('inventory_view')
    else:
        form = ActivoUpdateForm(instance=activo)

    return render(request, 'inventory_edit.html', {'form': form, 'activo': activo})

@login_required
def inventory_delete(request):
    if request.method != 'POST':
        return redirect('inventory_view')

    activos_seleccionados = request.POST.getlist('activos_seleccionados')

    if not activos_seleccionados:
        messages.error(request, 'No se seleccionó ningún activo para eliminar.')
        return redirect('inventory_view')

    filas_actualizadas = activos.objects.filter(codigo__in=activos_seleccionados).update(estado='inactivo')

    if filas_actualizadas > 0:
        messages.success(request, 'Activos desactivados correctamente.')
    else:
        messages.error(request, 'No se encontraron activos para desactivar.')

    return redirect('inventory_view')