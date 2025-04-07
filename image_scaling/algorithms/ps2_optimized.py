"""
Implementación de un algoritmo de escalado optimizado para PS2
"""
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance
from .base_scaler import BaseScaler

class PS2OptimizedScaler(BaseScaler):
    """
    Implementación de un algoritmo de escalado optimizado para PS2
    
    Este algoritmo está diseñado específicamente para producir imágenes
    que se vean bien en la PlayStation 2, teniendo en cuenta sus limitaciones
    de hardware y características de visualización.
    """
    
    def scale(self, image: Image.Image, target_width: int, target_height: int) -> Image.Image:
        """
        Escala una imagen utilizando un algoritmo optimizado para PS2
        
        Args:
            image: Imagen a escalar
            target_width: Ancho objetivo
            target_height: Alto objetivo
            
        Returns:
            Image.Image: Imagen escalada optimizada para PS2
        """
        # Convertir a RGB si es necesario
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Paso 1: Aplicar un filtro de nitidez para mejorar los detalles
        image = image.filter(ImageFilter.SHARPEN)
        
        # Paso 2: Redimensionar usando Lanczos para mantener la calidad
        resized = image.resize((target_width, target_height), Image.LANCZOS)
        
        # Paso 3: Ajustar el contraste ligeramente para compensar la pantalla CRT
        enhancer = ImageEnhance.Contrast(resized)
        resized = enhancer.enhance(1.1)  # Aumentar contraste en un 10%
        
        # Paso 4: Ajustar la saturación para que los colores se vean mejor en PS2
        enhancer = ImageEnhance.Color(resized)
        resized = enhancer.enhance(1.15)  # Aumentar saturación en un 15%
        
        # Paso 5: Aplicar una ligera reducción de ruido para evitar artefactos
        resized = resized.filter(ImageFilter.SMOOTH_MORE)
        
        # Paso 6: Optimizar para la paleta de colores de PS2 (16-bit color)
        # Convertir a array numpy para manipulación de píxeles
        try:
            img_array = np.array(resized)
            
            # Redondear los valores de color a los niveles de 5-6-5 bits (RGB)
            r = np.round(img_array[:, :, 0] / 8) * 8
            g = np.round(img_array[:, :, 1] / 4) * 4
            b = np.round(img_array[:, :, 2] / 8) * 8
            
            # Reconstruir la imagen
            img_array[:, :, 0] = r
            img_array[:, :, 1] = g
            img_array[:, :, 2] = b
            
            # Convertir de nuevo a imagen PIL
            optimized = Image.fromarray(img_array.astype('uint8'), 'RGB')
            return optimized
        except Exception as e:
            # Si hay un error con numpy, devolver la imagen sin este paso
            import logging
            logging.warning(f"Error en optimización de color para PS2: {str(e)}")
            return resized

