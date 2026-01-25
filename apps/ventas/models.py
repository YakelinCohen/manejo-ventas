from pyclbr import Class
from django.db import models
from apps.ventas.managers import VentaManager

# Create your models here.
class Cliente(models.Model):
    id_cliente = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255, null=False)
    apellido = models.CharField(max_length=255, null=False)
    direccion = models.CharField(max_length=255, null=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)

    def save(self, *args, **kwargs):
        # Normalizar texto: elimina espacios extra y convierte a formato Título
        if self.nombre:
            self.nombre = self.nombre.strip().title()
        if self.apellido:
            self.apellido = self.apellido.strip().title()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.nombre} {self.apellido}'
    
    class Meta:
        db_table = 've_cliente'
        unique_together = ('nombre', 'apellido')

class Venta(models.Model):
    id_venta = models.AutoField(primary_key=True)
    fecha_venta = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    cliente = models.ForeignKey('Cliente', on_delete=models.DO_NOTHING)
    observacion = models.CharField(max_length=255, blank=True, null=True)
    estado = models.ForeignKey('EstadoVenta', on_delete=models.DO_NOTHING)

    objects = VentaManager()

    def __str__(self):
        return f'Venta {self.id_venta} - Cliente: {self.cliente.nombre} - Total: {self.total}'
        
    @property
    def tiene_pago_pendiente(self):
        # Esto funciona como tu booleano, pero es automático
        return self.estado.id_estado_venta == 1

    class Meta:
            db_table = 've_venta'

class MetodoPago(models.Model):
    id_metodo_pago = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255, unique=True, null=False) 

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 've_metodo_pago'

class PagoVenta(models.Model):
    id_pago_venta = models.AutoField(primary_key=True)
    venta = models.ForeignKey('Venta', on_delete=models.DO_NOTHING)
    monto = models.DecimalField(max_digits=10, decimal_places=2) 
    fecha_pago = models.DateTimeField(auto_now_add=True)
    metodo_pago = models.ForeignKey('MetodoPago', on_delete=models.DO_NOTHING)
    moneda = models.ForeignKey('configuracion.Moneda', on_delete=models.DO_NOTHING) 

    def __str__(self):
        return f'Pago {self.id_pago_venta} - Venta: {self.venta.id_venta} - Monto: {self.monto}'

    class Meta:
        db_table = 've_pago_venta'

class EstadoVenta(models.Model):
    id_estado_venta = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255, unique=True, null=False) 

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 've_estado_venta'    

class DetalleVenta(models.Model):
    id_detalle_venta = models.AutoField(primary_key=True)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    venta = models.ForeignKey('Venta', on_delete=models.DO_NOTHING)
    producto = models.ForeignKey('inventario.Producto', on_delete=models.DO_NOTHING)    

    class Meta:
        db_table = 've_detalle_venta'   