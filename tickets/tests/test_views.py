from django.test import TestCase
from django.urls import reverse

from inventory.models import activos, activos_categoria
from tickets.models import matriz_prioridad, tickets, tickets_historial
from users.models import departamento, sede, usuario


class TicketViewsTests(TestCase):
    def setUp(self):
        self.depto = departamento.objects.create(codigo='OPS', nombre='Ventas')
        self.sede = sede.objects.create(codigo='SVZ', nombre='Estacion San Antonio')
        self.sede.departamentos.add(self.depto)
        self.user = usuario.objects.create_user(
            ID_empleado='3001', username='agent', password='Pass1234!', departamento=self.depto, sede=self.sede
        )
        categoria = activos_categoria.objects.create(codigo='CPU', nombre='CPU')
        self.activo = activos.objects.create(
            codigo='ETR-01-OPS-CPU-0001', categoria=categoria, marca='HP', modelo='Elite', serial='SER-456',
            sede=self.sede, departamento=self.depto, estado='activo'
        )
        self.na = matriz_prioridad.objects.create(prioridad='N/A', tiempo_respuesta_minutos=30, tiempo_resolucion_minutos=90)
        self.alta = matriz_prioridad.objects.create(prioridad='Alta', tiempo_respuesta_minutos=10, tiempo_resolucion_minutos=30)
        self.ticket = tickets.objects.create(
            codigo_ticket='TKT-00011', titulo='Falla', descripcion='Error general', prioridad=self.na,
            solicitante=self.user, usuario=self.user, activo_afectado=self.activo, estado='Pendiente'
        )

    def test_tickets_view_requires_login(self):
        response = self.client.get(reverse('tickets_view'))
        self.assertEqual(response.status_code, 302)

    def test_tickets_create_post_with_session_user_creates_ticket(self):
        session = self.client.session
        session['ID_empleado'] = self.user.ID_empleado
        session.save()

        response = self.client.post(reverse('tickets_create'), {
            'titulo': 'Nuevo ticket',
            'descripcion': 'Descripción',
            'activo_afectado': self.activo.codigo,
        })

        self.assertRedirects(response, reverse('tickets_view'), fetch_redirect_response=False)
        self.assertTrue(tickets.objects.filter(titulo='Nuevo ticket').exists())

    def test_tickets_edit_post_changes_status_and_creates_history(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('tickets_edit', args=[self.ticket.pk]), {
            'titulo': self.ticket.titulo,
            'descripcion': self.ticket.descripcion,
            'estado': 'En Progreso',
            'prioridad': self.alta.prioridad,
            'activo_afectado': self.activo.codigo,
            'solicitante': self.user.ID_empleado,
            'usuario': self.user.ID_empleado,
        })

        self.assertRedirects(response, reverse('tickets_view'))
        self.assertEqual(tickets_historial.objects.filter(ticket_id=self.ticket).count(), 1)

    def test_tickets_delete_get_redirects_without_deleting(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('tickets_delete'))
        self.assertRedirects(response, reverse('tickets_view'))
        self.assertTrue(tickets.objects.filter(pk=self.ticket.pk).exists())
