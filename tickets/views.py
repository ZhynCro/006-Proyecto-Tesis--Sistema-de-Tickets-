from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from tickets.forms import TicketCreationForm, TicketUpdateForm
from tickets.models import tickets, matriz_prioridad, tickets_historial
from users.models import usuario
from django.utils import timezone

def _get_current_usuario(request):
    id_empleado = request.session.get('ID_empleado')
    if id_empleado:
        return usuario.objects.filter(ID_empleado=id_empleado, is_active=True).first()

    if request.user.is_authenticated:
        return request.user

    return None

def _next_ticket_code():
    ultimo_ticket = tickets.objects.order_by('-id').first()
    siguiente = 1 if ultimo_ticket is None else ultimo_ticket.id + 1
    return f'TKT-{siguiente:05d}'

def _save_historial_ticket(ticket_id, form, request):
    ticket_actual = tickets.objects.get(pk=ticket_id)
    historial = tickets_historial(
        estado_anterior=ticket_actual.estado,
        estado_nuevo=form.cleaned_data['estado'],
        fecha_cambio=form.cleaned_data.get('fecha_resolucion') or timezone.now(),
        responsable=_get_current_usuario(request),
        ticket_id=ticket_actual,
    )
    historial.save()
    return None

def tickets_view(request):
    tickets_registrados = tickets.objects.select_related('activo_afectado', 'prioridad', 'solicitante', 'usuario').order_by(
        '-fecha_creacion'
    )

    # filtros enviados desde el formulario
    estado = request.GET.get('estado', '').strip()
    usuario_asignado = request.GET.get('usuario_asignado', '').strip()
    prioridad = request.GET.get('prioridad', '').strip()

    # aplicar filtros a la consulta
    if estado:
        tickets_registrados = tickets_registrados.filter(estado=estado)

    if usuario_asignado:
        tickets_registrados = tickets_registrados.filter(usuario_id=usuario_asignado)

    if prioridad:
        tickets_registrados = tickets_registrados.filter(prioridad_id=prioridad)

    # mantiene esos filtros seleccionados en el formulario
    filtros = {
        'estado': estado,
        'usuario_asignado': usuario_asignado,
        'prioridad': prioridad,
    }

    # prepara el contexto completo para la plantilla, incluyendo los tickets filtrados y las opciones para los filtros
    contexto = {
        'tickets': tickets_registrados,
        'estados': tickets.ESTADO_TYPES,
        'usuarios_asignados': usuario.objects.filter(is_active=True).order_by('first_name', 'last_name', 'ID_empleado'),
        'prioridades': matriz_prioridad.objects.order_by('prioridad'),
        'filtros': filtros,
    }

    return render(request, 'tickets_view.html', contexto)

def tickets_view_self(request):
    current_user = _get_current_usuario(request)
    tickets_asignados = tickets.objects.none()
    if current_user:
        tickets_asignados = tickets.objects.select_related('activo_afectado', 'prioridad', 'solicitante', 'usuario').filter(
            usuario=current_user, estado__iexact='pendiente'
        ).order_by('-fecha_creacion')

    return render(request, 'tickets_view_self.html', {'tickets': tickets_asignados})

def tickets_view_pending(request):
    tickets_pendientes = tickets.objects.select_related('activo_afectado', 'prioridad', 'solicitante', 'usuario').filter(
        estado__iexact='pendiente'
    ).order_by('-fecha_creacion')

    return render(request, 'tickets_view_pending.html', {'tickets': tickets_pendientes})

def tickets_create(request):
    current_user = _get_current_usuario(request)

    if not current_user:
        messages.error(request, 'No se pudo identificar al solicitante del ticket.')
        return redirect('login')

    if request.method == 'POST':
        form = TicketCreationForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.codigo_ticket = _next_ticket_code()
            ticket.estado = 'Pendiente'
            ticket.prioridad_id = 'N/A'
            ticket.solicitante = current_user
            ticket.usuario = None
            ticket.fecha_resolucion = None
            ticket.save()

            messages.success(request, 'Ticket creado correctamente.')
            return redirect('tickets_view')
    else:
        form = TicketCreationForm()

    return render(request, 'tickets_create.html', {'form': form})


def tickets_edit(request, ticket_id):
    print(f"Intentando editar el ticket con ID: {ticket_id}")
    ticket = get_object_or_404(tickets, pk=ticket_id)

    if request.method == 'POST':
        form = TicketUpdateForm(request.POST, instance=ticket)
        ticket_actual = tickets.objects.get(pk=ticket_id)
        if form.is_valid():
            ticket = form.save(commit=False)

            if form.cleaned_data['estado'] != ticket_actual.estado:
                print(f"Estado cambiado de {ticket_actual.estado} a {form.cleaned_data['estado']}")
                ticket.fecha_resolucion = timezone.now()
                _save_historial_ticket(ticket_id, form, request)
            ticket.save()
            messages.success(request, 'Ticket actualizado correctamente.')
            return redirect('tickets_view')
    else:
        form = TicketUpdateForm(instance=ticket)

    return render(request, 'tickets_edit.html', {'form': form, 'ticket': ticket})

def tickets_delete(request):
    if request.method != 'POST':
        return redirect('tickets_view')

    tickets_seleccionados = request.POST.getlist('tickets_seleccionados')

    if not tickets_seleccionados:
        messages.error(request, 'No se seleccionó ningún ticket para eliminar.')
        return redirect('tickets_view')

    borrar_tickets, _ = tickets.objects.filter(id__in=tickets_seleccionados).delete()

    if borrar_tickets > 0:
        messages.success(request, 'Tickets borrados correctamente.')
    else:
        messages.error(request, 'No se encontraron tickets para borrar.')

    return redirect('tickets_view')