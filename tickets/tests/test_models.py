from django.test import TestCase

from inventory.models import activos, activos_categoria
from tickets.models import matriz_prioridad, tickets
from users.models import departamento, sede, usuario


class TicketsModelTests(TestCase):
    def setUp(self):
        self.depto = departamento.objects.create(codigo='TI', nombre='Mercadeo')
        self.sede = sede.objects.create(codigo='CCS', nombre='Caracas - Sede Principal las Mercedes')
        self.sede.departamentos.add(self.depto)
        self.user = usuario.objects.create_user(ID_empleado='1001', username='sol', password='Pass1234!')
        categoria = activos_categoria.objects.create(codigo='LAP', nombre='Laptop')
        self.activo = activos.objects.create(
            codigo='ETR-01-TI-LAP-0001',
            categoria=categoria,
            marca='Dell',
            modelo='XPS',
            serial='SER-001',
            sede=self.sede,
            departamento=self.depto,
            estado='activo',
        )
        self.prioridad = matriz_prioridad.objects.create(
            prioridad='N/A',
            tiempo_respuesta_minutos=30,
            tiempo_resolucion_minutos=60,
        )

    def test_given_valid_ticket_when_create_then_str_returns_code(self):
        ticket = tickets.objects.create(
            codigo_ticket='TKT-00001',
            titulo='Pantalla dañada',
            descripcion='No enciende',
            prioridad=self.prioridad,
            solicitante=self.user,
            activo_afectado=self.activo,
        )
        self.assertEqual(str(ticket), 'TKT-00001')
