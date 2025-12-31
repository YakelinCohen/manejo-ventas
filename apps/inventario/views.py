from apps.utils.decorators import validar_payload
from .models import Estante, Producto,Categoria
from .serializers import EstanteSerializer, ProductoSerializer, CategoriaSerializer
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