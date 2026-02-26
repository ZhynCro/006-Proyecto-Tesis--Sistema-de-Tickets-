from django.db import models
from django.utils import timezone
from django.utils.text import slugify

import mimetypes
import os
import uuid

def tutorial_upload_path(instance, filename):
    """Genera carpeta por fecha y nombre único para evitar colisiones."""
    _, extension = os.path.splitext(filename)
    extension = extension.lower()
    titulo_slug = slugify(instance.titulo)[:40] if instance.titulo else 'tutorial'
    unique_name = f"{uuid.uuid4()}_{titulo_slug}{extension}"
    now = timezone.now()
    return os.path.join('tutoriales', now.strftime('%Y'), now.strftime('%m'), now.strftime('%d'), unique_name)


class Tutorial(models.Model):
    titulo = models.CharField(max_length=180)
    descripcion = models.TextField(blank=True)
    archivo = models.FileField(upload_to=tutorial_upload_path)
    archivo_path = models.CharField(max_length=255, editable=False, default='')
    nombre_original = models.CharField(max_length=255, editable=False, default='')
    extension = models.CharField(max_length=20, editable=False, default='')
    mime_type = models.CharField(max_length=100, editable=False, default='application/octet-stream')
    tamano_bytes = models.BigIntegerField(editable=False, default=0)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-creado_en']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.archivo:
            archivo_path = self.archivo.name
            nombre_original = getattr(self, 'nombre_original', '') or os.path.basename(archivo_path)
            extension = os.path.splitext(archivo_path)[1].lower()
            guessed_type, _ = mimetypes.guess_type(archivo_path)
            mime_type = guessed_type or 'application/octet-stream'
            tamano_bytes = self.archivo.size

            if (
                self.archivo_path != archivo_path
                or self.nombre_original != nombre_original
                or self.extension != extension
                or self.mime_type != mime_type
                or self.tamano_bytes != tamano_bytes
            ):
                Tutorial.objects.filter(pk=self.pk).update(
                    archivo_path=archivo_path,
                    nombre_original=nombre_original,
                    extension=extension,
                    mime_type=mime_type,
                    tamano_bytes=tamano_bytes,
                )
                self.archivo_path = archivo_path
                self.nombre_original = nombre_original
                self.extension = extension
                self.mime_type = mime_type
                self.tamano_bytes = tamano_bytes

    def __str__(self):
        return self.titulo