from django.db import models 

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

# Create your models here.
class Producto(models.Model):
    id_producto = models.AutoField(primary_key=True) 
    descripcion = models.CharField(max_length=255)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    unidades_totales  = models.IntegerField()
    unidades_en_exhibicion = models.IntegerField(default=0)
    cantidad_max_exhibicion = models.IntegerField(default=1)
    cantidad_min_exhibicion = models.IntegerField(default=1)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    categoria = models.ForeignKey('Categoria', on_delete=models.PROTECT, null=True)
    nivel = models.ForeignKey('Nivel', on_delete=models.PROTECT, related_name='ubicacion', null=True) 

    @property
    def unidades_en_bodega(self):
        # El resto siempre está en el almacén
        return self.unidades_totales - self.unidades_en_exhibicion

    @property
    def necesita_reposicion(self):
        # Si lo que hay en exhibición es menor o igual al mínimo
        return self.unidades_en_exhibicion <= self.cantidad_min_exhibicion

    def __str__(self):
        return self.descripcion
    
    class Meta:
        db_table = 'in_producto'