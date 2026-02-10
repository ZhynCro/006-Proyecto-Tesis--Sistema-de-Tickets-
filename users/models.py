from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

# Create your models here.
class usuario(AbstractUser):
    validador_empleado = RegexValidator(
        regex=r'^\d{4}',
        message="el numero de empleado debe tener 4 digitos"
    )

    ID_empleado = models.CharField(
        max_length=4,
        unique=True,
        validators=[validador_empleado],
        help_text="ID de empleado de 4 digitos",
        default="0000"
    )

    USERNAME_FIELD = 'ID_empleado'

    departamento = models.ForeignKey(
        'departamento',
        on_delete=models.SET_NULL,
        null=True,
        related_name='usuarios'
        )
    
    sede = models.ForeignKey(
        'sede',
        on_delete=models.SET_NULL,
        null=True,
        related_name='usuarios'
        )

    REQUIRED_FIELDS = ['username', 'email']
    def __str__(self):
        return f"{self.ID_empleado} - {self.get_full_name()}"
    
class departamento(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name_plural = "departamentos"
    
class sede(models.Model):
    codigo = models.CharField(max_length=3, unique=True)
    nombre = models.CharField(max_length=50, unique=True)

    departamentos = models.ManyToManyField(
        departamento,
        related_name='sedes',
        help_text="Departamentos en esta sede"
        )
    


    def __str__(self):
        return self.nombre