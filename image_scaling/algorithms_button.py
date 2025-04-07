"""
Botón de selección de algoritmos de escalado para OPL Image Converter
"""
from PyQt5.QtWidgets import (
    QToolButton, QMenu, QAction, QDialog, QVBoxLayout, QLabel, 
    QGroupBox, QRadioButton, QPushButton, QButtonGroup, QScrollArea,
    QWidget, QHBoxLayout, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QSize
from PyQt5.QtGui import QFont

# Señal personalizada para cambio de algoritmo de escalado
class ScalingAlgorithmChangedSignal(QObject):
    algorithm_changed = pyqtSignal(str)

# Variable global para la señal de algoritmo de escalado
scaling_algorithm_signal = ScalingAlgorithmChangedSignal()

class AlgorithmSelectionDialog(QDialog):
    """Diálogo para seleccionar el algoritmo de escalado"""
    
    def __init__(self, parent=None, language_manager=None, current_algorithm="lanczos"):
        super().__init__(parent)
        self.language_manager = language_manager
        self.current_algorithm = current_algorithm
        
        # Configurar diálogo
        self.setWindowTitle(self.get_text("scaling_algorithm_selection", "Selección de Algoritmo de Escalado"))
        self.setMinimumWidth(500)
        self.setMinimumHeight(500)
        self.setup_ui()
        
    def get_text(self, key, default):
        """Obtiene un texto traducido si hay un gestor de idiomas"""
        if self.language_manager:
            return self.language_manager.get_text(key, default)
        return default
        
    def setup_ui(self):
        """Configura la interfaz del diálogo"""
        layout = QVBoxLayout(self)
        
        # Título
        title_label = QLabel(self.get_text("scaling_algorithm_title", "Algoritmos de Escalado"))
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Descripción
        desc_label = QLabel(self.get_text("scaling_algorithm_description", 
            "Seleccione el algoritmo de escalado que desea utilizar para procesar las imágenes. "
            "Cada algoritmo tiene características diferentes y puede ser más adecuado para ciertos tipos de imágenes."))
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc_label)
        
        # Separador
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)
        
        # Área de desplazamiento para los algoritmos
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        # Grupo de botones para los algoritmos
        self.algorithm_group = QButtonGroup(self)
        
        # Definir los algoritmos disponibles
        self.algorithms = [
            {
                "id": "lanczos",
                "name": self.get_text("algorithm_lanczos", "Lanczos (Alta calidad)"),
                "description": self.get_text("algorithm_lanczos_desc", 
                    "Algoritmo de alta calidad que produce imágenes nítidas con menos artefactos. "
                    "Es computacionalmente más intensivo pero produce resultados de alta calidad. "
                    "Ideal para portadas y logos donde la calidad es importante."),
                "icon": "🔍"
            },
            {
                "id": "bicubic",
                "name": self.get_text("algorithm_bicubic", "Bicúbico (Buena calidad)"),
                "description": self.get_text("algorithm_bicubic_desc", 
                    "Utiliza los valores de los 16 píxeles más cercanos para calcular el valor del nuevo píxel. "
                    "Produce resultados más suaves que la interpolación bilineal y es adecuada para imágenes fotográficas. "
                    "Buen equilibrio entre calidad y rendimiento."),
                "icon": "📊"
            },
            {
                "id": "bilinear",
                "name": self.get_text("algorithm_bilinear", "Bilineal (Calidad media)"),
                "description": self.get_text("algorithm_bilinear_desc", 
                    "Utiliza los valores de los 4 píxeles más cercanos para calcular el valor del nuevo píxel. "
                    "Es más rápida que la interpolación bicúbica pero produce resultados menos suaves. "
                    "Adecuada para capturas de pantalla y fondos."),
                "icon": "📈"
            },
            {
                "id": "nearest",
                "name": self.get_text("algorithm_nearest", "Vecino más cercano (Rápido)"),
                "description": self.get_text("algorithm_nearest_desc", 
                    "Selecciona el valor del píxel más cercano en la imagen original para cada píxel en la imagen redimensionada. "
                    "Es el método más rápido pero produce resultados con bordes dentados y pixelados. "
                    "Útil cuando se necesita velocidad sobre calidad."),
                "icon": "⚡"
            },
            {
                "id": "box",
                "name": self.get_text("algorithm_box", "Box (Suavizado)"),
                "description": self.get_text("algorithm_box_desc", 
                    "Utiliza un filtro de caja para redimensionar la imagen. "
                    "Es adecuado para reducir el tamaño de una imagen y produce resultados suavizados. "
                    "Bueno para imágenes que necesitan un aspecto más suave."),
                "icon": "🔲"
            },
            {
                "id": "hamming",
                "name": self.get_text("algorithm_hamming", "Hamming (Detalle)"),
                "description": self.get_text("algorithm_hamming_desc", 
                    "Utiliza un filtro de ventana Hamming para redimensionar la imagen. "
                    "Produce resultados con buen detalle y menos artefactos que otros métodos. "
                    "Adecuado para imágenes con detalles finos como texto o líneas."),
                "icon": "📝"
            },
            {
                "id": "ps2_optimized",
                "name": self.get_text("algorithm_ps2", "Optimizado para PS2 (Recomendado)"),
                "description": self.get_text("algorithm_ps2_desc", 
                    "Algoritmo especialmente diseñado para producir imágenes que se vean bien en la PlayStation 2. "
                    "Tiene en cuenta las limitaciones de hardware y características de visualización de la PS2. "
                    "Recomendado para todos los tipos de imágenes destinadas a OPL Manager."),
                "icon": "🎮"
            }
        ]
        
        # Crear un grupo para cada algoritmo
        for i, algorithm in enumerate(self.algorithms):
            group = QGroupBox()
            group_layout = QVBoxLayout(group)
            
            # Cabecera con radio button y nombre
            header_layout = QHBoxLayout()
            
            # Radio button
            radio_btn = QRadioButton()
            radio_btn.setProperty("algorithm_id", algorithm["id"])
            self.algorithm_group.addButton(radio_btn, i)
            if algorithm["id"] == self.current_algorithm:
                radio_btn.setChecked(True)
            header_layout.addWidget(radio_btn)
            
            # Icono y nombre
            name_label = QLabel(f"{algorithm['icon']} {algorithm['name']}")
            name_font = QFont()
            name_font.setBold(True)
            name_label.setFont(name_font)
            header_layout.addWidget(name_label, 1)
            
            group_layout.addLayout(header_layout)
            
            # Descripción
            desc_label = QLabel(algorithm["description"])
            desc_label.setWordWrap(True)
            desc_label.setContentsMargins(20, 0, 0, 0)
            group_layout.addWidget(desc_label)
            
            scroll_layout.addWidget(group)
        
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)
        
        # Botones de acción
        button_layout = QHBoxLayout()
        
        # Botón de cancelar
        cancel_button = QPushButton(self.get_text("cancel", "Cancelar"))
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        # Botón de aceptar
        accept_button = QPushButton(self.get_text("accept", "Aceptar"))
        accept_button.clicked.connect(self.accept)
        button_layout.addWidget(accept_button)
        
        layout.addLayout(button_layout)
        
    def get_selected_algorithm(self):
        """Obtiene el algoritmo seleccionado"""
        selected_button = self.algorithm_group.checkedButton()
        if selected_button:
            return selected_button.property("algorithm_id")
        return self.current_algorithm

