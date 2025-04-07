"""
Implementación del algoritmo de escalado Lanczos
"""
from PIL import Image
from .base_scaler import BaseScaler

class LanczosScaler(BaseScaler):
    """
    Implementación del algoritmo de escalado Lanczos
    
    El filtro Lanczos es un filtro de reconstrucción de alta calidad que produce
    imágenes nítidas con menos artefactos que otros algoritmos. Es computacionalmente
    más intensivo pero produce resultados de alta calidad.
    """
    
    def __init__(self, a: int = 3):
        """
        Inicializa el escalador Lanczos
        
        Args:
            a: Parámetro 'a' del filtro Lanczos (tamaño del lóbulo)
        """
        self.a = a
    
    def scale(self, image: Image.Image, target_width: int, target_height: int) -> Image.Image:
        """
        Escala una imagen utilizando el algoritmo Lanczos
        
        Args:
            image: Imagen a escalar
            target_width: Ancho objetivo
            target_height: Alto objetivo
            
        Returns:
            Image.Image: Imagen escalada
        """
        return image.resize((target_width, target_height), Image.LANCZOS)

