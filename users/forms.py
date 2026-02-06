from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model


class UsuarioCreationForm(UserCreationForm):
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
        for field in self.fields.values():
            field.widget.attrs.setdefault(
                'class',
                'w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:border-blue-300',
            )


class UsuarioUpdateForm(forms.ModelForm):
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
        for field in self.fields.values():
            field.widget.attrs.setdefault(
                'class',
                'w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:border-blue-300',
            )