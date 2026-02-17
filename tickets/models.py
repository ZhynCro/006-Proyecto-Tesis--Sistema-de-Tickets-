from django.db import models

class matriz_prioridad(models.Model):
    prioridad = models.CharField(max_length=20, unique=True)
    tiempo_respuesta_minutos = models.IntegerField()
    tiempo_resolucion_minutos = models.IntegerField()

    def __str__(self):
        return f"{self.prioridad} (Respuesta: {self.tiempo_respuesta_minutos}m, Resolución: {self.tiempo_resolucion_minutos}m)"


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
        default='N/A'
    )
    estado = models.CharField(max_length=30)
    solicitante = models.ForeignKey(
        'users.usuario',
        on_delete=models.PROTECT,
        to_field='ID_empleado',
        db_column='solicitante',
        related_name='tickets_solicitados'
    )
    usuario = models.ForeignKey(
        'users.usuario',
        on_delete=models.PROTECT,
        to_field='ID_empleado',
        db_column='usuario',
        related_name='tickets_asignados'
    )
    activo_afectado = models.ForeignKey(
        "inventory.activos",
        on_delete=models.CASCADE,
        to_field='codigo',
        db_column='activo_afectado',
        related_name='tickets_afectados',
        limit_choices_to={'estado': 'activo'}
)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_resolucion = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.codigo_ticket


class tickets_comentarios(models.Model):
    ticket_id = models.ForeignKey(
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
        related_name='comentarios_autor'
    )
    mensaje = models.TextField()
    archivo_adjunto = models.FileField(upload_to='tickets_adjuntos/', null=True, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)


class tickets_historial(models.Model):
    ticket_id = models.ForeignKey(
        tickets,
        on_delete=models.CASCADE,
        db_column='ticket_id',
        to_field='codigo_ticket',
        related_name='historial'
    )
    estado_anterior = models.CharField(max_length=30)
    estado_nuevo = models.CharField(max_length=30)
    fecha_cambio = models.DateTimeField(auto_now_add=True)
    responsable = models.ForeignKey(
        "users.usuario",
        on_delete=models.CASCADE,
        verbose_name="Responsable del cambio",
        to_field='ID_empleado',
        db_column='responsable'
    )