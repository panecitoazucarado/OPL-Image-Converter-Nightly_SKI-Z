"""
Procesador de imágenes mejorado con soporte para múltiples algoritmos de escalado
"""
import os
import logging
from typing import Dict, List, Tuple, Optional
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np

logger = logging.getLogger(__name__)

class ImageProcessorEnhanced:
    """Clase para procesamiento de imágenes con soporte para múltiples algoritmos de escalado"""
    
    DIMENSIONS = {
        "caratula": (140, 200),
        "borde": (18, 240),
        "contracaratula": (242, 344),
        "captura": (250, 168),
        "fondo": (640, 480),
        "disco": (128, 128),
        "logo": (300, 125)
    }
    
    # Mapeo de algoritmos a métodos de PIL
    ALGORITHM_METHODS = {
        "lanczos": Image.LANCZOS,
        "bicubic": Image.BICUBIC,
        "bilinear": Image.BILINEAR,
        "nearest": Image.NEAREST,
        "box": Image.BOX,
        "hamming": Image.HAMMING
    }

    @staticmethod
    def is_supported_format(file_path: str) -> bool:
        """
        Verifica si un archivo tiene un formato de imagen soportado
        
        Args:
            file_path: Ruta del archivo a verificar
            
        Returns:
            bool: True si el formato es soportado, False en caso contrario
        """
        # Importar desde el módulo principal para evitar dependencias circulares
        from opl_image_converter_pyqt import SUPPORTED_FORMATS
        return os.path.splitext(file_path)[1].lower() in SUPPORTED_FORMATS

    def convert_resize_image(self, 
                           input_path: str, 
                           output_path: str, 
                           image_type: str,
                           maintain_aspect: bool = True,
                           algorithm: str = "lanczos",
                           enhance_contrast: bool = False,
                           sharpen: bool = False) -> Tuple[bool, str]:
        """
        Convierte y redimensiona una imagen según las especificaciones
        
        Args:
            input_path: Ruta de la imagen de entrada
            output_path: Ruta de la imagen de salida
            image_type: Tipo de imagen (caratula, borde, etc.)
            maintain_aspect: Si se debe mantener la relación de aspecto
            algorithm: Algoritmo de escalado a utilizar
            enhance_contrast: Si se debe mejorar el contraste
            sharpen: Si se debe aplicar un filtro de nitidez
            
        Returns:
            Tuple[bool, str]: (éxito, ruta de salida o mensaje de error)
        """
        try:
            with Image.open(input_path) as img:
                if img.mode != 'RGB':
                    img = img.convert('RGB')

                # Obtener dimensiones objetivo
                target_width, target_height = self.DIMENSIONS.get(image_type, (0, 0))
                if not target_width or not target_height:
                    raise ValueError(f"Tipo de imagen inválido: {image_type}")

                # Aplicar escalado con el algoritmo seleccionado
                if algorithm == "ps2_optimized":
                    scaled_img = self._resize_ps2_optimized(img, target_width, target_height, maintain_aspect)
                else:
                    # Usar el método de PIL correspondiente al algoritmo
                    resize_method = self.ALGORITHM_METHODS.get(algorithm, Image.LANCZOS)
                    
                    if maintain_aspect:
                        scaled_img = self._resize_with_aspect(img, target_width, target_height, resize_method)
                    else:
                        scaled_img = img.resize((target_width, target_height), resize_method)
                
                # Aplicar mejoras adicionales si se solicitan
                if enhance_contrast:
                    enhancer = ImageEnhance.Contrast(scaled_img)
                    scaled_img = enhancer.enhance(1.2)  # Aumentar contraste en un 20%
                
                if sharpen:
                    scaled_img = scaled_img.filter(ImageFilter.SHARPEN)

                # Guardar la imagen procesada
                scaled_img.save(output_path, 'PNG', optimize=True)
                return True, output_path
        except Exception as e:
            logger.error(f"Error procesando {input_path}: {str(e)}")
            return False, str(e)

    def get_preview(self, 
                   image_path: str, 
                   image_type: str, 
                   maintain_aspect: bool = True,
                   algorithm: str = "lanczos",
                   enhance_contrast: bool = False,
                   sharpen: bool = False,
                   max_preview_size: Tuple[int, int] = (300, 300)) -> Optional[Image.Image]:
        """
        Genera una vista previa de la imagen procesada
        
        Args:
            image_path: Ruta de la imagen original
            image_type: Tipo de imagen a procesar
            maintain_aspect: Si se debe mantener la relación de aspecto
            algorithm: Algoritmo de escalado a utilizar
            enhance_contrast: Si se debe mejorar el contraste
            sharpen: Si se debe aplicar un filtro de nitidez
            max_preview_size: Tamaño máximo de la vista previa
            
        Returns:
            Optional[Image.Image]: Imagen de vista previa o None si hay error
        """
        try:
            with Image.open(image_path) as img:
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Obtener dimensiones objetivo
                target_width, target_height = self.DIMENSIONS.get(image_type, (0, 0))
                if not target_width or not target_height:
                    raise ValueError(f"Tipo de imagen inválido: {image_type}")
                
                # Aplicar escalado con el algoritmo seleccionado
                if algorithm == "ps2_optimized":
                    processed_img = self._resize_ps2_optimized(img, target_width, target_height, maintain_aspect)
                else:
                    # Usar el método de PIL correspondiente al algoritmo
                    resize_method = self.ALGORITHM_METHODS.get(algorithm, Image.LANCZOS)
                    
                    if maintain_aspect:
                        processed_img = self._resize_with_aspect(img, target_width, target_height, resize_method)
                    else:
                        processed_img = img.resize((target_width, target_height), resize_method)
                
                # Aplicar mejoras adicionales si se solicitan
                if enhance_contrast:
                    enhancer = ImageEnhance.Contrast(processed_img)
                    processed_img = enhancer.enhance(1.2)  # Aumentar contraste en un 20%
                
                if sharpen:
                    processed_img = processed_img.filter(ImageFilter.SHARPEN)
                
                # Redimensionar para la vista previa
                preview_width, preview_height = max_preview_size
                processed_img.thumbnail((preview_width, preview_height))
                
                return processed_img
        except Exception as e:
            logger.error(f"Error generando vista previa de {image_path}: {str(e)}")
            return None

    def _resize_with_aspect(self, 
                           img: Image.Image, 
                           target_width: int, 
                           target_height: int,
                           resize_method: int = Image.LANCZOS) -> Image.Image:
        """
        Redimensiona manteniendo la relación de aspecto con bordes negros
        
        Args:
            img: Imagen a redimensionar
            target_width: Ancho objetivo
            target_height: Alto objetivo
            resize_method: Método de redimensionamiento de PIL
            
        Returns:
            Image.Image: Imagen redimensionada
        """
        img_width, img_height = img.size
        aspect_ratio = img_width / img_height
        target_ratio = target_width / target_height

        if aspect_ratio > target_ratio:
            new_width = target_width
            new_height = int(new_width / aspect_ratio)
        else:
            new_height = target_height
            new_width = int(new_height * aspect_ratio)

        resized_img = img.resize((new_width, new_height), resize_method)
        new_img = Image.new('RGB', (target_width, target_height), (0, 0, 0))
        new_img.paste(resized_img, (
            (target_width - new_width) // 2,
            (target_height - new_height) // 2
        ))
        return new_img

    def _resize_ps2_optimized(self, 
                             img: Image.Image, 
                             target_width: int, 
                             target_height: int,
                             maintain_aspect: bool = True) -> Image.Image:
        """
        Redimensiona una imagen con optimizaciones específicas para PS2
        
        Args:
            img: Imagen a redimensionar
            target_width: Ancho objetivo
            target_height: Alto objetivo
            maintain_aspect: Si se debe mantener la relación de aspecto
            
        Returns:
            Image.Image: Imagen redimensionada optimizada para PS2
        """
        # Paso 1: Aplicar un filtro de nitidez para mejorar los detalles
        img = img.filter(ImageFilter.SHARPEN)
        
        # Paso 2: Redimensionar usando Lanczos para mantener la calidad
        if maintain_aspect:
            resized = self._resize_with_aspect(img, target_width, target_height, Image.LANCZOS)
        else:
            resized = img.resize((target_width, target_height), Image.LANCZOS)
        
        # Paso 3: Ajustar el contraste ligeramente para compensar la pantalla CRT
        try:
            enhancer = ImageEnhance.Contrast(resized)
            resized = enhancer.enhance(1.1)  # Aumentar contraste en un 10%
        except Exception as e:
            logger.warning(f"Error al ajustar contraste: {str(e)}")
        
        # Paso 4: Ajustar la saturación para que los colores se vean mejor en PS2
        try:
            enhancer = ImageEnhance.Color(resized)
            resized = enhancer.enhance(1.15)  # Aumentar saturación en un 15%
        except Exception as e:
            logger.warning(f"Error al ajustar saturación: {str(e)}")
        
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
            logger.warning(f"Error en optimización de color para PS2: {str(e)}")
            return resized