class AlgorithmButton(QToolButton):
    """Botón personalizado para seleccionar el algoritmo de escalado"""
    
    def __init__(self, parent=None, language_manager=None):
        super().__init__(parent)
        self.language_manager = language_manager
        self.setPopupMode(QToolButton.InstantPopup)
        self.setText("🔍")
        self.setToolTip(self.get_text("scaling_algorithm_button", "Algoritmo de Escalado"))
        
        # Algoritmo actual
        self.current_algorithm = "lanczos"
        
        # Crear menú de algoritmos
        self.algorithm_menu = QMenu(self)
        
        # Añadir opciones de algoritmos
        self.add_algorithm_action("lanczos", self.get_text("algorithm_lanczos", "Lanczos (Alta calidad)"), "🔍")
        self.add_algorithm_action("bicubic", self.get_text("algorithm_bicubic", "Bicúbico (Buena calidad)"), "📊")
        self.add_algorithm_action("bilinear", self.get_text("algorithm_bilinear", "Bilineal (Calidad media)"), "📈")
        self.add_algorithm_action("nearest", self.get_text("algorithm_nearest", "Vecino más cercano (Rápido)"), "⚡")
        self.add_algorithm_action("box", self.get_text("algorithm_box", "Box (Suavizado)"), "🔲")
        self.add_algorithm_action("hamming", self.get_text("algorithm_hamming", "Hamming (Detalle)"), "📝")
        self.add_algorithm_action("ps2_optimized", self.get_text("algorithm_ps2", "Optimizado para PS2 (Recomendado)"), "🎮")
        
        # Añadir separador
        self.algorithm_menu.addSeparator()
        
        # Añadir opción para mostrar diálogo detallado
        self.advanced_action = QAction(self.get_text("advanced_selection", "Selección Avanzada..."), self)
        self.advanced_action.triggered.connect(self.show_advanced_dialog)
        self.algorithm_menu.addAction(self.advanced_action)
        
        self.setMenu(self.algorithm_menu)
        self.setStyleSheet("""
            QToolButton {
                font-size: 16px;
                padding: 5px;
                border: none;
            }
        """)
        
        # Conectar señal de cambio de idioma si hay un gestor de idiomas
        if language_manager:
            from languages import language_signal
            language_signal.language_changed.connect(self.on_language_changed)
        
    def get_text(self, key, default):
        """Obtiene un texto traducido si hay un gestor de idiomas"""
        if self.language_manager:
            return self.language_manager.get_text(key, default)
        return default
        
    def add_algorithm_action(self, algorithm_id, algorithm_name, icon=""):
        """Añade una acción al menú de algoritmos"""
        action = QAction(f"{icon} {algorithm_name}", self)
        action.setData(algorithm_id)
        action.setCheckable(True)
        action.setChecked(self.current_algorithm == algorithm_id)
        action.triggered.connect(lambda checked, a=algorithm_id: self.on_algorithm_selected(a))
        self.algorithm_menu.addAction(action)
        
    def on_algorithm_selected(self, algorithm_id):
        """Maneja la selección de un algoritmo"""
        # Actualizar estado de las acciones
        for act in self.algorithm_menu.actions():
            if act.isCheckable():  # Solo las acciones de algoritmos son checkable
                act.setChecked(act.data() == algorithm_id)
        
        # Actualizar algoritmo actual
        self.current_algorithm = algorithm_id
        
        # Actualizar icono del botón según el algoritmo
        icons = {
            "lanczos": "🔍",
            "bicubic": "📊",
            "bilinear": "📈",
            "nearest": "⚡",
            "box": "🔲",
            "hamming": "📝",
            "ps2_optimized": "🎮"
        }
        self.setText(icons.get(algorithm_id, "🔍"))
        
        # Emitir señal global de cambio de algoritmo
        scaling_algorithm_signal.algorithm_changed.emit(algorithm_id)
        
    def show_advanced_dialog(self):
        """Muestra el diálogo avanzado de selección de algoritmo"""
        dialog = AlgorithmSelectionDialog(self.parent(), self.language_manager, self.current_algorithm)
        if dialog.exec_() == QDialog.Accepted:
            selected_algorithm = dialog.get_selected_algorithm()
            self.on_algorithm_selected(selected_algorithm)
            
    def update_checked_algorithm(self, algorithm_id):
        """Actualiza el algoritmo seleccionado en el menú"""
        for action in self.algorithm_menu.actions():
            if action.isCheckable():  # Solo las acciones de algoritmos son checkable
                action.setChecked(action.data() == algorithm_id)
        
        # Actualizar algoritmo actual
        self.current_algorithm = algorithm_id
        
        # Actualizar icono del botón según el algoritmo
        icons = {
            "lanczos": "🔍",
            "bicubic": "📊",
            "bilinear": "📈",
            "nearest": "⚡",
            "box": "🔲",
            "hamming": "📝",
            "ps2_optimized": "🎮"
        }
        self.setText(icons.get(algorithm_id, "🔍"))
            
    def on_language_changed(self, lang_code):
        """Actualiza los textos cuando cambia el idioma"""
        self.setToolTip(self.get_text("scaling_algorithm_button", "Algoritmo de Escalado"))
        
        # Actualizar textos del menú
        algorithm_names = {
            "lanczos": self.get_text("algorithm_lanczos", "Lanczos (Alta calidad)"),
            "bicubic": self.get_text("algorithm_bicubic", "Bicúbico (Buena calidad)"),
            "bilinear": self.get_text("algorithm_bilinear", "Bilineal (Calidad media)"),
            "nearest": self.get_text("algorithm_nearest", "Vecino más cercano (Rápido)"),
            "box": self.get_text("algorithm_box", "Box (Suavizado)"),
            "hamming": self.get_text("algorithm_hamming", "Hamming (Detalle)"),
            "ps2_optimized": self.get_text("algorithm_ps2", "Optimizado para PS2 (Recomendado)")
        }
        
        # Actualizar las acciones del menú
        for action in self.algorithm_menu.actions():
            if action.isCheckable():  # Solo las acciones de algoritmos son checkable
                algorithm_id = action.data()
                if algorithm_id in algorithm_names:
                    icons = {
                        "lanczos": "🔍",
                        "bicubic": "📊",
                        "bilinear": "📈",
                        "nearest": "⚡",
                        "box": "🔲",
                        "hamming": "📝",
                        "ps2_optimized": "🎮"
                    }
                    icon = icons.get(algorithm_id, "")
                    action.setText(f"{icon} {algorithm_names[algorithm_id]}")
        
        # Actualizar la acción avanzada
        self.advanced_action.setText(self.get_text("advanced_selection", "Selección Avanzada..."))

