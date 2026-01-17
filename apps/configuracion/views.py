from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.utils.decorators import validar_payload
from apps.configuracion.models import Moneda, TasaCambio
from apps.configuracion.serializers import MonedaSerializer, TasaCambioSerializer
from apps.configuracion.services import MiPropioBCVScraper

# Create your views here.
class MonedaView(APIView):
    def get(self, request):
        monedas = Moneda.objects.all()
        serializer = MonedaSerializer(monedas, many=True)
        return Response(serializer.data)

    @validar_payload
    def post(self, request):
        try:
            payload = request.data.get("payload")
            validador = MonedaSerializer(data=payload)
            validador.is_valid(raise_exception=True) 
            validador.save() 
            return Response(validador.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ActualizarTasaAPIView(APIView):
    def get(self, request):
        tasas_cambio = TasaCambio.objects.all()
        serializer = TasaCambioSerializer(tasas_cambio, many=True)
        return Response(serializer.data)

    @validar_payload
    def post(self, request):
        try:
            payload = request.data.get("payload")
            validador = TasaCambioSerializer(data=payload)
            validador.is_valid(raise_exception=True) 
            tasa_cambio = MiPropioBCVScraper.sincronizar()
        
            if tasa_cambio:
                return Response({
                    "mensaje": "Tasa actualizada exitosamente",
                    "monto": tasa_cambio.tasa,
                    "fecha": tasa_cambio.fecha_actualizacion.strftime("%d/%m/%Y %H:%M:%S")
                }, status=status.HTTP_200_OK)
            
            return Response({
                "error": "No se pudo conectar con el BCV. Intente más tarde."
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)