from django.test import TestCase

from inventory.models import activos, activos_categoria
from users.models import departamento, sede


class InventoryModelsTests(TestCase):
    def setUp(self):
        self.depto = departamento.objects.create(codigo='ADM', nombre='Administracion')
        self.sede = sede.objects.create(codigo='STD', nombre='Estacion Santo Domingo')
        self.sede.departamentos.add(self.depto)
        self.categoria = activos_categoria.objects.create(codigo='IMP', nombre='Impresora')

    def test_activo_categoria_str(self):
        self.assertEqual(str(self.categoria), 'Impresora')

    def test_activo_str_returns_brand_model(self):
        activo = activos.objects.create(
            codigo='ETR-01-ADM-IMP-0001',
            categoria=self.categoria,
            marca='Brother',
            modelo='DCP',
            serial='SER-I-01',
            sede=self.sede,
            departamento=self.depto,
            estado='activo',
        )
        self.assertEqual(str(activo), 'Brother DCP')
