import requests
import urllib3
from bs4 import BeautifulSoup
from decimal import Decimal
from .models import TasaCambio, Moneda

# Suppress only the single warning from urllib3 needed.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class MiPropioBCVScraper:
    URL = "https://www.bcv.org.ve/"

    @classmethod
    def obtener_tasa_usd(cls):
        try:
            # 1. Descargar la página con un "User-Agent" para que el servidor no nos bloquee
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
            }
            response = requests.get(cls.URL, headers=headers, verify=False) # verify=False por si hay problemas de SSL en el sitio
            
            # 2. Parsear el contenido HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 3. Buscar el contenedor específico del Dólar
            # El BCV usa el ID 'dolar' para el contenedor del precio
            contenedor_dolar = soup.find('div', id='dolar')
            
            if contenedor_dolar:
                # Extraemos el texto, limpiamos espacios y cambiamos la coma por punto
                texto_precio = contenedor_dolar.find('strong').text.strip()
                precio_limpio = texto_precio.replace(',', '.')
                
                return Decimal(precio_limpio)
            
            return None
        except Exception as e:
            print(f"Error realizando scraping manual: {e}")
            return None

    @classmethod
    def sincronizar(cls):
        valor = cls.obtener_tasa_usd()
        if valor:
            # Buscar o crear la moneda USD
            moneda_usd, _ = Moneda.objects.get_or_create(
                codigo='USD', 
                defaults={'nombre': 'Dolar Estadounidense'}
            )
            
            tasa, _ = TasaCambio.objects.update_or_create(
                moneda=moneda_usd,
                tasa = valor,
                fecha_actualizacion = timezone.now()
            )
            return tasa
        return None