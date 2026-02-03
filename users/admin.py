from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import usuario, departamento, sede

# Register your models here.

class usuarioAdmin(UserAdmin):
    list_display = ('ID_empleado', 'username', 'email', 'sede', 'departamento', 'is_staff', 'is_active')
    ordering = ('ID_empleado',)
    search_fields = ('ID_empleado', 'username', 'email')

    fieldsets = UserAdmin.fieldsets + (
        ('Información Corporativa', {
            'fields': ('ID_empleado', 'sede', 'departamento')
        }),
    )

    # 3. Configuración para CREAR un usuario nuevo
    # Esto asegura que aparezcan los campos en el formulario inicial
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información Corporativa', {
            'fields': ('ID_empleado', 'sede', 'departamento')
        }),
    )

admin.site.register(usuario, usuarioAdmin)
admin.site.register(departamento)
admin.site.register(sede)