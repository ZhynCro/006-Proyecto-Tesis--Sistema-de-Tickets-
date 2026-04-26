from django.contrib.auth.models import Group
from django.test import TestCase

from users.forms import UsuarioCreationForm, UsuarioUpdateForm
from users.models import departamento, sede, usuario


class UsuarioFormTests(TestCase):
    def setUp(self):
        self.group = Group.objects.create(name='Tecnico')
        self.depto = departamento.objects.create(codigo='OPS', nombre='Ventas')
        self.sede = sede.objects.create(codigo='PMV', nombre='Estacion Porlamar')
        self.sede.departamentos.add(self.depto)

    def _valid_payload(self, **overrides):
        payload = {
            'ID_empleado': '7777',
            'username': 'operador',
            'first_name': 'Ana',
            'last_name': 'Perez',
            'email': 'ana@example.com',
            'departamento': self.depto.pk,
            'sede': self.sede.pk,
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
            'grupo': self.group.pk,
        }
        payload.update(overrides)
        return payload

    def test_given_valid_data_when_creation_form_then_is_valid_and_assigns_group(self):
        form = UsuarioCreationForm(data=self._valid_payload())

        self.assertTrue(form.is_valid(), form.errors)
        created_user = form.save()
        self.assertEqual(created_user.groups.first(), self.group)

    def test_given_duplicate_employee_id_when_creation_form_then_invalid(self):
        usuario.objects.create_user(ID_empleado='7777', username='otro', password='Pass1234!')

        form = UsuarioCreationForm(data=self._valid_payload(username='repetido'))

        self.assertFalse(form.is_valid())
        self.assertIn('ID_empleado', form.errors)

    def test_given_update_form_when_valid_then_group_reassigned(self):
        old_group = Group.objects.create(name='Supervisor')
        instance = usuario.objects.create_user(
            ID_empleado='9876',
            username='edituser',
            password='Pass1234!',
            departamento=self.depto,
            sede=self.sede,
        )
        instance.groups.add(old_group)

        form = UsuarioUpdateForm(
            data={
                'ID_empleado': '9876',
                'username': 'edituser',
                'first_name': 'Edit',
                'last_name': 'User',
                'email': 'edit@example.com',
                'departamento': self.depto.pk,
                'sede': self.sede.pk,
                'grupo': self.group.pk,
            },
            instance=instance,
        )

        self.assertTrue(form.is_valid(), form.errors)
        updated_user = form.save()
        self.assertEqual(updated_user.groups.first(), self.group)
