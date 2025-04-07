"""
Gestor de algoritmos de escalado para OPL Image Converter
Este módulo proporciona una interfaz unificada para diferentes algoritmos de escalado
"""
import os
import logging
from typing import Dict, List, Tuple, Optional, Callable
from enum import Enum
from PIL import Image

# Importar los algoritmos de escalado
from .algorithms.lanczos import LanczosScaler
from .algorithms.bicubic import BicubicScaler
from .algorithms.bilinear import BilinearScaler
from .algorithms.nearest import NearestScaler
from .algorithms.box import BoxScaler
from .algorithms.hamming import HammingScaler
from .algorithms.ps2_optimized import PS2OptimizedScaler

logger = logging.getLogger(__name__)

class ScalingMethod(Enum):
    """Enumeración de métodos de escalado disponibles"""
    LANCZOS = "lanczos"
    BICUBIC = "bicubic"
    BILINEAR = "bilinear"
    NEAREST = "nearest"
    BOX = "box"
    HAMMING = "hamming"
    PS2_OPTIMIZED = "ps2_optimized"

class ScalingManager:
    """Gestor de algoritmos de escalado para imágenes"""
    
    _instance = None
    
    def __new__(cls):
        """Implementación del patrón Singleton para asegurar una única instancia"""
        if cls._instance is None:
            cls._instance = super(ScalingManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Inicializa el gestor de escalado"""
        # Evitar reinicialización si ya está inicializado (Singleton)
        if getattr(self, '_initialized', False):
            return
            
        self._initialized = True
        
        # Inicializar los algoritmos de escalado
        self.scalers = {
            ScalingMethod.LANCZOS: LanczosScaler(),
            ScalingMethod.BICUBIC: BicubicScaler(),
            ScalingMethod.BILINEAR: BilinearScaler(),
            ScalingMethod.NEAREST: NearestScaler(),
            ScalingMethod.BOX: BoxScaler(),
            ScalingMethod.HAMMING: HammingScaler(),
            ScalingMethod.PS2_OPTIMIZED: PS2OptimizedScaler()
        }
        
        # Método de escalado predeterminado
        self.default_method = ScalingMethod.LANCZOS
        self.current_method = self.default_method
    
    def get_available_methods(self) -> List[Tuple[ScalingMethod, str]]:
        """
        Obtiene la lista de métodos de escalado disponibles
        
        Returns:
            List[Tuple[ScalingMethod, str]]: Lista de tuplas (método, nombre descriptivo)
        """
        return [
            (ScalingMethod.LANCZOS, "Lanczos (Alta calidad)"),
            (ScalingMethod.BICUBIC, "Bicúbico (Buena calidad)"),
            (ScalingMethod.BILINEAR, "Bilineal (Calidad media)"),
            (ScalingMethod.NEAREST, "Vecino más cercano (Rápido)"),
            (ScalingMethod.BOX, "Box (Suavizado)"),
            (ScalingMethod.HAMMING, "Hamming (Detalle)"),
            (ScalingMethod.PS2_OPTIMIZED, "Optimizado para PS2 (Recomendado)")
        ]
    
    def set_scaling_method(self, method: ScalingMethod) -> bool:
        """
        Establece el método de escalado actual
        
        Args:
            method: Método de escalado a establecer
            
        Returns:
            bool: True si se estableció correctamente, False en caso contrario
        """
        if method in self.scalers:
            self.current_method = method
            return True
        return False
    
    def get_current_method(self) -> ScalingMethod:
        """
        Obtiene el método de escalado actual
        
        Returns:
            ScalingMethod: Método de escalado actual
        """
        return self.current_method
    
    def scale_image(self, 
                   image: Image.Image, 
                   target_width: int, 
                   target_height: int, 
                   method: Optional[ScalingMethod] = None,
                   maintain_aspect: bool = True,
                   background_color: Tuple[int, int, int] = (0, 0, 0)) -> Image.Image:
        """
        Escala una imagen utilizando el método especificado
        
        Args:
            image: Imagen a escalar
            target_width: Ancho objetivo
            target_height: Alto objetivo
            method: Método de escalado a utilizar (opcional, usa el actual si no se especifica)
            maintain_aspect: Si se debe mantener la relación de aspecto
            background_color: Color de fondo para rellenar si se mantiene la relación de aspecto
            
        Returns:
            Image.Image: Imagen escalada
        """
        # Usar el método actual si no se especifica uno
        if method is None:
            method = self.current_method
        
        # Verificar que el método existe
        if method not in self.scalers:
            logger.warning(f"Método de escalado {method} no disponible, usando {self.default_method}")
            method = self.default_method
        
        # Obtener el escalador correspondiente
        scaler = self.scalers[method]
        
        try:
            # Escalar la imagen
            if maintain_aspect:
                return scaler.scale_with_aspect(image, target_width, target_height, background_color)
            else:
                return scaler.scale(image, target_width, target_height)
        except Exception as e:
            logger.error(f"Error al escalar la imagen con el método {method}: {str(e)}")
            # Intentar con el método predeterminado en caso de error
            if method != self.default_method:
                logger.info(f"Intentando escalar con el método predeterminado {self.default_method}")
                return self.scale_image(image, target_width, target_height, self.default_method, maintain_aspect, background_color)
            else:
                # Si ya estamos usando el método predeterminado, propagar el error
                raise

