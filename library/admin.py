from django.contrib import admin

# Register your models here.
from .models import Tutorial

class TutorialAdmin(admin.ModelAdmin):
    list_display = (
        'titulo',
        'extension',
        'mime_type',
        'tamano_bytes',
        'creado_en'
    )
    search_fields = (
        'titulo', 
        'nombre_original', 
        'extension', 
        'mime_type'
    )
    list_filter = (
        'extension', 
        'mime_type',
        'creado_en'
    )
