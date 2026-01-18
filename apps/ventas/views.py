from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.utils.decorators import validar_payload
from apps.ventas.models import Cliente, Venta, MetodoPago, EstadoVenta
from apps.ventas.serializers import ClienteSerializer, VentaSerializer, MetodoPagoSerializer, EstadoVentaSerializer, VentaCreateSerializer, PagoVentaSerializer
from apps.ventas.services import VentaService


# Create your views here.
class VentaView(APIView):
    def get(self, request):
        ventas = Venta.objects.all()
        serializer = VentaSerializer(ventas, many=True) 
        return Response(serializer.data)

    @validar_payload
    def post(self, request):    
        '''Crear una nueva venta'''
        try: 
            payload = request.data.get("payload")
            
            # 1. Validar INPUT con el serializer especifico
            validador = VentaCreateSerializer(data=payload)
            validador.is_valid(raise_exception=True)
            
            # 2. Obtener datos validados
            data_validada = validador.validated_data
            
            # 3. Obtener instancia de Cliente (Ya validamos que existe en el serializer)
            cliente = Cliente.objects.get(pk=data_validada['cliente'])

            # 4. Llamar al servicio
            venta = VentaService.crear_venta(
                cliente=cliente,
                detalles_data=data_validada['detalles'],
                pagos_data=data_validada['pagos'],
                observacion=data_validada.get('observacion')
            )

            # 5. Serializar OUTPUT (respuesta completa)
            serializer = VentaSerializer(venta)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

class ClienteView(APIView):
    def get(self, request):
        clientes = Cliente.objects.all()
        serializer = ClienteSerializer(clientes, many=True)
        return Response(serializer.data)

    @validar_payload
    def post(self, request):
        '''Crear un nuevo cliente'''
        serializer = ClienteSerializer(data=request.data.get('payload'))   
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MetodoPagoView(APIView):
    def get(self, request):
        metodos_pago = MetodoPago.objects.all()
        serializer = MetodoPagoSerializer(metodos_pago, many=True)
        return Response(serializer.data)

    @validar_payload
    def post(self, request):
        '''Crear un nuevo metodo de pago'''
        try:
            payload = request.data.get("payload")
            validador = MetodoPagoSerializer(data=payload)
            validador.is_valid(raise_exception=True) 
            validador.save() 
            return Response(validador.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class EstadoVentaView(APIView):
    def get(self, request):
        estados_venta = EstadoVenta.objects.all()
        serializer = EstadoVentaSerializer(estados_venta, many=True)
        return Response(serializer.data)

    @validar_payload
    def post(self, request):
        '''Crear un nuevo estado de venta (soporta uno o varios)'''
        try:
            payload = request.data.get("payload")
            # Detectamos si es una lista para activar many=True
            es_lista = isinstance(payload, list)
            
            validador = EstadoVentaSerializer(data=payload, many=es_lista)
            validador.is_valid(raise_exception=True) 
            validador.save() 
            return Response(validador.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class PagoVentaView(APIView):
    def get(self, request):
        pagos_venta = PagoVenta.objects.all()
        serializer = PagoVentaSerializer(pagos_venta, many=True)
        return Response(serializer.data)

    @validar_payload
    def post(self, request):
        '''Crear un nuevo pago de venta (soporta uno o varios)'''
        try:
            payload = request.data.get("payload")
            es_lista = isinstance(payload, list)
            
            # 1. Validar datos
            validador = PagoVentaSerializer(data=payload, many=es_lista)
            validador.is_valid(raise_exception=True) 
            
            # 2. Agrupar pagos por Venta
            datos_validados = validador.validated_data
            if not es_lista:
                datos_validados = [datos_validados]
            
            pagos_por_venta = {}
            for item in datos_validados:
                venta_id = item['venta'] # El serializer devuelve el ID si es IntegerField o el objeto si es PKRelatedField. Verificamos.
                # En serializer definimos venta = serializers.IntegerField(), asi que es un ID.
                if venta_id not in pagos_por_venta:
                    pagos_por_venta[venta_id] = []
                
                # Preparamos el diccionario como lo espera el servicio
                pagos_por_venta[venta_id].append({
                    'metodo_pago_id': item['metodo_pago'],
                    'moneda_id': item['moneda'],
                    'monto': item['monto']
                })

            # 3. Procesar pagos con el servicio
            ventas_actualizadas = []
            for venta_id, pagos in pagos_por_venta.items():
                venta = VentaService.registrar_pago(venta_id, pagos)
                ventas_actualizadas.append(venta)
            
            # 4. Respuesta
            # Podriamos devolver los IDs de los pagos creados, pero por simplicidad confirmamos OK
            return Response({'mensaje': f'Pagos registrados para {len(ventas_actualizadas)} ventas.', 'ventas_ids': [v.id_venta for v in ventas_actualizadas]}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
