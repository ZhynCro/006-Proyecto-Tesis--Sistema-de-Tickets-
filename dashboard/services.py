from django.db.models import Count, Q

from inventory.models import activos
from library.models import Tutorial
from tickets.models import tickets
from users.models import usuario


def get_current_usuario(request):
    id_empleado = request.session.get('ID_empleado')
    if id_empleado:
        return usuario.objects.filter(ID_empleado=id_empleado, is_active=True).first()

    if request.user.is_authenticated:
        return request.user

    return None


def build_dashboard_context(request):
    tickets_all = tickets.objects.select_related('prioridad', 'usuario', 'solicitante', 'activo_afectado')

    estado_totales = {
        row['estado']: row['total']
        for row in tickets_all.values('estado').annotate(total=Count('id'))
    }

    prioridades_totales = list(
        tickets_all.values('prioridad_id').annotate(total=Count('id')).order_by('-total')
    )

    current_user = get_current_usuario(request)
    mis_tickets = tickets.objects.none()
    if current_user:
        mis_tickets = (
            tickets_all.filter(usuario=current_user)
            .exclude(estado='Cerrado')
            .order_by('-fecha_creacion')[:5]
        )

    kpis = {
        'tickets_totales': tickets_all.count(),
        'tickets_abiertos': tickets_all.filter(estado__in=['Pendiente', 'En Progreso']).count(),
        'tickets_resueltos': tickets_all.filter(estado='Resuelto').count(),
        'tickets_sin_asignar': tickets_all.filter(estado='Pendiente', usuario__isnull=True).count(),
        'activos_totales': activos.objects.count(),
        'activos_asignados': activos.objects.filter(usuario_asignado__isnull=False).count(),
        'documentos_totales': Tutorial.objects.count(),
    }

    return {
        'kpis': kpis,
        'estado_totales': estado_totales,
        'prioridades_totales': prioridades_totales,
        'tickets_recientes': tickets_all.order_by('-fecha_creacion')[:5],
        'mis_tickets': mis_tickets,
        'tickets_criticos': tickets_all.filter(
            Q(prioridad_id='Alta') | Q(prioridad_id='Crítica'),
            estado='Pendiente',
        ).order_by('-fecha_creacion')[:5],
    }