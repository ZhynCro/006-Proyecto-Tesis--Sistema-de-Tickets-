from django import forms
from .models import tickets, tickets_comentarios
from inventory.models import activos
import os
from django.core.exceptions import ValidationError


class TicketCommentForm(forms.ModelForm):
    ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg'}
    ALLOWED_MIME_TYPES = {'image/png', 'image/jpeg'}
    MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB

    class Meta:
        model = tickets_comentarios
        fields = ('mensaje', 'archivo_adjunto')
        widgets = {
            'mensaje': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Escribe un comentario...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['mensaje'].widget.attrs.setdefault(
            'class',
            'w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:border-blue-300',
        )
        self.fields['archivo_adjunto'].widget.attrs.setdefault(
            'class',
            'file-input file-input-bordered w-full',
        )

    def clean_archivo_adjunto(self):
        archivo = self.cleaned_data.get('archivo_adjunto')
        if not archivo:
            return archivo

        extension = os.path.splitext(archivo.name)[1].lower()
        if extension not in self.ALLOWED_EXTENSIONS:
            raise ValidationError('Tipo de archivo no permitido. Solo se aceptan .png, .jpg y .jpeg')

        mime_type = getattr(archivo, 'content_type', None)
        if mime_type and mime_type not in self.ALLOWED_MIME_TYPES:
            raise ValidationError('Formato del archivo no válido')

        if archivo.size > self.MAX_FILE_SIZE_BYTES:
            raise ValidationError('El tamaño maximo permitido es de 5MB')

        return archivo


class TicketCreationForm(forms.ModelForm):
    class Meta:
        model = tickets
        fields = (
            'titulo',
            'descripcion',
            'activo_afectado',
        )
        widgets = {
            'titulo': forms.TextInput(attrs={'placeholder': 'Título del ticket'}),
            'descripcion': forms.Textarea(attrs={'rows': 1, 'placeholder': 'Describenos brevemente el problema...'}),
        }

    def __init__(self, *args, **kwargs):
        usuario = kwargs.pop('usuario', None)
        super().__init__(*args, **kwargs)
        queryset = activos.objects.filter(estado__iexact='activo')
        if usuario is not None:
            queryset = queryset.filter(usuario_asignado=usuario)
        else:
            queryset = queryset.none()
        self.fields['activo_afectado'].queryset = queryset
        for field in self.fields.values():
            field.widget.attrs.setdefault(
                'class',
                'w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:border-blue-300',
            )


class TicketUpdateForm(forms.ModelForm):
    class Meta:
        model = tickets
        fields = (
            'titulo',
            'descripcion',
            'estado',
            'prioridad',
            'activo_afectado',
            'solicitante',
            'usuario',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault(
                'class',
                'w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:border-blue-300',
            )