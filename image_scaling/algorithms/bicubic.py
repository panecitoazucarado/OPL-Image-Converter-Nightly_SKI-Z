"""
Implementación del algoritmo de escalado Bicúbico
"""
from PIL import Image
from .base_scaler import BaseScaler

class BicubicScaler(BaseScaler):
    """
    Implementación del algoritmo de escalado Bicúbico
    
    La interpolación bicúbica utiliza los valores de los 16 píxeles más cercanos
    para calcular el valor del nuevo píxel. Produce resultados más suaves que
    la interpolación bilineal y es adecuada para imágenes fotográficas.
    """
    
    def scale(self, image: Image.Image, target_width: int, target_height: int) -> Image.Image:
        """
        Escala una imagen utilizando el algoritmo Bicúbico
        
        Args:
            image: Imagen a escalar
            target_width: Ancho objetivo
            target_height: Alto objetivo
            
        Returns:
            Image.Image: Imagen escalada
        """
        return image.resize((target_width, target_height), Image.BICUBIC)

