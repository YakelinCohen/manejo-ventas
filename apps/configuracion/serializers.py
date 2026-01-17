from rest_framework import serializers
from apps.configuracion.models import Moneda, TasaCambio

class MonedaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Moneda
        fields = '__all__'

class TasaCambioSerializer(serializers.ModelSerializer):
    actualizar = serializers.BooleanField(write_only=True,required=True)
    class Meta:
        model = TasaCambio
        fields = ['actualizar']