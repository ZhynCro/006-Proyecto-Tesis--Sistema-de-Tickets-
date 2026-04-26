from django import forms
from .models import Tutorial
import os
from django.core.exceptions import ValidationError

class TutorialForm(forms.ModelForm):
    ALLOWED_EXTENSIONS = {
        '.pdf', '.docx', '.doc','.xlsx', '.xls', '.pptx', '.txt'
    }
    ALLOWED_MIME_TYPES = {
        'application/pdf',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        'text/plain',
    }

    MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB

    class Meta:
        model = Tutorial
        fields = ('titulo', 'descripcion', 'archivo')
        labels = {
        'titulo': 'Título',
        'descripcion': 'Descripción',
        'archivo': 'Actualizar Archivo',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs.setdefault(
                'class',
                'w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:border-blue-300',
            )
            if name == 'archivo':
                field.widget = forms.FileInput(attrs=field.widget.attrs)

    # Utils

    def clean_archivo(self):
        archivo = self.cleaned_data.get('archivo')
        if not archivo:
            return archivo
        
        extension = os.path.splitext(archivo.name)[1].lower()
        if extension not in self.ALLOWED_EXTENSIONS:
            raise ValidationError('Tipo de archivo no permitido')
        
        mime_type = getattr(archivo, 'content_type', None)
        if mime_type and mime_type not in self.ALLOWED_MIME_TYPES:
            raise ValidationError('Atributo del archivo no permitido')
        
        if archivo.size > self.MAX_FILE_SIZE_BYTES:
            raise ValidationError('El tamaño máximo permitido es de 5MB.')
        
        return archivo
    
    def save(self, commit=True):
        instance = super().save(commit=False)

        if self.cleaned_data.get('archivo'):
            instance.nombre_original = self.cleaned_data['archivo'].name

        if commit:
            instance.save()
        return instance