from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from inventory.models import activos
from tickets.forms import TicketCreationForm, TicketUpdateForm
from tickets.models import tickets


def ticket_view(request):
    tickets_registrados = (
        tickets.objects.select_related('categoria', 'titulo', 'sede', 'usuario', 'departamento')
        .filter(estado__iexact='abierto')
        .order_by('fecha_creacion')
    )
    return render(request, 'tickets_view.html', {'tickets': tickets_registrados})


def inventory_create(request):
    if request.method == 'POST':
        form = TicketCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Activo creado correctamente.')
            return redirect('ticket_view')
    else:
        form = TicketCreationForm()

    return render(request, 'tickets_create.html', {'form': form})


def inventory_edit(request, id):
    ticket = get_object_or_404(tickets, pk=id)

    if request.method == 'POST':
        form = TicketUpdateForm(request.POST, instance=ticket)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ticket actualizado correctamente.')
            return redirect('ticket_view')
    else:
        form = TicketUpdateForm(instance=ticket)

    return render(request, 'tickets_edit.html', {'form': form, 'ticket': ticket})


def inventory_delete(request):
    if request.method != 'POST':
        return redirect('ticket_view')

    tickets_seleccionados = request.POST.getlist('tickets_seleccionados')

    if not tickets_seleccionados:
        messages.error(request, 'No se seleccionó ningún ticket para eliminar.')
        return redirect('ticket_view')

    borrar_tickets = tickets.objects.filter(id__in=tickets_seleccionados).delete()

    if borrar_tickets > 0:
        messages.success(request, 'Tickets borrados correctamente.')
    else:
        messages.error(request, 'No se encontraron tickets para borrar.')

    return redirect('ticket_view')