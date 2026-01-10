from functools import wraps
from rest_framework.response import Response
from rest_framework import status

def validar_payload(f):
    @wraps(f)
    def decorator(self, request, *args, **kwargs):
        # 1. Validar que la llave 'payload' exista en los datos recibidos

        payload = request.data.get('payload')
        if 'payload' not in request.data:
            return Response(
                {"error": "Estructura incorrecta. Se requiere la llave 'payload'."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 2. Validar que el contenido de payload no sea nulo o esté vacío
        if not request.data.get('payload'):
            return Response(
                {"error": "El contenido de 'payload' no puede estar vacío."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if not isinstance(payload, dict):
            return Response(
                {'error': 'El campo "payload" debe ser un objeto JSON'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return f(self, request, *args, **kwargs)
    return decorator