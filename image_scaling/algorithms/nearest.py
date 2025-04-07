"""
Implementación del algoritmo de escalado Vecino más cercano
"""
from PIL import Image
from .base_scaler import BaseScaler

class NearestScaler(BaseScaler):
    """
    Implementación del algoritmo de escalado Vecino más cercano
    
    Este método selecciona el valor del píxel más cercano en la imagen original
    para cada píxel en la imagen redimensionada. Es el método más rápido pero
    produce resultados con bordes dentados y pixelados.
    """
    
    def scale(self, image: Image.Image, target_width: int, target_height: int) -> Image.Image:
        """
        Escala una imagen utilizando el algoritmo Vecino más cercano
        
        Args:
            image: Imagen a escalar
            target_width: Ancho objetivo
            target_height: Alto objetivo
            
        Returns:
            Image.Image: Imagen escalada
        """
        return image.resize((target_width, target_height), Image.NEAREST)

