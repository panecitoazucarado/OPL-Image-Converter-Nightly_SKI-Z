"""
Clase base para los algoritmos de escalado
"""
from abc import ABC, abstractmethod
from typing import Tuple
from PIL import Image

class BaseScaler(ABC):
    """Clase base abstracta para los algoritmos de escalado"""
    
    @abstractmethod
    def scale(self, image: Image.Image, target_width: int, target_height: int) -> Image.Image:
        """
        Escala una imagen al tamaño objetivo
        
        Args:
            image: Imagen a escalar
            target_width: Ancho objetivo
            target_height: Alto objetivo
            
        Returns:
            Image.Image: Imagen escalada
        """
        pass
    
    def scale_with_aspect(self, 
                         image: Image.Image, 
                         target_width: int, 
                         target_height: int,
                         background_color: Tuple[int, int, int] = (0, 0, 0)) -> Image.Image:
        """
        Escala una imagen manteniendo la relación de aspecto
        
        Args:
            image: Imagen a escalar
            target_width: Ancho objetivo
            target_height: Alto objetivo
            background_color: Color de fondo para rellenar
            
        Returns:
            Image.Image: Imagen escalada con la relación de aspecto mantenida
        """
        # Calcular las dimensiones manteniendo la relación de aspecto
        img_width, img_height = image.size
        aspect_ratio = img_width / img_height
        target_ratio = target_width / target_height

        if aspect_ratio > target_ratio:
            new_width = target_width
            new_height = int(new_width / aspect_ratio)
        else:
            new_height = target_height
            new_width = int(new_height * aspect_ratio)

        # Escalar la imagen
        resized_img = self.scale(image, new_width, new_height)
        
        # Crear una nueva imagen con el tamaño objetivo y el color de fondo
        new_img = Image.new('RGB', (target_width, target_height), background_color)
        
        # Pegar la imagen escalada centrada
        new_img.paste(resized_img, (
            (target_width - new_width) // 2,
            (target_height - new_height) // 2
        ))
        
        return new_img

