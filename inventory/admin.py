from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import activos_categoria, activos

# Register your models here.

class ActivosCategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
    search_fields = ('nombre',)
    ordering = ('nombre',)

class ActivosAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'categoria', 'marca', 'modelo', 'serial', 'sede', 'usuario_asignado', 'departamento', 'estado')
    search_fields = ('codigo', 'marca', 'modelo', 'serial')
    list_filter = ('categoria', 'sede', 'departamento', 'estado')
    ordering = ('codigo',)

admin.site.register(activos_categoria, ActivosCategoriaAdmin)
admin.site.register(activos, ActivosAdmin)

