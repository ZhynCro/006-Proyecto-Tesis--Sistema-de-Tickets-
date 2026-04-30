from django import forms
from .models import tickets
from inventory.models import activos

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