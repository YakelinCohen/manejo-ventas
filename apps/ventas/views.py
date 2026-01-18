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

