import os
import uuid
from django.db import models
from django.utils import timezone


def comentario_adjunto_path(instance, filename):
    fecha = timezone.now().strftime('%Y-%m-%d')
    ticket_code = instance.ticket.codigo_ticket
    ext = os.path.splitext(filename)[1].lower()
    unique_id = uuid.uuid4().hex[:8]
    new_name = f"{ticket_code}_{fecha}_{unique_id}{ext}"
    return os.path.join('tickets_adjuntos', new_name)


class matriz_prioridad(models.Model):
    prioridad = models.CharField(max_length=20, unique=True)
    tiempo_respuesta_minutos = models.IntegerField()
    tiempo_resolucion_minutos = models.IntegerField()

    def __str__(self):
        return f"{self.prioridad}"


class tickets(models.Model):
    codigo_ticket = models.CharField(max_length=30, unique=True)
    titulo = models.CharField(max_length=150)
    descripcion = models.TextField()
    prioridad = models.ForeignKey(
        matriz_prioridad,
        on_delete=models.PROTECT,
        to_field='prioridad',
        db_column='prioridad',
        related_name='tickets',
        default='N/A',
    )

    ESTADO_TYPES = [
        ('Pendiente', 'Pendiente'),
        ('En Progreso', 'En Progreso'),
        ('Resuelto', 'Resuelto'),
        ('Cerrado', 'Cerrado'),
    ]
    estado = models.CharField(max_length=30, default='Pendiente', choices=ESTADO_TYPES)
    solicitante = models.ForeignKey(
        'users.usuario',
        on_delete=models.PROTECT,
        to_field='ID_empleado',
        db_column='solicitante',
        related_name='tickets_solicitados',
    )
    usuario = models.ForeignKey(
        'users.usuario',
        on_delete=models.PROTECT,
        to_field='ID_empleado',
        db_column='usuario',
        related_name='tickets_asignados',
        null=True,
        blank=True,
    )
    activo_afectado = models.ForeignKey(
        'inventory.activos',
        on_delete=models.CASCADE,
        to_field='codigo',
        db_column='activo_afectado',
        related_name='tickets_afectados',
        limit_choices_to={'estado': 'activo'},
)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_resolucion = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.codigo_ticket


class tickets_comentarios(models.Model):
    ticket = models.ForeignKey(
        tickets,
        on_delete=models.CASCADE,

        related_name='comentarios'
    )
    autor = models.ForeignKey(
        'users.usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        to_field='ID_empleado',
        db_column='autor',
        related_name='comentarios_autor',
    )
    mensaje = models.TextField()
    archivo_adjunto = models.FileField(upload_to=comentario_adjunto_path, null=True, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)


class tickets_historial(models.Model):
    ticket_id = models.ForeignKey(
        tickets,
        on_delete=models.CASCADE,
        db_column='ticket_id',
        to_field='codigo_ticket',
        related_name='historial',
    )
    estado_anterior = models.CharField(max_length=30)
    estado_nuevo = models.CharField(max_length=30)
    fecha_cambio = models.DateTimeField(auto_now_add=True)
    responsable = models.ForeignKey(
        'users.usuario',
        on_delete=models.CASCADE,
        verbose_name='Responsable del cambio',
        to_field='ID_empleado',
        db_column='responsable',
    )