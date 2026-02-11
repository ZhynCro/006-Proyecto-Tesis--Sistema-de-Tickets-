from django import forms

from inventory.models import activos


class ActivoCreationForm(forms.ModelForm):
    class Meta:
        model = activos
        fields = (
            'codigo',
            'categoria',
            'marca',
            'modelo',
            'serial',
            'sede',
            'usuario_asignado',
            'departamento',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault(
                'class',
                'w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:border-blue-300',
            )

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.estado:
            instance.estado = 'activo'
        if commit:
            instance.save()
        return instance


class ActivoUpdateForm(forms.ModelForm):
    class Meta:
        model = activos
        fields = (
            'categoria',
            'marca',
            'modelo',
            'serial',
            'sede',
            'usuario_asignado',
            'departamento',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault(
                'class',
                'w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:border-blue-300',
            )