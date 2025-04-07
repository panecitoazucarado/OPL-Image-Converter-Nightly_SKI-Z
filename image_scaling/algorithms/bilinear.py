"""
Implementación del algoritmo de escalado Bilineal
"""
from PIL import Image
from .base_scaler import BaseScaler

class BilinearScaler(BaseScaler):
    """
    Implementación del algoritmo de escalado Bilineal
    
    La interpolación bilineal utiliza los valores de los 4 píxeles más cercanos
    para calcular el valor del nuevo píxel. Es más rápida que la interpolación
    bicúbica pero produce resultados menos suaves.
    """
    
    def scale(self, image: Image.Image, target_width: int, target_height: int) -> Image.Image:
        """
        Escala una imagen utilizando el algoritmo Bilineal
        
        Args:
            image: Imagen a escalar
            target_width: Ancho objetivo
            target_height: Alto objetivo
            
        Returns:
            Image.Image: Imagen escalada
        """
        return image.resize((target_width, target_height), Image.BILINEAR)

