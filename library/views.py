from django.shortcuts import get_object_or_404, redirect, render
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404, HttpResponse


from .forms import TutorialForm
from .models import Tutorial

import os
# Create your views here.



@login_required
def library_view(request):
    tutoriales = Tutorial.objects.all().order_by('-creado_en')
    return render(request, 'library_view.html', {'tutoriales': tutoriales})


@login_required
def library_create(request):
    if request.method == 'POST':
        form = TutorialForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Documento cargado correctamente.')
            return redirect('library_view')
    else:
        form = TutorialForm()

    return render(request, 'library_create.html', {'form': form})


@login_required
def library_edit(request, tutorial_id):
    tutorial = get_object_or_404(Tutorial, pk=tutorial_id)

    if request.method == 'POST':
        form = TutorialForm(request.POST, request.FILES, instance=tutorial)
        if form.is_valid():
            form.save()
            messages.success(request, 'Documento actualizado correctamente.')
            return redirect('library_view')
    else:
        form = TutorialForm(instance=tutorial)

    return render(request, 'library_edit.html', {'form': form, 'tutorial': tutorial})


@login_required
def library_delete(request):
    if request.method != 'POST':
        return redirect('library_view')

    tutoriales_seleccionados = request.POST.getlist('tutoriales_seleccionados')

    if not tutoriales_seleccionados:
        messages.error(request, 'No se seleccionó ningún documento para eliminar.')
        return redirect('library_view')

    borrados, _ = Tutorial.objects.filter(id__in=tutoriales_seleccionados).delete()

    if borrados > 0:
        messages.success(request, 'Documentos eliminados correctamente.')
    else:
        messages.error(request, 'No se encontraron documentos para eliminar.')

    return redirect('library_view')


@login_required
def library_download(request, tutorial_id):
    tutorial = get_object_or_404(Tutorial, pk=tutorial_id)

    if not tutorial.archivo:
        raise Http404('No existe archivo asociado.')


    if getattr(settings, 'USE_X_SENDFILE', False):
        response = HttpResponse(content_type=tutorial.mime_type)
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(tutorial.nombre_original)}"'
        response['X-Sendfile'] = tutorial.archivo.path
        return response

    file_handle = tutorial.archivo.open('rb')
    response = FileResponse(file_handle, content_type=tutorial.mime_type)
    response['Content-Disposition'] = f'attachment; filename="{os.path.basename(tutorial.nombre_original)}"'
    return response