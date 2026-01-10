from django.db import models
from django.db.models import F, Sum, Q
from datetime import date, timedelta

class ProductoQuerySet(models.QuerySet):
    """
    Un QuerySet personalizado permite encadenar filtros como:
    Producto.objects.stock_bajo().por_vencer()
    """
    def stock_bajo(self):
        # Filtra productos donde la exhibición es menor o igual al mínimo
        return self.filter(unidades_en_exhibicion__lte=F('cantidad_min_exhibicion'))

    def con_sobrestock_exhibicion(self):
        # Filtra productos que exceden la capacidad del estante
        return self.filter(unidades_en_exhibicion__gt=F('cantidad_max_exhibicion'))

    def por_vencer(self, dias=7):
        # Busca productos que tengan al menos un lote próximo a vencer
        hoy = date.today()
        limite = hoy + timedelta(days=dias)
        return self.filter(
            lotes__fecha_vencimiento__range=[hoy, limite]
        ).distinct()

    def vencidos(self):
        # Busca productos con lotes cuya fecha ya pasó
        return self.filter(lotes__fecha_vencimiento__lt=date.today()).distinct()

class ProductoManager(models.Manager):
    def get_queryset(self):
        return ProductoQuerySet(self.model, using=self._db)

    # Atajos para usar directamente: Producto.objects.stock_bajo()
    def stock_bajo(self):
        return self.get_queryset().stock_bajo()

    def por_vencer(self, dias=7):
        return self.get_queryset().por_vencer(dias)
    
    def vencidos(self):
        return self.get_queryset().vencidos()