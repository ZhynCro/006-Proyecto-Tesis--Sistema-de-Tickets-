from django import forms
from django.contrib.auth.models import Group
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError


class UsuarioCreationForm(UserCreationForm):

    grupo = forms.ModelChoiceField(
        queryset=Group.objects.none(),
        required=True,
        empty_label='Seleccione un grupo',
        label='Grupo',
    )

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = (
            'ID_empleado',
            'username',
            'first_name',
            'last_name',
            'email',
            'departamento',
            'sede',
            'password1',
            'password2',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['grupo'].queryset = Group.objects.order_by('name')
        self.fields['grupo'].widget.attrs['required'] = 'required'
        for field in self.fields.values():
            field.widget.attrs.setdefault(
                'class',
                'w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:border-blue-300',
            )

    def save(self, commit=True):
        usuario = super().save(commit=False)
        grupo = self.cleaned_data.get('grupo')

        if commit:
            usuario.save()
            if grupo:
                usuario.groups.set([grupo])

        return usuario

    def clean_ID_empleado(self):
        id_empleado = (self.cleaned_data.get('ID_empleado') or '').strip()

        if not id_empleado:
            raise ValidationError('Debes ingresar un ID de empleado.')

        if get_user_model().objects.filter(ID_empleado=id_empleado).exists():
            raise ValidationError('Ya existe un usuario con este ID de empleado.')

        return id_empleado


class UsuarioUpdateForm(forms.ModelForm):

    grupo = forms.ModelChoiceField(
        queryset=Group.objects.none(),
        required=True,
        empty_label='Seleccione un grupo',
        label='Grupo',
    )

    class Meta:
        model = get_user_model()
        fields = (
            'ID_empleado',
            'username',
            'first_name',
            'last_name',
            'email',
            'departamento',
            'sede',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['grupo'].queryset = Group.objects.order_by('name')
        if self.instance and self.instance.pk:
            self.fields['grupo'].initial = self.instance.groups.first()
        for field in self.fields.values():
            field.widget.attrs.setdefault(
                'class',
                'w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:border-blue-300',
            )

    def save(self, commit=True):
        usuario = super().save(commit=False)
        grupo = self.cleaned_data.get('grupo')

        if commit:
            usuario.save()
            if grupo:
                usuario.groups.set([grupo])

        return usuario