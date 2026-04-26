from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from users.models import departamento, sede, usuario


class UsersViewsTests(TestCase):
    def setUp(self):
        self.group = Group.objects.create(name='Superadmin')
        self.depto = departamento.objects.create(codigo='IT', nombre='Tecnologia')
        self.sede = sede.objects.create(codigo='MIQ', nombre='Estacion Maiquetia')
        self.sede.departamentos.add(self.depto)
        self.admin = usuario.objects.create_user(
            ID_empleado='1000',
            username='admin',
            password='AdminPass123!',
            departamento=self.depto,
            sede=self.sede,
        )

    def test_login_view_get_returns_template(self):
        response = self.client.get(reverse('login'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_login_view_post_with_existing_employee_sets_session(self):
        response = self.client.post(reverse('login'), {'ID_empleado': self.admin.ID_empleado})

        self.assertRedirects(response, reverse('tickets_create'))
        self.assertEqual(self.client.session.get('ID_empleado'), self.admin.ID_empleado)

    def test_user_view_requires_authentication(self):
        response = self.client.get(reverse('user_view'))
        self.assertEqual(response.status_code, 302)

    def test_user_create_post_valid_creates_user(self):
        self.client.force_login(self.admin)
        payload = {
            'ID_empleado': '2222',
            'username': 'nuevo',
            'first_name': 'Nuevo',
            'last_name': 'Usuario',
            'email': 'nuevo@example.com',
            'departamento': self.depto.pk,
            'sede': self.sede.pk,
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
            'grupo': self.group.pk,
        }

        response = self.client.post(reverse('user_create'), payload)

        self.assertRedirects(response, reverse('user_view'))
        self.assertTrue(usuario.objects.filter(ID_empleado='2222').exists())

    def test_user_delete_post_without_selection_redirects(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse('user_delete'), {})

        self.assertRedirects(response, reverse('user_view'))

    def test_admin_login_view_post_valid_credentials_redirects_dashboard(self):
        response = self.client.post(
            reverse('admin_login'),
            {'ID_empleado': self.admin.ID_empleado, 'password': 'AdminPass123!'},
        )

        self.assertRedirects(response, reverse('dashboard_view'))
