
from django.db import models

class Desperdicio(models.Model):
    fecha = models.DateField()
    peso = models.FloatField()
    hotel = models.CharField(max_length=255)
    tipo = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.hotel} - {self.tipo} - {self.fecha}"
