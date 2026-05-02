from django.db import models

class activos_categoria(models.Model):
    codigo = models.CharField(max_length=50, unique=True, null=True)
    nombre = models.CharField(max_length=100, unique=True)
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
        to_field='nombre',
        db_column='categoria',
        related_name='activos',
    )
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    serial = models.CharField(max_length=50)
    sede = models.ForeignKey(
        'users.sede',
        on_delete=models.PROTECT,
        to_field='codigo',
        related_name='activos',
    )
    usuario_asignado = models.ForeignKey(
        'users.usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='activos_asignados',
        to_field='ID_empleado',
        db_column='usuario_asignado'
    )
    departamento = models.ForeignKey(
        'users.departamento',
        on_delete=models.PROTECT,
        to_field='codigo',
        db_column='departamento',
        related_name='activos'
    )
    estado = models.CharField(max_length=50) #'Activo', 'Inactivo', 'Dado de baja'

    verbose_name_plural = "activos"

    def __str__(self):
        return f"{self.marca} {self.modelo}"
