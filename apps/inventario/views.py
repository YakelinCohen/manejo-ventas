from datetime import date, timedelta
from apps.utils.decorators import validar_payload
from .models import Estante, Lote, Producto,Categoria
from .serializers import EstanteSerializer, LoteSerializer, ProductoSerializer, CategoriaSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class Categorias(APIView):
    def get(self, request):
        categorias = Categoria.objects.all()
        serializer = CategoriaSerializer(categorias, many=True)
        return Response(serializer.data)

    @validar_payload
    def post(self, request):
        '''Crear una nueva categoria'''
        serializer = CategoriaSerializer(data=request.data.get('payload'))   
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class Productos(APIView): 
        
    def get(self, request):
        productos = Producto.objects.all()
        serializer = ProductoSerializer(productos, many=True)
        return Response(serializer.data)

    @validar_payload 
    def post(self, request):
        '''Crear un nuevo producto'''
        serializer = ProductoSerializer(data=request.data.get('payload'))
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoriaProductos(APIView):
    def get(self, request, categoria_id):
        productos = Producto.objects.filter(id_categoria_id=categoria_id)
        serializer = ProductoSerializer(productos, many=True)
        return Response(serializer.data)
    
class Estantes(APIView):
    def get(self, request):
        estantes = Estante.objects.all()
        serializer = EstanteSerializer(estantes, many=True)
        return Response(serializer.data)
    
    @validar_payload
    def post(self, request):
        '''Crear un nuevo estante'''
        serializer = EstanteSerializer(data=request.data.get('payload'))
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class AlertaVencimiento(APIView):
    def get(self, request):
        hoy = date.today()
        proximos_15_dias = hoy + timedelta(days=15)
        
        # Filtramos lotes que vencen pronto y que aún tienen stock
        lotes_en_riesgo = Lote.objects.filter(
            fecha_vencimiento__range=[hoy, proximos_15_dias],
            cantidad__gt=0
        ).order_by('fecha_vencimiento')
        
        serializer = LoteSerializer(lotes_en_riesgo, many=True)
        return Response({
            "conteo": len(serializer.data),
            "payload": serializer.data
        })
    
class Lote(APIView):
    def get(self, request):
        lotes = Lote.objects.all()
        serializer = LoteSerializer(lotes, many=True)
        return Response(serializer.data)

    @validar_payload
    def post(self, request):
        '''Crear un nuevo lote'''
        serializer = LoteSerializer(data=request.data.get('payload'))
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
     
    @validar_payload
    def put(self, request, lote_id):
        '''Actualizar un lote'''        
        try:
            lote = Lote.objects.get(id_lote=lote_id)
        except Lote.DoesNotExist:
            return Response({"error": "Lote no encontrado"}, status=status.HTTP_404_NOT_FOUND)  
        serializer = LoteSerializer(lote, data=request.data.get('payload'), partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @validar_payload
    def post(self, request):
        '''Crear un nuevo lote'''
        serializer = LoteSerializer(data=request.data.get('payload'))
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)