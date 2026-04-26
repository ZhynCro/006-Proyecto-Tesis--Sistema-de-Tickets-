from django.test import TestCase
from django.urls import reverse

from users.models import usuario


class DashboardViewTests(TestCase):
    def setUp(self):
        self.user = usuario.objects.create_user(ID_empleado='8010', username='viewdash', password='Pass1234!')

    def test_dashboard_view_requires_login(self):
        response = self.client.get(reverse('dashboard_view'))
        self.assertEqual(response.status_code, 302)

    def test_dashboard_view_renders_template_for_authenticated_user(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('dashboard_view'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard_view.html')