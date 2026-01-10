from django.db import transaction
from django.core.exceptions import ValidationError
from datetime import date
from apps.inventario.models import EntradaMercancia, Producto, Lote, CodigoBarras

class ProductoService:
    """
    Servicio para manejar la lógica de negocio de Productos.
    Aquí los imports están arriba porque este archivo no define modelos.
    """

    @staticmethod
    def validar_datos_basicos(precio, lotes_data):
        if precio <= 0:
            raise ValidationError("El precio debe ser positivo.")
        
        hoy = date.today()
        for lote in lotes_data:
            if lote['fecha_vencimiento'] < hoy:
                raise ValidationError(f"El lote {lote['codigo']} ya está vencido.")

    @staticmethod
    def registrar_entrada(producto, cantidad):
        """
        Registra una entrada de mercancía de forma segura.
        Busca automáticamente un código de barras asociado para vincular la entrada.
        """
        if cantidad <= 0:
            return

        # Usamos filter().first() para evitar errores si hay 0 o múltiples códigos
        codigo_barras = CodigoBarras.objects.filter(producto=producto).first()
        if codigo_barras:
            EntradaMercancia.objects.create(unidades=cantidad, CodigoBarras=codigo_barras)

    @classmethod
    @transaction.atomic
    def crear_producto_completo(cls, **data):
        # 1. Extraer listas
        lotes_data = data.pop('lotes_data', []) or data.pop('lote_set', [])
        codigos_data = data.pop('codigos_barras_data', []) or data.pop('codigobarras_set', [])

        # 2. Validar
        cls.validar_datos_basicos(data.get('precio'), lotes_data)

        # 3. Crear Producto
        producto = Producto.objects.create(**data)

        # 4. Optimización: BULK CREATE para Códigos de Barras
        if codigos_data:
            codigos_objs = [
                CodigoBarras(producto=producto, codigo=c['codigo']) 
                for c in codigos_data
            ]
            CodigoBarras.objects.bulk_create(codigos_objs)

        # Registrar entrada inicial (suma stock base + stock de lotes si existen)
        # total_unidades = data.get('unidades_stock', 0)
        if lotes_data:
            total_unidades = sum(l['cantidad_disponible'] for l in lotes_data)
        cls.registrar_entrada(producto, total_unidades)

        # 5. Optimización: BULK CREATE para Lotes
        if lotes_data:
            lotes_objs = [
                Lote(
                    producto=producto,
                    codigo=l['codigo'],
                    fecha_expedicion=l['fecha_expedicion'],
                    fecha_vencimiento=l['fecha_vencimiento'],
                    cantidad_disponible=l['cantidad_disponible']
                ) for l in lotes_data
            ]
            Lote.objects.bulk_create(lotes_objs)

        return producto