"""
Conector entre la interfaz de usuario y el sistema de escalado de imágenes
"""
import os
from typing import Dict, List, Tuple, Optional, Callable
from PyQt5.QtWidgets import (
    QComboBox, QGroupBox, QVBoxLayout, QLabel, QWidget
)
from PyQt5.QtCore import pyqtSignal, QObject

from .scaling_manager import ScalingManager, ScalingMethod

# Señal personalizada para cambio de método de escalado
class ScalingMethodChangedSignal(QObject):
    method_changed = pyqtSignal(ScalingMethod)

# Variable global para la señal de método de escalado
scaling_signal = ScalingMethodChangedSignal()

class ScalingMethodSelector(QGroupBox):
    """Widget selector de método de escalado para la interfaz de usuario"""
    
    def __init__(self, parent=None, language_manager=None):
        """
        Inicializa el selector de método de escalado
        
        Args:
            parent: Widget padre
            language_manager: Gestor de idiomas (opcional)
        """
        # Obtener el título del grupo según el idioma
        title = "Método de Escalado"
        if language_manager:
            title = language_manager.get_text("scaling_method", "Método de Escalado")
            
        super().__init__(title, parent)
        
        # Inicializar el gestor de escalado
        self.scaling_manager = ScalingManager()
        self.language_manager = language_manager
        
        # Configurar la interfaz
        self._setup_ui()
        
        # Conectar señales
        if language_manager:
            from languages import language_signal
            language_signal.language_changed.connect(self._on_language_changed)
    
    def _setup_ui(self):
        """Configura la interfaz del selector"""
        layout = QVBoxLayout(self)
        
        # Etiqueta de descripción
        description = "Seleccione el método de escalado para las imágenes:"
        if self.language_manager:
            description = self.language_manager.get_text(
                "scaling_method_description", 
                "Seleccione el método de escalado para las imágenes:"
            )
        
        self.description_label = QLabel(description)
        self.description_label.setWordWrap(True)
        layout.addWidget(self.description_label)
        
        # Combobox para seleccionar el método
        self.method_combo = QComboBox()
        
        # Añadir los métodos disponibles
        for method, name in self.scaling_manager.get_available_methods():
            # Traducir el nombre si hay un gestor de idiomas
            if self.language_manager:
                key = f"scaling_method_{method.value}"
                translated_name = self.language_manager.get_text(key, name)
                self.method_combo.addItem(translated_name, method.value)
            else:
                self.method_combo.addItem(name, method.value)
        
        # Seleccionar el método actual
        current_method = self.scaling_manager.get_current_method()
        index = self.method_combo.findData(current_method.value)
        if index >= 0:
            self.method_combo.setCurrentIndex(index)
        
        # Conectar señal de cambio
        self.method_combo.currentIndexChanged.connect(self._on_method_changed)
        
        layout.addWidget(self.method_combo)
        
        # Etiqueta de información del método
        self.info_label = QLabel("")
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label)
        
        # Actualizar la información del método seleccionado
        self._update_method_info()
    
    def _on_method_changed(self, index):
        """
        Maneja el cambio de método de escalado
        
        Args:
            index: Índice del método seleccionado en el combobox
        """
        # Obtener el método seleccionado
        method_value = self.method_combo.itemData(index)
        method = ScalingMethod(method_value)
        
        # Establecer el método en el gestor
        self.scaling_manager.set_scaling_method(method)
        
        # Actualizar la información del método
        self._update_method_info()
        
        # Emitir señal de cambio de método
        scaling_signal.method_changed.emit(method)
    
    def _update_method_info(self):
        """Actualiza la información del método seleccionado"""
        # Obtener el método actual
        method = self.scaling_manager.get_current_method()
        
        # Información según el método
        info = {
            ScalingMethod.LANCZOS: "Algoritmo de alta calidad que produce imágenes nítidas. Ideal para portadas y logos.",
            ScalingMethod.BICUBIC: "Buena calidad con suavizado. Adecuado para la mayoría de imágenes.",
            ScalingMethod.BILINEAR: "Calidad media con buen rendimiento. Útil para capturas de pantalla.",
            ScalingMethod.NEAREST: "Rápido pero de menor calidad. Mantiene bordes duros.",
            ScalingMethod.BOX: "Suavizado uniforme. Bueno para reducir imágenes.",
            ScalingMethod.HAMMING: "Preserva detalles finos. Ideal para textos e iconos.",
            ScalingMethod.PS2_OPTIMIZED: "Optimizado específicamente para PS2. Recomendado para todos los tipos de imagen."
        }
        
        # Traducir la información si hay un gestor de idiomas
        if self.language_manager:
            for key in info:
                info_key = f"scaling_method_info_{key.value}"
                info[key] = self.language_manager.get_text(info_key, info[key])
        
        # Establecer el texto de información
        self.info_label.setText(info[method])
    
    def _on_language_changed(self, lang_code):
        """
        Actualiza los textos cuando cambia el idioma
        
        Args:
            lang_code: Código del idioma
        """
        # Actualizar título
        self.setTitle(self.language_manager.get_text("scaling_method", "Método de Escalado"))
        
        # Actualizar descripción
        self.description_label.setText(
            self.language_manager.get_text(
                "scaling_method_description", 
                "Seleccione el método de escalado para las imágenes:"
            )
        )
        
        # Guardar el método actual
        current_data = self.method_combo.currentData()
        
        # Actualizar los elementos del combobox
        self.method_combo.clear()
        for method, name in self.scaling_manager.get_available_methods():
            key = f"scaling_method_{method.value}"
            translated_name = self.language_manager.get_text(key, name)
            self.method_combo.addItem(translated_name, method.value)
        
        # Restaurar el método seleccionado
        index = self.method_combo.findData(current_data)
        if index >= 0:
            self.method_combo.setCurrentIndex(index)
        
        # Actualizar la información del método
        self._update_method_info()

