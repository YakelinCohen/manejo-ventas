from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.utils.decorators import validar_payload
from apps.ventas.models import Cliente, Venta
from apps.ventas.serializers import ClienteSerializer, VentaSerializer, MetodoPagoSerializer
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
            validador = VentaSerializer(data=payload)
            validador.is_valid(raise_exception=True)

            venta = VentaService.crear_venta(**payload)

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
