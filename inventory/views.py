from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from inventory.forms import ActivoCreationForm, ActivoUpdateForm
from inventory.models import activos


@login_required
def inventory_view(request):
    activos_registrados = (
        activos.objects.select_related('categoria', 'sede', 'usuario_asignado', 'departamento')
        .filter(estado__iexact='activo')
        .order_by('codigo')
    )
    paginator = Paginator(activos_registrados, 50)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'inventory_view.html', {'activos': page_obj, 'page_obj': page_obj})

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