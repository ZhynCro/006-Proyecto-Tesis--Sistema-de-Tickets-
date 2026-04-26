from django.test import TestCase
from django.urls import reverse

from inventory.models import activos, activos_categoria
from users.models import departamento, sede, usuario


class InventoryViewsTests(TestCase):
    def setUp(self):
        self.depto = departamento.objects.create(codigo='TES', nombre='Tesoreria')
        self.sede = sede.objects.create(codigo='MAR', nombre='Estacion Maracaibo')
        self.sede.departamentos.add(self.depto)
        self.user = usuario.objects.create_user(ID_empleado='5010', username='invadmin', password='Pass1234!')
        self.categoria = activos_categoria.objects.create(codigo='TEL', nombre='Telefono')
        self.activo = activos.objects.create(
            codigo='ETR-01-COM-TEL-0001',
            categoria=self.categoria,
            marca='Cisco',
            modelo='CP',
            serial='SER-T-01',
            sede=self.sede,
            departamento=self.depto,
            estado='activo',
        )

    def test_inventory_view_requires_auth(self):
        response = self.client.get(reverse('inventory_view'))
        self.assertEqual(response.status_code, 302)

    def test_inventory_create_post_valid_redirects(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('inventory_create'), {
            'categoria': self.categoria.nombre,
            'marca': 'Avaya',
            'modelo': 'V2',
            'serial': 'SER-T-02',
            'sede': self.sede.codigo,
            'departamento': self.depto.nombre,
        })

        self.assertRedirects(response, reverse('inventory_view'))
        self.assertTrue(activos.objects.filter(serial='SER-T-02').exists())

    def test_inventory_delete_post_marks_inactive(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('inventory_delete'), {'activos_seleccionados': [self.activo.codigo]})

        self.assertRedirects(response, reverse('inventory_view'))
        self.activo.refresh_from_db()
        self.assertEqual(self.activo.estado, 'inactivo')
