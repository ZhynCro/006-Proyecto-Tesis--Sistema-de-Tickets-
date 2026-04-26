from django.core.exceptions import ValidationError
from django.test import TestCase

from users.models import departamento, sede, usuario


class UsuarioModelTests(TestCase):
    def setUp(self):
        self.depto = departamento.objects.create(codigo='TI', nombre='Mercadeo')
        self.sede = sede.objects.create(codigo='CCS', nombre='Caracas - Sede Principal las Mercedes')
        self.sede.departamentos.add(self.depto)

    def test_given_valid_usuario_when_create_then_persists_and_str_format(self):
        user = usuario.objects.create_user(
            ID_empleado='1234',
            username='jdoe',
            password='SafePass123!',
            first_name='John',
            last_name='Doe',
            departamento=self.depto,
            sede=self.sede,
        )

        self.assertEqual(user.ID_empleado, '1234')
        self.assertEqual(str(user), '1234 - John Doe')

    def test_given_invalid_id_empleado_when_full_clean_then_validation_error(self):
        user = usuario(
            ID_empleado='12',
            username='badid',
            departamento=self.depto,
            sede=self.sede,
        )

        with self.assertRaises(ValidationError):
            user.full_clean()


class BaseCatalogModelTests(TestCase):
    def test_departamento_str_returns_nombre(self):
        depto = departamento.objects.create(codigo='RH', nombre='Talento Humano')
        self.assertEqual(str(depto), 'Talento Humano')

    def test_sede_str_returns_nombre(self):
        sede_obj = sede.objects.create(codigo='ALT', nombre='Estacion Barinas')
        self.assertEqual(str(sede_obj), 'Estacion Barinas')
