import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from library.models import Tutorial
from users.models import usuario


@override_settings(MEDIA_ROOT=tempfile.gettempdir())
class LibraryViewsTests(TestCase):
    def setUp(self):
        self.user = usuario.objects.create_user(ID_empleado='6010', username='libadmin', password='Pass1234!')
        self.tutorial = Tutorial.objects.create(
            titulo='Documento base - Estacion Barinas',
            archivo=SimpleUploadedFile('base.txt', b'texto', content_type='text/plain'),
        )

    def test_library_view_requires_authentication(self):
        response = self.client.get(reverse('library_view'))
        self.assertEqual(response.status_code, 302)

    def test_library_create_post_valid_redirects(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('library_create'),
            data={
                'titulo': 'Documento nuevo - Estacion Porlamar',
                'descripcion': 'Desc',
                'archivo': SimpleUploadedFile('nuevo.pdf', b'%PDF-1.4', content_type='application/pdf'),
            },
        )
        self.assertRedirects(response, reverse('library_view'))
        self.assertTrue(Tutorial.objects.filter(titulo='Documento nuevo - Estacion Porlamar').exists())

    def test_library_download_without_file_returns_404(self):
        self.client.force_login(self.user)
        self.tutorial.archivo.delete(save=True)

        response = self.client.get(reverse('library_download', args=[self.tutorial.pk]))
        self.assertEqual(response.status_code, 404)
