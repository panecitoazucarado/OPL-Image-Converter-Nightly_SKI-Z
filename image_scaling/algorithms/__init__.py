"""
Paquete de algoritmos de escalado
"""
from .base_scaler import BaseScaler
from .lanczos import LanczosScaler
from .bicubic import BicubicScaler
from .bilinear import BilinearScaler
from .nearest import NearestScaler
from .box import BoxScaler
from .hamming import HammingScaler
from .ps2_optimized import PS2OptimizedScaler

__all__ = [
    'BaseScaler',
    'LanczosScaler',
    'BicubicScaler',
    'BilinearScaler',
    'NearestScaler',
    'BoxScaler',
    'HammingScaler',
    'PS2OptimizedScaler'
]

