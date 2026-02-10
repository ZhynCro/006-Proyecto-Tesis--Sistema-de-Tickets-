from django.db import models

class activos_categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    impacto = models.CharField(max_length=10)
    descripcion = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "categorias de activo"

    def __str__(self):
        return self.nombre


class activos(models.Model):
    codigo = models.CharField(max_length=50, primary_key=True)
    categoria = models.ForeignKey(
        activos_categoria,
        on_delete=models.PROTECT,
        related_name='activos',
    )
    sede = models.ForeignKey(
        'users.sede',
        on_delete=models.PROTECT,
        related_name='activos',
    )
    usuario_asignado = models.ForeignKey(
        'users.usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='activos_asignados',
        to_field='ID_empleado',
    )
    departamento = models.ForeignKey(
        'users.departamento',
        on_delete=models.PROTECT,
        related_name='activos',
    )
    estado = models.CharField(max_length=50) #'Activo', 'Inactivo', 'Dado de baja'
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    serial = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f"{self.codigo} - {self.marca} {self.modelo}"
