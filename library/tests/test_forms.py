from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from library.forms import TutorialForm


class TutorialFormTests(TestCase):
    def test_given_valid_pdf_when_form_validate_then_valid(self):
        form = TutorialForm(
            data={'titulo': 'Guia tecnica - Estacion San Antonio', 'descripcion': 'Documento'},
            files={'archivo': SimpleUploadedFile('guia.pdf', b'%PDF-1.4', content_type='application/pdf')},
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_given_invalid_extension_when_form_validate_then_error(self):
        form = TutorialForm(
            data={'titulo': 'Guia tecnica - Estacion San Antonio', 'descripcion': 'Documento'},
            files={'archivo': SimpleUploadedFile('guia.exe', b'binario', content_type='application/octet-stream')},
        )
        self.assertFalse(form.is_valid())
        self.assertIn('archivo', form.errors)
