from django.test import TestCase

from inventory.forms import ActivoCreationForm
from inventory.models import activos, activos_categoria
from users.models import departamento, sede


class InventoryFormsTests(TestCase):
    def setUp(self):
        self.depto = departamento.objects.create(codigo='FIN', nombre='Contabilidad')
        self.sede = sede.objects.create(codigo='STB', nombre='Estacion Santa Barbara')
        self.sede.departamentos.add(self.depto)
        self.categoria = activos_categoria.objects.create(codigo='LAP', nombre='Laptop')

    def test_creation_form_valid_and_generates_code(self):
        form = ActivoCreationForm(data={
            'categoria': self.categoria.nombre,
            'marca': 'Lenovo',
            'modelo': 'T14',
            'serial': 'SER-L-01',
            'sede': self.sede.codigo,
            'departamento': self.depto.nombre,
        })

        self.assertTrue(form.is_valid(), form.errors)
        instance = form.save()
        self.assertTrue(instance.codigo.startswith('ETR-01-FIN-LAP-'))

    def test_creation_form_invalid_when_correlativo_overflow(self):
        activos.objects.create(
            codigo='ETR-01-FIN-LAP-9999',
            categoria=self.categoria,
            marca='Lenovo',
            modelo='T14',
            serial='SER-L-99',
            sede=self.sede,
            departamento=self.depto,
            estado='activo',
        )
        form = ActivoCreationForm(data={
            'categoria': self.categoria.nombre,
            'marca': 'Dell',
            'modelo': 'XPS',
            'serial': 'SER-L-02',
            'sede': self.sede.codigo,
            'departamento': self.depto.nombre,
        })
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
