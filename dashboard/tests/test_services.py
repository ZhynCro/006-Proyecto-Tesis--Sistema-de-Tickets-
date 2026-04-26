from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, TestCase

from dashboard.services import build_dashboard_context, get_current_usuario
from inventory.models import activos, activos_categoria
from library.models import Tutorial
from tickets.models import matriz_prioridad, tickets
from users.models import departamento, sede, usuario


class DashboardServicesTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.depto = departamento.objects.create(codigo='SUP', nombre='Comercial')
        self.sede = sede.objects.create(codigo='PTY', nombre='Estacion Panama')
        self.sede.departamentos.add(self.depto)
        self.user = usuario.objects.create_user(ID_empleado='7010', username='dash', password='Pass1234!')
        categoria = activos_categoria.objects.create(codigo='PC', nombre='PC')
        self.activo = activos.objects.create(
            codigo='ETR-01-SUP-PC-0001', categoria=categoria, marca='HP', modelo='Pro', serial='SER-D-1',
            sede=self.sede, departamento=self.depto, usuario_asignado=self.user, estado='activo'
        )
        self.prioridad_alta = matriz_prioridad.objects.create(prioridad='Alta', tiempo_respuesta_minutos=15, tiempo_resolucion_minutos=60)
        self.prioridad_na = matriz_prioridad.objects.create(prioridad='N/A', tiempo_respuesta_minutos=60, tiempo_resolucion_minutos=120)
        tickets.objects.create(
            codigo_ticket='TKT-08001', titulo='Ticket crítico - Sede Principal las Mercedes', descripcion='Desc', prioridad=self.prioridad_alta,
            solicitante=self.user, usuario=self.user, activo_afectado=self.activo, estado='Pendiente'
        )
        tickets.objects.create(
            codigo_ticket='TKT-08002', titulo='Ticket resuelto - Estacion Maracaibo', descripcion='Desc', prioridad=self.prioridad_na,
            solicitante=self.user, usuario=self.user, activo_afectado=self.activo, estado='Resuelto'
        )
        Tutorial.objects.create(
            titulo='Manual dashboard - Sede Principal las Mercedes',
            archivo=SimpleUploadedFile('manual.txt', b'contenido', content_type='text/plain'),
        )

    def test_get_current_usuario_from_session(self):
        request = self.factory.get('/')
        request.session = {'ID_empleado': self.user.ID_empleado}
        request.user = self.user

        current = get_current_usuario(request)
        self.assertEqual(current, self.user)

    def test_build_dashboard_context_contains_expected_kpis(self):
        request = self.factory.get('/')
        request.session = {'ID_empleado': self.user.ID_empleado}
        request.user = self.user

        context = build_dashboard_context(request)

        self.assertEqual(context['kpis']['tickets_totales'], 2)
        self.assertEqual(context['kpis']['tickets_resueltos'], 1)
        self.assertEqual(context['kpis']['documentos_totales'], 1)
        self.assertEqual(len(context['tickets_criticos']), 1)
