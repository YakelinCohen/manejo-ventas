from django.db import models
from django.db.models import Sum
from datetime import date

class VentaManager(models.Manager):
    def ventas_del_dia(self):
        """Retorna las ventas realizadas hoy."""
        return self.filter(fecha_venta__date=date.today())

    def total_ventas_rango(self, fecha_inicio, fecha_fin):
        """Calcula el total de dinero vendido en un rango de fechas."""
        return self.filter(
            fecha_venta__date__range=[fecha_inicio, fecha_fin]
        ).aggregate(total_periodo=Sum('total'))['total_periodo'] or 0
