from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator
from django.conf import settings
from tickets.forms import TicketCreationForm, TicketUpdateForm, TicketCommentForm
from tickets.models import tickets, matriz_prioridad, tickets_historial, tickets_comentarios
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

@login_required
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
        'usuarios_asignados': usuario.objects.filter(is_active=True, groups__id__in=[1, 5, 3, 4]).order_by('first_name', 'last_name', 'ID_empleado').distinct(),
        'prioridades': matriz_prioridad.objects.order_by('prioridad'),
        'filtros': filtros,
    }

    paginator = Paginator(tickets_registrados, settings.PAGINATION_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get('page'))
    contexto['tickets'] = page_obj
    contexto['page_obj'] = page_obj

    return render(request, 'tickets_view.html', contexto)

@login_required
def tickets_view_self(request):
    current_user = _get_current_usuario(request)
    tickets_asignados = tickets.objects.none()
    if current_user:
        tickets_asignados = tickets.objects.select_related('activo_afectado', 'prioridad', 'solicitante', 'usuario').filter(
            usuario=current_user, estado__in=['Pendiente', 'En Progreso']
        ).order_by('-fecha_creacion')

    paginator = Paginator(tickets_asignados, settings.PAGINATION_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'tickets_view_self.html', {'tickets': page_obj, 'page_obj': page_obj})

@login_required
def tickets_view_pending(request):
    tickets_pendientes = tickets.objects.select_related('activo_afectado', 'prioridad', 'solicitante', 'usuario').filter(
        estado__iexact='pendiente'
    ).order_by('-fecha_creacion')

    paginator = Paginator(tickets_pendientes, settings.PAGINATION_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'tickets_view_pending.html', {'tickets': page_obj, 'page_obj': page_obj})

def tickets_create(request):
    current_user = _get_current_usuario(request)

    if not current_user:
        messages.error(request, 'No se pudo identificar al solicitante del ticket.')
        return redirect('login')

    if request.method == 'POST':
        form = TicketCreationForm(request.POST, usuario=current_user)
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
        form = TicketCreationForm(usuario=current_user)

    return render(request, 'tickets_create.html', {'form': form})

@login_required
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

@login_required
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


@login_required
def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(tickets, pk=ticket_id)
    comentarios = ticket.comentarios.select_related('autor').order_by('fecha_registro')
    current_user = _get_current_usuario(request)

    if request.method == 'POST' and 'comentario' in request.POST:
        form = TicketCommentForm(request.POST, request.FILES)
        if form.is_valid():
            comentario = form.save(commit=False)
            comentario.ticket = ticket
            comentario.autor = current_user
            comentario.save()
            messages.success(request, 'Comentario agregado correctamente.')
            return redirect('ticket_detail', ticket_id=ticket_id)
    else:
        form = TicketCommentForm()

    can_process = False
    if current_user and ticket.estado == 'En Progreso':
        is_assigned = ticket.usuario_id == current_user.ID_empleado
        is_superuser = getattr(current_user, 'is_superuser', False)
        is_tech_or_supervisor = current_user.groups.filter(name__in=['Tecnico', 'Supervisor']).exists()
        can_process = is_assigned or is_superuser or is_tech_or_supervisor

    if request.method == 'POST' and 'procesar' in request.POST:
        if can_process:
            estado_anterior = ticket.estado
            ticket.estado = 'Resuelto'
            ticket.fecha_resolucion = timezone.now()
            ticket.save()
            historial = tickets_historial(
                estado_anterior=estado_anterior,
                estado_nuevo='Resuelto',
                fecha_cambio=timezone.now(),
                responsable=current_user,
                ticket_id=ticket,
            )
            historial.save()
            messages.success(request, 'Ticket marcado como Resuelto.')
            return redirect('ticket_detail', ticket_id=ticket_id)

    contexto = {
        'ticket': ticket,
        'comentarios': comentarios,
        'form': form,
        'can_process': can_process,
    }
    return render(request, 'ticket_detail.html', contexto)


@login_required
def tickets_view_resolved(request):
    tickets_resueltos = tickets.objects.select_related('activo_afectado', 'prioridad', 'solicitante', 'usuario').filter(
        estado='Resuelto'
    ).order_by('-fecha_creacion')

    paginator = Paginator(tickets_resueltos, settings.PAGINATION_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'tickets_view_resolved.html', {'tickets': page_obj, 'page_obj': page_obj})


@login_required
def ticket_resolve(request, ticket_id):
    ticket = get_object_or_404(tickets, pk=ticket_id)
    comentarios = ticket.comentarios.select_related('autor').order_by('fecha_registro')
    current_user = _get_current_usuario(request)

    if request.method == 'POST' and 'comentario' in request.POST:
        form = TicketCommentForm(request.POST, request.FILES)
        if form.is_valid() and form.cleaned_data.get('mensaje'):
            comentario = form.save(commit=False)
            comentario.ticket = ticket
            comentario.autor = current_user
            comentario.save()
            return redirect('ticket_resolve', ticket_id=ticket_id)
    else:
        form = TicketCommentForm()

    can_approve = False
    if current_user and ticket.estado == 'Resuelto':
        is_superuser = getattr(current_user, 'is_superuser', False)
        is_supervisor = current_user.groups.filter(name='Supervisor').exists()
        can_approve = is_superuser or is_supervisor

    if request.method == 'POST' and 'aprobar' in request.POST:
        if can_approve:
            estado_anterior = ticket.estado
            ticket.estado = 'Cerrado'
            ticket.fecha_resolucion = timezone.now()
            ticket.save()
            historial = tickets_historial(
                estado_anterior=estado_anterior,
                estado_nuevo='Cerrado',
                fecha_cambio=timezone.now(),
                responsable=current_user,
                ticket_id=ticket,
            )
            historial.save()
            messages.success(request, 'Resolución aprobada. Ticket cerrado.')
            return redirect('tickets_view_resolved')

    contexto = {
        'ticket': ticket,
        'comentarios': comentarios,
        'form': form,
        'can_approve': can_approve,
    }
    return render(request, 'ticket_resolve.html', contexto)