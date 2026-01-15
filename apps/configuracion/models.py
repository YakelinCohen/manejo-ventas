from django.db import models

# Create your models here.
class Moneda(models.Model):
    id_moneda = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=10, unique=True, null=False)
    nombre = models.CharField(max_length=100, null=False)
    simbolo = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return f'{self.nombre} ({self.codigo})'

    class Meta:
        db_table = 'co_moneda'

class TasaCambio(models.Model):
    id_tasa_cambio = models.AutoField(primary_key=True)
    moneda= models.ForeignKey('Moneda', on_delete=models.DO_NOTHING)  
    tasa = models.DecimalField(max_digits=10, decimal_places=4)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Tasa de {self.moneda.codigo}  : {self.tasa}'

    class Meta:
        db_table = 'co_tasa_cambio'