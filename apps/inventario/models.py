from django.db import models 
from .managers import ProductoManager

class Categoria(models.Model):
    id_categoria = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100,unique=True)
    descripcion = models.CharField(max_length=255, blank=True, null=True) 

    class Meta:
        db_table = 'in_categoria'

class Estante(models.Model):    
    id_estante = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    cantidad_niveles = models.IntegerField(
        default=1, 
        help_text="¿Cuántos niveles tiene este estante?",
        verbose_name="Cantidad de niveles"
    )

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        # Primero guardamos el estante para tener un ID
        nuevo_estante = not self.pk
        super().save(*args, **kwargs)
        
        # Si es la primera vez que se crea, generamos los niveles
        if nuevo_estante:
            for i in range(1, self.cantidad_niveles + 1):
                Nivel.objects.get_or_create(estante=self, numero=i)

    class Meta:
        db_table = 'in_estante'

class Nivel(models.Model):
    id_nivel = models.AutoField(primary_key=True)
    numero = models.IntegerField()
    estante = models.ForeignKey('Estante', on_delete=models.CASCADE)

    def __str__(self):
        return f'Estante: {self.estante.nombre} - Nivel: {self.numero}'
    

    class Meta:
        db_table = 'in_nivel'
        unique_together = ('numero', 'estante')

#Los lotes se deben ingresar en el estantes por orden de vencimiento, el primero en vencer debe ser el primero en salir
class Lote(models.Model):
    id_lote = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=100)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    fecha_expedicion  = models.DateField()
    fecha_vencimiento = models.DateField() 
    cantidad_disponible = models.IntegerField()
    producto = models.ForeignKey('Producto', on_delete=models.DO_NOTHING)

    def __str__(self):
        return f"{self.producto.nombre} - Lote: {self.codigo}"

    class Meta:
        db_table = 'in_lote'
        unique_together = ('producto', 'codigo', 'fecha_vencimiento')

class CodigoBarras(models.Model):
    id_codigo = models.AutoField(primary_key=True)
    codigo = models.CharField(
        max_length=50, 
        blank=True, 
        null=True, 
        unique=True,
        help_text="Escanea el código de barras aquí"
    )
    producto = models.ForeignKey('Producto', on_delete=models.DO_NOTHING)

    def __str__(self):
        return f"{self.codigo} - Producto: {self.producto.descripcion}"

    class Meta:
        db_table = 'in_codigo_barras'

class EntradaMercancia(models.Model):
    id_entrada_mercancia = models.AutoField(primary_key=True)
    unidades = models.IntegerField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    CodigoBarras = models.ForeignKey('CodigoBarras', on_delete=models.DO_NOTHING)

    class Meta:
        db_table = "in_entrada_mercancia"

class Producto(models.Model):
    id_producto = models.AutoField(primary_key=True) 
    descripcion = models.CharField(
        max_length=255, 
        unique=True, 
        verbose_name="Descripción del Producto"
    )
    precio = models.DecimalField(max_digits=10, decimal_places=2) 
    unidades_stock = models.IntegerField(default=0, help_text="Total de unidades (usado cuando no requiere lotes)")
    unidades_en_exhibicion = models.IntegerField(default=0)
    cantidad_max_exhibicion = models.IntegerField(default=1)
    cantidad_min_exhibicion = models.IntegerField(default=1)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    requiere_lotes = models.BooleanField(default=True)
    categoria = models.ForeignKey('Categoria', on_delete=models.PROTECT, null=True)
    nivel = models.ForeignKey('Nivel', on_delete=models.PROTECT, related_name='ubicacion', null=True)  

    objects = ProductoManager()

    @property
    def unidades_totales(self):
        if not self.requiere_lotes:
            return self.unidades_stock
        # Si requiere lotes, suma de lotes
        return self.lotes.aggregate(total=models.Sum('cantidad_disponible'))['total'] or 0

    @property
    def unidades_en_bodega(self):
        # Calculado: Total de lotes menos lo que ya sacaste a exhibición
        return self.unidades_totales - self.unidades_en_exhibicion

    @property
    def necesita_reposicion(self):
        # Lógica de estante: ¿hay que traer más de la bodega?
        return self.unidades_en_exhibicion <= self.cantidad_min_exhibicion

    def __str__(self):
        return self.descripcion
    
    class Meta:
        db_table = 'in_producto'