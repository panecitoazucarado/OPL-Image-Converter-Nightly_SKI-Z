"""
Implementación del algoritmo de escalado Box
"""
from PIL import Image
from .base_scaler import BaseScaler

class BoxScaler(BaseScaler):
    """
    Implementación del algoritmo de escalado Box
    
    Este método utiliza un filtro de caja para redimensionar la imagen.
    Es adecuado para reducir el tamaño de una imagen y produce resultados
    suavizados.
    """
    
    def scale(self, image: Image.Image, target_width: int, target_height: int) -> Image.Image:
        """
        Escala una imagen utilizando el algoritmo Box
        
        Args:
            image: Imagen a escalar
            target_width: Ancho objetivo
            target_height: Alto objetivo
            
        Returns:
            Image.Image: Imagen escalada
        """
        return image.resize((target_width, target_height), Image.BOX)

