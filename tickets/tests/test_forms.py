from django.test import TestCase

from inventory.models import activos, activos_categoria
from tickets.forms import TicketCreationForm, TicketUpdateForm
from tickets.models import matriz_prioridad, tickets
from users.models import departamento, sede, usuario


class TicketFormsTests(TestCase):
    def setUp(self):
        self.depto = departamento.objects.create(codigo='TI', nombre='Mercadeo')
        self.sede = sede.objects.create(codigo='CCS', nombre='Caracas - Sede Principal las Mercedes')
        self.sede.departamentos.add(self.depto)
        self.user = usuario.objects.create_user(ID_empleado='2001', username='tech', password='Pass1234!')
        categoria = activos_categoria.objects.create(codigo='MON', nombre='Monitor')
        self.activo = activos.objects.create(
            codigo='ETR-01-TI-MON-0001',
            categoria=categoria,
            marca='LG',
            modelo='24MK',
            serial='SER-777',
            sede=self.sede,
            departamento=self.depto,
            estado='activo',
            usuario_asignado=self.user,
        )
        self.prioridad = matriz_prioridad.objects.create(prioridad='Baja', tiempo_respuesta_minutos=60, tiempo_resolucion_minutos=240)

    def test_creation_form_valid_with_required_fields(self):
        form = TicketCreationForm(data={
            'titulo': 'No prende',
            'descripcion': 'Revisión urgente',
            'activo_afectado': self.activo.codigo,
        })
        self.assertTrue(form.is_valid(), form.errors)

    def test_creation_form_invalid_without_title(self):
        form = TicketCreationForm(data={
            'descripcion': 'Sin título',
            'activo_afectado': self.activo.codigo,
        })
        self.assertFalse(form.is_valid())
        self.assertIn('titulo', form.errors)

    def test_update_form_valid(self):
        ticket = tickets.objects.create(
            codigo_ticket='TKT-00009',
            titulo='Inicial',
            descripcion='Texto',
            prioridad=self.prioridad,
            solicitante=self.user,
            usuario=self.user,
            activo_afectado=self.activo,
            estado='Pendiente',
        )
        form = TicketUpdateForm(data={
            'titulo': 'Actualizado',
            'descripcion': 'Texto nuevo',
            'estado': 'En Progreso',
            'prioridad': self.prioridad.prioridad,
            'activo_afectado': self.activo.codigo,
            'solicitante': self.user.ID_empleado,
            'usuario': self.user.ID_empleado,
        }, instance=ticket)
        self.assertTrue(form.is_valid(), form.errors)

    def test_creation_form_limits_assets_to_usuario(self):
        other = usuario.objects.create_user(ID_empleado='2002', username='other', password='Pass1234!')
        categoria = activos_categoria.objects.get(codigo='MON')
        activo_otro = activos.objects.create(
            codigo='ETR-01-TI-MON-0002',
            categoria=categoria,
            marca='Samsung',
            modelo='S24',
            serial='SER-778',
            sede=self.sede,
            departamento=self.depto,
            estado='activo',
            usuario_asignado=other,
        )

        form = TicketCreationForm(usuario=self.user)

        self.assertIn(self.activo, form.fields['activo_afectado'].queryset)
        self.assertNotIn(activo_otro, form.fields['activo_afectado'].queryset)
