"""
Implementación del algoritmo de escalado Hamming
"""
from PIL import Image
from .base_scaler import BaseScaler

class HammingScaler(BaseScaler):
    """
    Implementación del algoritmo de escalado Hamming
    
    Este método utiliza un filtro de ventana Hamming para redimensionar la imagen.
    Produce resultados con buen detalle y menos artefactos que otros métodos.
    """
    
    def scale(self, image: Image.Image, target_width: int, target_height: int) -> Image.Image:
        """
        Escala una imagen utilizando el algoritmo Hamming
        
        Args:
            image: Imagen a escalar
            target_width: Ancho objetivo
            target_height: Alto objetivo
            
        Returns:
            Image.Image: Imagen escalada
        """
        return image.resize((target_width, target_height), Image.HAMMING)

