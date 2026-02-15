from django import forms
from inventory.models import activos
from django.core.exceptions import ValidationError
from django.db.models import Max


class ActivoCreationForm(forms.ModelForm):
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

    def _get_next_correlativo(self, prefijo_codigo):
        ultimo_codigo = (
            activos.objects.filter(codigo__startswith=f'{prefijo_codigo}-')
            .aggregate(max_codigo=Max('codigo'))
            .get('max_codigo')
        )

        if not ultimo_codigo:
            return 1

        try:
            ultimo_correlativo = int(ultimo_codigo.split('-')[-1])
        except (TypeError, ValueError):
            return 1

        return ultimo_correlativo + 1
    
    def clean(self):
        cleaned_data = super().clean()

        sede = cleaned_data.get('sede')
        departamento = cleaned_data.get('departamento')
        categoria = cleaned_data.get('categoria')

        if not (sede and departamento and categoria):
            return cleaned_data

        correlativo = self._get_next_correlativo(
            f"ETR-{str(sede.id).zfill(2)}-{departamento.codigo}-{categoria.codigo}"
        )
        if correlativo > 9999:
            raise ValidationError('No hay más correlativos disponibles para esta combinación (máximo 9999).')

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        sede_id = str(instance.sede.id).zfill(2)
        prefijo_codigo = f"ETR-{sede_id}-{instance.departamento.codigo}-{instance.categoria.codigo}"
        correlativo = self._get_next_correlativo(prefijo_codigo)

        if correlativo > 9999:
            raise ValidationError('No hay más correlativos disponibles para esta combinación (máximo 9999).')

        instance.codigo = f"{prefijo_codigo}-{str(correlativo).zfill(4)}"

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