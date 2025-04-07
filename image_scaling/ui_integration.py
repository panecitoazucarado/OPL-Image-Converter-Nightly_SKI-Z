"""
Integración de los componentes de escalado con la interfaz de usuario
"""
import os
from typing import Optional, Tuple
from PIL import Image
from PyQt5.QtWidgets import (
    QVBoxLayout, QWidget, QComboBox, QLabel, QCheckBox, 
    QHBoxLayout, QToolBar, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal

# Importar componentes de escalado
from image_scaling.algorithms_button import AlgorithmButton, scaling_algorithm_signal
from image_scaling.image_processor_enhanced import ImageProcessorEnhanced

def integrate_scaling_ui(app, toolbar, options_layout):
    """
    Integra los componentes de escalado en la interfaz de usuario
    
    Args:
        app: Instancia de la aplicación principal
        toolbar: Barra de herramientas donde se añadirá el botón
        options_layout: Layout donde se añadirán las opciones adicionales
    """
    # Crear el botón de algoritmo de escalado
    algorithm_button = AlgorithmButton(app, app.language_manager)
    
    # Añadir espacio flexible antes del botón
    spacer = QWidget()
    spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    toolbar.insertWidget(toolbar.actions()[0], spacer)
    
    # Añadir el botón a la barra de herramientas
    toolbar.insertWidget(toolbar.actions()[0], algorithm_button)
    
    # Añadir opciones adicionales al panel de opciones
    options_container = QWidget()
    options_container_layout = QVBoxLayout(options_container)
    options_container_layout.setContentsMargins(0, 10, 0, 0)
    
    # Etiqueta de información del algoritmo
    algorithm_info_label = QLabel(app.language_manager.get_text(
        "algorithm_info", 
        "Algoritmo actual: Lanczos (Alta calidad)"
    ))
    algorithm_info_label.setWordWrap(True)
    options_container_layout.addWidget(algorithm_info_label)
    
    # Opciones de mejora
    enhance_checkbox = QCheckBox(app.language_manager.get_text(
        "enhance_contrast", 
        "Mejorar contraste"
    ))
    enhance_checkbox.setChecked(False)
    options_container_layout.addWidget(enhance_checkbox)
    
    sharpen_checkbox = QCheckBox(app.language_manager.get_text(
        "sharpen_image", 
        "Aplicar nitidez"
    ))
    sharpen_checkbox.setChecked(False)
    options_container_layout.addWidget(sharpen_checkbox)
    
    # Añadir al layout de opciones
    options_layout.addWidget(options_container)
    
    # Crear instancia del procesador de imágenes mejorado
    image_processor = ImageProcessorEnhanced()
    
    # Guardar referencias en la aplicación
    app.algorithm_button = algorithm_button
    app.algorithm_info_label = algorithm_info_label
    app.enhance_checkbox = enhance_checkbox
    app.sharpen_checkbox = sharpen_checkbox
    app.image_processor_enhanced = image_processor
    
    # Conectar señales
    scaling_algorithm_signal.algorithm_changed.connect(
        lambda algorithm: update_algorithm_info(app, algorithm)
    )
    enhance_checkbox.stateChanged.connect(lambda state: app._update_preview())
    sharpen_checkbox.stateChanged.connect(lambda state: app._update_preview())
    
    # Reemplazar métodos de la aplicación
    original_update_preview = app._update_preview
    original_process_images = app._process_images
    
    # Reemplazar el método de actualización de vista previa
    app._update_preview = lambda: enhanced_update_preview(app, original_update_preview)
    
    # Reemplazar el método de procesamiento de imágenes
    app._process_images = lambda: enhanced_process_images(app, original_process_images)
    
    # Actualizar traducciones cuando cambia el idioma
    original_update_ui_texts = app._update_ui_texts
    app._update_ui_texts = lambda: enhanced_update_ui_texts(app, original_update_ui_texts)

def update_algorithm_info(app, algorithm):
    """
    Actualiza la información del algoritmo seleccionado
    
    Args:
        app: Instancia de la aplicación
        algorithm: ID del algoritmo seleccionado
    """
    # Mapeo de algoritmos a nombres descriptivos
    algorithm_names = {
        "lanczos": app.language_manager.get_text("algorithm_lanczos", "Lanczos (Alta calidad)"),
        "bicubic": app.language_manager.get_text("algorithm_bicubic", "Bicúbico (Buena calidad)"),
        "bilinear": app.language_manager.get_text("algorithm_bilinear", "Bilineal (Calidad media)"),
        "nearest": app.language_manager.get_text("algorithm_nearest", "Vecino más cercano (Rápido)"),
        "box": app.language_manager.get_text("algorithm_box", "Box (Suavizado)"),
        "hamming": app.language_manager.get_text("algorithm_hamming", "Hamming (Detalle)"),
        "ps2_optimized": app.language_manager.get_text("algorithm_ps2", "Optimizado para PS2 (Recomendado)")
    }
    
    # Actualizar la etiqueta de información
    app.algorithm_info_label.setText(
        app.language_manager.get_text("algorithm_info", "Algoritmo actual: {}").format(
            algorithm_names.get(algorithm, algorithm_names["lanczos"])
        )
    )
    
    # Actualizar la vista previa
    app._update_preview()

def enhanced_update_preview(app, original_method):
    """
    Versión mejorada del método de actualización de vista previa
    
    Args:
        app: Instancia de la aplicación
        original_method: Método original de actualización de vista previa
    """
    if not app.input_files:
        app.original_label.setText(app.language_manager.get_text("drag_drop_here", "Arrastra y suelta una imagen aquí"))
        app.original_label.setPixmap(None)
        app.processed_label.setText(app.language_manager.get_text("processed_preview", "Vista previa procesada"))
        app.processed_label.setPixmap(None)
        app.preview_index_label.setText("")
        return
    
    app.preview_index_label.setText(
        app.language_manager.get_text("image_count", "Imagen {} de {}").format(
            app.current_preview_index + 1, len(app.input_files)
        )
    )
    
    current_file = app.input_files[app.current_preview_index]
    
    try:
        # Vista previa original
        img = Image.open(current_file)
        img.thumbnail((300, 300))
        
        # Convertir imagen PIL a QPixmap para mostrar
        img_qt = app._pil_to_pixmap(img)
        app.original_label.setText("")
        app.original_label.setPixmap(img_qt)
        
        # Vista previa procesada con el algoritmo seleccionado
        algorithm = app.algorithm_button.current_algorithm
        enhance_contrast = app.enhance_checkbox.isChecked()
        sharpen = app.sharpen_checkbox.isChecked()
        
        # Generar vista previa procesada
        processed_img = app.image_processor_enhanced.get_preview(
            current_file,
            app.image_type,
            app.maintain_aspect,
            algorithm,
            enhance_contrast,
            sharpen
        )
        
        if processed_img:
            # Convertir a QPixmap
            proc_img_qt = app._pil_to_pixmap(processed_img)
            app.processed_label.setText("")
            app.processed_label.setPixmap(proc_img_qt)
        else:
            app.processed_label.setText(app.language_manager.get_text("error_preview", "Error en la vista previa"))
    except Exception as e:
        import logging
        logging.error(f"Error actualizando vista previa: {str(e)}")
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.critical(
            app, 
            app.language_manager.get_text("dialog_error_title", "Error"), 
            app.language_manager.get_text("dialog_error_preview", "No se pudo cargar la vista previa: {}").format(str(e))
        )

def enhanced_process_images(app, original_method):
    """
    Versión mejorada del método de procesamiento de imágenes
    
    Args:
        app: Instancia de la aplicación
        original_method: Método original de procesamiento de imágenes
    """
    if not app.input_files:
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.warning(
            app, 
            app.language_manager.get_text("dialog_warning_title", "Sin archivos"), 
            app.language_manager.get_text("dialog_warning_no_files", "No hay imágenes seleccionadas para procesar")
        )
        return
    
    # Obtener opciones de procesamiento
    algorithm = app.algorithm_button.current_algorithm
    enhance_contrast = app.enhance_checkbox.isChecked()
    sharpen = app.sharpen_checkbox.isChecked()
    
    # Crear una clase personalizada para el hilo de procesamiento
    from PyQt5.QtCore import QThread, pyqtSignal
    from datetime import datetime
    
    class EnhancedProcessingThread(QThread):
        progress_signal = pyqtSignal(int, int)
        finished_signal = pyqtSignal(int, int)
        
        def __init__(self, input_files, output_dir, image_type, maintain_aspect, auto_rename,
                    algorithm, enhance_contrast, sharpen):
            super().__init__()
            self.input_files = input_files
            self.output_dir = output_dir
            self.image_type = image_type
            self.maintain_aspect = maintain_aspect
            self.auto_rename = auto_rename
            self.algorithm = algorithm
            self.enhance_contrast = enhance_contrast
            self.sharpen = sharpen
            self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.processor = ImageProcessorEnhanced()
        
        def run(self):
            batch_dir = os.path.join(self.output_dir, f"{self.image_type}_{self.timestamp}")
            os.makedirs(batch_dir, exist_ok=True)
            
            success_count = 0
            for i, input_file in enumerate(self.input_files):
                try:
                    base_name = os.path.splitext(os.path.basename(input_file))[0]
                    
                    # Aplicar renombrado automático si está activado
                    if self.auto_rename:
                        output_filename = f"{base_name}_{self.image_type}.png"
                    else:
                        output_filename = f"{base_name}.png"
                        
                    output_file = os.path.join(batch_dir, output_filename)
                    success, _ = self.processor.convert_resize_image(
                        input_file, 
                        output_file,
                        self.image_type,
                        self.maintain_aspect,
                        self.algorithm,
                        self.enhance_contrast,
                        self.sharpen
                    )
                    if success:
                        success_count += 1
                    self.progress_signal.emit(i + 1, len(self.input_files))
                except Exception as e:
                    import logging
                    logging.error(f"Error procesando {input_file}: {str(e)}")
            
            self.finished_signal.emit(success_count, len(self.input_files))
    
    # Configurar y ejecutar el hilo de procesamiento mejorado
    app.processing_thread = EnhancedProcessingThread(
        app.input_files, 
        app.output_dir, 
        app.image_type, 
        app.maintain_aspect,
        app.auto_rename,
        algorithm,
        enhance_contrast,
        sharpen
    )
    
    # Conectar señales
    app.processing_thread.progress_signal.connect(app._update_progress)
    app.processing_thread.finished_signal.connect(app._processing_finished)
    
    # Iniciar procesamiento
    app.progress_bar.setVisible(True)
    app.progress_bar.setValue(0)
    app.progress_bar.setMaximum(len(app.input_files))
    app.status_bar.showMessage(app.language_manager.get_text("status_processing", "Procesando imágenes..."))
    app.processing_thread.start()

def enhanced_update_ui_texts(app, original_method):
    """
    Versión mejorada del método de actualización de textos de la interfaz
    
    Args:
        app: Instancia de la aplicación
        original_method: Método original de actualización de textos
    """
    # Llamar al método original
    original_method()
    
    # Actualizar textos de los componentes de escalado
    app.enhance_checkbox.setText(app.language_manager.get_text("enhance_contrast", "Mejorar contraste"))
    app.sharpen_checkbox.setText(app.language_manager.get_text("sharpen_image", "Aplicar nitidez"))
    
    # Actualizar información del algoritmo
    update_algorithm_info(app, app.algorithm_button.current_algorithm)

