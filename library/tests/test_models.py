from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from library.models import Tutorial


@override_settings(MEDIA_ROOT='/tmp/django_test_media_library_models')
class LibraryModelTests(TestCase):
    def test_tutorial_save_populates_metadata_and_str(self):
        file_obj = SimpleUploadedFile('manual.txt', b'contenido', content_type='text/plain')

        tutorial = Tutorial.objects.create(titulo='Manual operativo - Estacion Maiquetia', archivo=file_obj)

        self.assertEqual(str(tutorial), 'Manual operativo - Estacion Maiquetia')
        self.assertTrue(tutorial.archivo_path)
        self.assertEqual(tutorial.extension, '.txt')
        self.assertEqual(tutorial.mime_type, 'text/plain')
        self.assertGreater(tutorial.tamano_bytes, 0)
