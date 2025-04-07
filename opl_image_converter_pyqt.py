import os
import sys
import platform
import json
import logging
import subprocess
import threading
import tempfile
import shutil
from datetime import datetime
from typing import List, Dict, Tuple, Optional

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QRadioButton, QCheckBox, QFileDialog, 
    QTreeWidget, QTreeWidgetItem, QScrollArea, QFrame, QSplitter,
    QGroupBox, QMessageBox, QButtonGroup, QStatusBar, QProgressBar,
    QComboBox, QAction, QMenu, QToolBar, QGridLayout, QSizePolicy,
    QToolButton, QDialog, QDesktopWidget
)
from PyQt5.QtCore import Qt, QSize, QThread, pyqtSignal, QMimeData, QUrl, QSettings, QRect, QPoint, QVersionNumber, QObject
from PyQt5.QtGui import QPixmap, QImage, QDragEnterEvent, QDropEvent, QPalette, QColor, QIcon, QPainter, QPen, QBrush, QFont, QFontMetrics
from PIL import Image, __version__ as PIL_VERSION

# Importar el gestor de idiomas
from languages import LanguageManager, LanguageButton, language_signal

# Información de la aplicación
APP_NAME = "OPL Image Converter"
APP_VERSION = "2.1.0"
APP_AUTHOR = "Josema (panecitoazucarado)"
APP_GITHUB = "https://github.com/panecitoazucarado"
APP_DESCRIPTION = "Aplicación para convertir y redimensionar imágenes para OPL Manager"

# Configuración inicial de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='opl_converter.log',
    filemode='a'
)
logger = logging.getLogger(__name__)

# Constantes
SUPPORTED_FORMATS = ('.jpg', '.jpeg', '.png', '.bmp', '.webp', '.tiff', '.gif')
DEFAULT_OUTPUT_DIR = os.path.join(os.path.expanduser("~"), "OPL_Images")
HISTORY_FILE = os.path.join(os.path.expanduser("~"), ".opl_converter_history.json")
TEMP_DIR = os.path.join(os.path.expanduser("~"), ".opl_converter_temp")
SETTINGS_FILE = os.path.join(os.path.expanduser("~"), ".opl_converter_settings.json")

# Temas de color
THEMES = {
    "light": {
        "name": "Modo Claro",
        "primary": "#6366f1",  # Indigo-500
        "primary_hover": "#4f46e5",  # Indigo-600
        "secondary": "#f97316",  # Orange-500
        "secondary_hover": "#ea580c",  # Orange-600
        "background": "#f8fafc",  # Slate-50
        "card": "#ffffff",  # White
        "text": "#1e293b",  # Slate-800
        "text_secondary": "#64748b",  # Slate-500
        "border": "#e2e8f0",  # Slate-200
        "success": "#10b981",  # Emerald-500
        "warning": "#f59e0b",  # Amber-500
        "error": "#ef4444",  # Red-500
        "info": "#3b82f6",  # Blue-500
        "disabled": "#cbd5e1",  # Slate-300
        "hover": "#f1f5f9",  # Slate-100
        "active": "#e2e8f0",  # Slate-200
        "drop_target": "#dbeafe",  # Blue-100
        "drop_border": "#3b82f6",  # Blue-500
    },
    "dark": {
        "name": "Modo Oscuro",
        "primary": "#818cf8",  # Indigo-400
        "primary_hover": "#6366f1",  # Indigo-500
        "secondary": "#fb923c",  # Orange-400
        "secondary_hover": "#f97316",  # Orange-500
        "background": "#0f172a",  # Slate-900
        "card": "#1e293b",  # Slate-800
        "text": "#f8fafc",  # Slate-50
        "text_secondary": "#94a3b8",  # Slate-400
        "border": "#334155",  # Slate-700
        "success": "#34d399",  # Emerald-400
        "warning": "#fbbf24",  # Amber-400
        "error": "#f87171",  # Red-400
        "info": "#60a5fa",  # Blue-400
        "disabled": "#475569",  # Slate-600
        "hover": "#1e293b",  # Slate-800
        "active": "#334155",  # Slate-700
        "drop_target": "#1e3a8a",  # Blue-900
        "drop_border": "#60a5fa",  # Blue-400
    },
    "purple": {
        "name": "Púrpura",
        "primary": "#a855f7",  # Purple-500
        "primary_hover": "#9333ea",  # Purple-600
        "secondary": "#ec4899",  # Pink-500
        "secondary_hover": "#db2777",  # Pink-600
        "background": "#faf5ff",  # Purple-50
        "card": "#ffffff",  # White
        "text": "#581c87",  # Purple-900
        "text_secondary": "#a855f7",  # Purple-500
        "border": "#e9d5ff",  # Purple-200
        "success": "#10b981",  # Emerald-500
        "warning": "#f59e0b",  # Amber-500
        "error": "#ef4444",  # Red-500
        "info": "#3b82f6",  # Blue-500
        "disabled": "#d8b4fe",  # Purple-300
        "hover": "#f3e8ff",  # Purple-100
        "active": "#e9d5ff",  # Purple-200
        "drop_target": "#f3e8ff",  # Purple-100
        "drop_border": "#a855f7",  # Purple-500
    },
    "dark_purple": {
        "name": "Púrpura Oscuro",
        "primary": "#c084fc",  # Purple-400
        "primary_hover": "#a855f7",  # Purple-500
        "secondary": "#f472b6",  # Pink-400
        "secondary_hover": "#ec4899",  # Pink-500
        "background": "#2e1065",  # Purple-950
        "card": "#4c1d95",  # Purple-900
        "text": "#faf5ff",  # Purple-50
        "text_secondary": "#d8b4fe",  # Purple-300
        "border": "#7e22ce",  # Purple-700
        "success": "#34d399",  # Emerald-400
        "warning": "#fbbf24",  # Amber-400
        "error": "#f87171",  # Red-400
        "info": "#60a5fa",  # Blue-400
        "disabled": "#7e22ce",  # Purple-700
        "hover": "#6b21a8",  # Purple-800
        "active": "#7e22ce",  # Purple-700
        "drop_target": "#6b21a8",  # Purple-800
        "drop_border": "#c084fc",  # Purple-400
    }
}

# Iconos para los tipos de imagen
IMAGE_TYPE_ICONS = {
    "caratula": "🖼️",
    "borde": "↕️",
    "contracaratula": "📄",
    "captura": "📸",
    "fondo": "🌄",
    "disco": "💿",
    "logo": "🏷️"
}

# Descripciones para los tipos de imagen
IMAGE_TYPE_DESCRIPTIONS = {
    "caratula": "Portada frontal del juego",
    "borde": "Borde lateral de la caja",
    "contracaratula": "Portada trasera del juego",
    "captura": "Captura de pantalla del juego",
    "fondo": "Imagen de fondo para el menú",
    "disco": "Imagen del disco o etiqueta",
    "logo": "Logo del juego o título"
}

# Señal personalizada para cambio de tema
class ThemeChangedSignal(QObject):
    theme_changed = pyqtSignal(str)

# Variable global para la señal de tema
theme_signal = ThemeChangedSignal()

class ThemeManager:
    """Gestor de temas para la aplicación"""
    
    _instance = None
    
    def __new__(cls):
        """Implementación del patrón Singleton para asegurar una única instancia"""
        if cls._instance is None:
            cls._instance = super(ThemeManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        # Evitar reinicialización si ya está inicializado (Singleton)
        if getattr(self, '_initialized', False):
            return
            
        self._initialized = True
        self.settings = QSettings("OPLManager", "ImageConverter")
        self.current_theme = self.settings.value("theme", "system")
        self.system_is_dark = self._detect_system_theme()
        
    def _detect_system_theme(self):
        """Detecta si el sistema está usando tema oscuro"""
        if platform.system() == "Windows":
            try:
                import winreg
                registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
                key = winreg.OpenKey(registry, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
                value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                return value == 0
            except:
                return False
        elif platform.system() == "Darwin":  # macOS
            try:
                result = subprocess.run(
                    ["defaults", "read", "-g", "AppleInterfaceStyle"],
                    capture_output=True, text=True
                )
                return result.stdout.strip() == "Dark"
            except:
                return False
        else:  # Linux y otros
            try:
                # Intenta detectar en entornos GNOME
                result = subprocess.run(
                    ["gsettings", "get", "org.gnome.desktop.interface", "gtk-theme"],
                    capture_output=True, text=True
                )
                return "dark" in result.stdout.lower()
            except:
                return False
    
    def get_theme_name(self):
        """Obtiene el nombre del tema actual"""
        if self.current_theme == "system":
            return "dark" if self.system_is_dark else "light"
        return self.current_theme
    
    def get_theme(self):
        """Obtiene el diccionario de colores del tema actual"""
        theme_name = self.get_theme_name()
        return THEMES[theme_name]
    
    def set_theme(self, theme_name):
        """Establece el tema actual"""
        if theme_name in THEMES or theme_name == "system":
            self.current_theme = theme_name
            self.settings.setValue("theme", theme_name)
            return True
        return False
    
    def get_stylesheet(self):
        """Genera la hoja de estilos CSS para el tema actual"""
        theme = self.get_theme()
        
        return f"""
            QMainWindow, QDialog {{
                background-color: {theme["background"]};
                color: {theme["text"]};
            }}
            
            QWidget {{
                color: {theme["text"]};
            }}
            
            QGroupBox {{
                font-weight: bold;
                border: 1px solid {theme["border"]};
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: {theme["card"]};
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: {theme["text"]};
            }}
            
            QPushButton {{
                background-color: {theme["primary"]};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                min-height: 30px;
                font-weight: bold;
            }}
            
            QPushButton:hover {{
                background-color: {theme["primary_hover"]};
            }}
            
            QPushButton:pressed {{
                background-color: {theme["primary_hover"]};
            }}
            
            QPushButton:disabled {{
                background-color: {theme["disabled"]};
                color: {theme["text_secondary"]};
            }}
            
            QPushButton#secondary_button {{
                background-color: transparent;
                color: {theme["primary"]};
                border: 1px solid {theme["primary"]};
            }}
            
            QPushButton#secondary_button:hover {{
                background-color: {theme["hover"]};
                border-color: {theme["primary_hover"]};
                color: {theme["primary_hover"]};
            }}
            
            QPushButton#convert_button {{
                background-color: {theme["secondary"]};
                color: white;
                font-weight: bold;
                font-size: 14px;
                padding: 10px 20px;
            }}
            
            QPushButton#convert_button:hover {{
                background-color: {theme["secondary_hover"]};
            }}
            
            QRadioButton, QCheckBox {{
                spacing: 8px;
                color: {theme["text"]};
            }}
            
            QRadioButton::indicator {{
                width: 18px;
                height: 18px;
                border: 2px solid {theme["border"]};
                border-radius: 9px;
                background-color: {theme["card"]};
            }}
            
            QRadioButton::indicator:checked {{
                border: 2px solid {theme["primary"]};
                background-color: {theme["card"]};
                image: url("data:image/svg+xml,<svg width='10' height='10'><circle cx='5' cy='5' r='5' fill='{theme["primary"].replace('#', '%23')}'/></svg>");
            }}
            
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 2px solid {theme["border"]};
                border-radius: 3px;
                background-color: {theme["card"]};
            }}
            
            QCheckBox::indicator:checked {{
                border: 2px solid {theme["primary"]};
                background-color: {theme["primary"]};
            }}
            
            QLabel {{
                color: {theme["text"]};
            }}
            
            QStatusBar {{
                background-color: {theme["card"]};
                color: {theme["text"]};
                border-top: 1px solid {theme["border"]};
            }}
            
            QProgressBar {{
                border: 1px solid {theme["border"]};
                border-radius: 4px;
                text-align: center;
                background-color: {theme["background"]};
            }}
            
            QProgressBar::chunk {{
                background-color: {theme["primary"]};
                width: 10px;
                margin: 0.5px;
            }}
            
            QTreeWidget {{
                background-color: {theme["card"]};
                alternate-background-color: {theme["hover"]};
                color: {theme["text"]};
                border: 1px solid {theme["border"]};
                border-radius: 4px;
            }}
            
            QTreeWidget::item:selected {{
                background-color: {theme["primary"]};
                color: white;
            }}
            
            QTreeWidget::item:hover {{
                background-color: {theme["hover"]};
            }}
            
            QHeaderView::section {{
                background-color: {theme["card"]};
                color: {theme["text"]};
                padding: 5px;
                border: 1px solid {theme["border"]};
            }}
            
            QComboBox {{
                border: 1px solid {theme["border"]};
                border-radius: 4px;
                padding: 5px;
                background-color: {theme["card"]};
                color: {theme["text"]};
                min-height: 25px;
            }}
            
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 15px;
                border-left-width: 1px;
                border-left-color: {theme["border"]};
                border-left-style: solid;
            }}
            
            QComboBox QAbstractItemView {{
                background-color: {theme["card"]};
                color: {theme["text"]};
                selection-background-color: {theme["primary"]};
                selection-color: white;
            }}
            
            QToolBar {{
                background-color: {theme["card"]};
                border-bottom: 1px solid {theme["border"]};
                spacing: 5px;
            }}
            
            QToolButton {{
                background-color: transparent;
                border-radius: 4px;
                padding: 5px;
            }}
            
            QToolButton:hover {{
                background-color: {theme["hover"]};
            }}
            
            QToolButton::menu-indicator {{
                image: none;
            }}
            
            QMenu {{
                background-color: {theme["card"]};
                color: {theme["text"]};
                border: 1px solid {theme["border"]};
                border-radius: 4px;
            }}
            
            QMenu::item {{
                padding: 8px 30px 8px 20px;
            }}
            
            QMenu::item:selected {{
                background-color: {theme["primary"]};
                color: white;
            }}
            
            QScrollArea {{
                border: none;
            }}
            
            QScrollBar:vertical {{
                background: {theme["background"]};
                width: 10px;
                margin: 0px;
            }}
            
            QScrollBar::handle:vertical {{
                background: {theme["border"]};
                min-height: 20px;
                border-radius: 5px;
            }}
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            
            QDialog {{
                min-width: 400px;
                min-height: 300px;
            }}
        """

class AboutDialog(QDialog):
    """Diálogo de información 'Acerca de'"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.language_manager = LanguageManager()
        self.setWindowTitle(self.language_manager.get_text("dialog_about_title", "Acerca de") + " " + APP_NAME)
        self.setMinimumWidth(500)
        self.setup_ui()
        
        # Conectar señal de cambio de idioma
        language_signal.language_changed.connect(self.on_language_changed)
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Título
        title_label = QLabel(APP_NAME)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Versión
        self.version_label = QLabel(self.language_manager.get_text("dialog_about_version", "Versión {}").format(APP_VERSION))
        self.version_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.version_label)
        
        # Separador
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)
        
        # Descripción
        self.desc_label = QLabel(self.language_manager.get_text("app_description", APP_DESCRIPTION))
        self.desc_label.setWordWrap(True)
        self.desc_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.desc_label)
        
        # Desarrollador
        self.dev_label = QLabel(self.language_manager.get_text("dialog_about_developer", "Desarrollado por: {}").format(APP_AUTHOR))
        self.dev_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.dev_label)
        
        # GitHub
        self.github_label = QLabel(f"{self.language_manager.get_text('dialog_about_github', 'GitHub:')} <a href='{APP_GITHUB}'>{APP_GITHUB}</a>")
        self.github_label.setOpenExternalLinks(True)
        self.github_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.github_label)
        
        # Tecnologías
        self.tech_group = QGroupBox(self.language_manager.get_text("dialog_about_technologies", "Tecnologías utilizadas"))
        tech_layout = QVBoxLayout(self.tech_group)
        
        # PyQt
        try:
            from PyQt5.QtCore import QT_VERSION_STR
            pyqt_version = f"{QVersionNumber.fromString(QT_VERSION_STR).majorVersion()}.{QVersionNumber.fromString(QT_VERSION_STR).minorVersion()}"
        except:
            pyqt_version = "5.x"  # Versión genérica si no se puede determinar
        pyqt_label = QLabel(f"• PyQt {pyqt_version}")
        tech_layout.addWidget(pyqt_label)
        
        # Pillow
        pillow_label = QLabel(f"• Pillow {PIL_VERSION}")
        tech_layout.addWidget(pillow_label)
        
        # Python
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        python_label = QLabel(f"• Python {python_version}")
        tech_layout.addWidget(python_label)
        
        layout.addWidget(self.tech_group)
        
        # Sistema
        self.system_label = QLabel(self.language_manager.get_text("dialog_about_system", "Sistema: {} {}").format(platform.system(), platform.version()))
        self.system_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.system_label)
        
        # Botón de cerrar
        self.close_button = QPushButton(self.language_manager.get_text("dialog_about_close", "Cerrar"))
        self.close_button.clicked.connect(self.accept)
        layout.addWidget(self.close_button)
        
    def on_language_changed(self, lang_code):
        """Actualiza los textos cuando cambia el idioma"""
        self.setWindowTitle(self.language_manager.get_text("dialog_about_title", "Acerca de") + " " + APP_NAME)
        
        # Actualizar todos los textos
        self.version_label.setText(self.language_manager.get_text("dialog_about_version", "Versión {}").format(APP_VERSION))
        self.desc_label.setText(self.language_manager.get_text("app_description", APP_DESCRIPTION))
        self.dev_label.setText(self.language_manager.get_text("dialog_about_developer", "Desarrollado por: {}").format(APP_AUTHOR))
        self.github_label.setText(f"{self.language_manager.get_text('dialog_about_github', 'GitHub:')} <a href='{APP_GITHUB}'>{APP_GITHUB}</a>")
        self.system_label.setText(self.language_manager.get_text("dialog_about_system", "Sistema: {} {}").format(platform.system(), platform.version()))
        
        # Actualizar grupos
        self.tech_group.setTitle(self.language_manager.get_text("dialog_about_technologies", "Tecnologías utilizadas"))
        
        # Actualizar botones
        self.close_button.setText(self.language_manager.get_text("dialog_about_close", "Cerrar"))

class ThemeButton(QToolButton):
    """Botón personalizado para seleccionar el tema"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme_manager = ThemeManager()
        self.language_manager = LanguageManager()
        self.setPopupMode(QToolButton.InstantPopup)
        self.setText("⚙️")
        self.setToolTip(self.language_manager.get_text("menu_theme", "Cambiar tema"))
        
        # Crear menú de temas
        self.theme_menu = QMenu(self)
        
        # Añadir opciones de tema
        self.add_theme_action("system", self.language_manager.get_text("theme_system", "Sistema (Auto)"))
        self.add_theme_action("light", self.language_manager.get_text("theme_light", "Modo Claro"))
        self.add_theme_action("dark", self.language_manager.get_text("theme_dark", "Modo Oscuro"))
        self.add_theme_action("purple", self.language_manager.get_text("theme_purple", "Púrpura"))
        self.add_theme_action("dark_purple", self.language_manager.get_text("theme_dark_purple", "Púrpura Oscuro"))
        
        self.setMenu(self.theme_menu)
        self.setStyleSheet("""
            QToolButton {
                font-size: 16px;
                padding: 5px;
                border: none;
            }
        """)
        
        # Conectar señal de cambio de idioma
        language_signal.language_changed.connect(self.on_language_changed)
        
    def add_theme_action(self, theme_key, theme_name):
        """Añade una acción al menú de temas"""
        action = QAction(theme_name, self)
        action.setData(theme_key)
        action.setCheckable(True)
        action.setChecked(self.theme_manager.current_theme == theme_key)
        action.triggered.connect(lambda checked, k=theme_key: self.on_theme_selected(k))
        self.theme_menu.addAction(action)
        
    def on_theme_selected(self, theme_key):
        """Maneja la selección de un tema"""
        # Actualizar estado de las acciones
        for act in self.theme_menu.actions():
            act.setChecked(act.data() == theme_key)
        
        # Emitir señal global de cambio de tema
        theme_signal.theme_changed.emit(theme_key)
        print(f"Tema seleccionado: {theme_key}")  # Depuración
        
    def update_checked_theme(self, theme_key):
        """Actualiza el tema seleccionado en el menú"""
        for action in self.theme_menu.actions():
            action.setChecked(action.data() == theme_key)
            
    def on_language_changed(self, lang_code):
        """Actualiza los textos cuando cambia el idioma"""
        self.setToolTip(self.language_manager.get_text("menu_theme", "Cambiar tema"))
        
        # Actualizar textos del menú
        theme_names = {
            "system": self.language_manager.get_text("theme_system", "Sistema (Auto)"),
            "light": self.language_manager.get_text("theme_light", "Modo Claro"),
            "dark": self.language_manager.get_text("theme_dark", "Modo Oscuro"),
            "purple": self.language_manager.get_text("theme_purple", "Púrpura"),
            "dark_purple": self.language_manager.get_text("theme_dark_purple", "Púrpura Oscuro")
        }
        
        for action in self.theme_menu.actions():
            theme_key = action.data()
            if theme_key in theme_names:
                action.setText(theme_names[theme_key])

class ImageProcessor:
    """Clase para procesamiento de imágenes con soporte para conversión y redimensionamiento"""
    
    DIMENSIONS = {
        "caratula": (140, 200),
        "borde": (18, 240),
        "contracaratula": (242, 344),
        "captura": (250, 168),
        "fondo": (640, 480),
        "disco": (128, 128),
        "logo": (300, 125)
    }

    @staticmethod
    def is_supported_format(file_path: str) -> bool:
        """Verifica si un archivo tiene un formato de imagen soportado"""
        return os.path.splitext(file_path)[1].lower() in SUPPORTED_FORMATS

    @staticmethod
    def convert_resize_image(input_path: str, output_path: str, image_type: str, 
                            maintain_aspect: bool = True) -> Tuple[bool, str]:
        """Convierte y redimensiona una imagen según las especificaciones"""
        try:
            with Image.open(input_path) as img:
                if img.mode != 'RGB':
                    img = img.convert('RGB')

                target_width, target_height = ImageProcessor.DIMENSIONS.get(image_type, (0, 0))
                if not target_width or not target_height:
                    raise ValueError(f"Tipo de imagen inválido: {image_type}")

                if maintain_aspect:
                    img = ImageProcessor._resize_with_aspect(img, target_width, target_height)
                else:
                    img = img.resize((target_width, target_height), Image.LANCZOS)

                img.save(output_path, 'PNG', optimize=True)
                return True, output_path
        except Exception as e:
            logger.error(f"Error procesando {input_path}: {str(e)}")
            return False, str(e)

    @staticmethod
    def _resize_with_aspect(img: Image.Image, target_width: int, 
                           target_height: int) -> Image.Image:
        """Redimensiona manteniendo la relación de aspecto con bordes negros"""
        img_width, img_height = img.size
        aspect_ratio = img_width / img_height
        target_ratio = target_width / target_height

        if aspect_ratio > target_ratio:
            new_width = target_width
            new_height = int(new_width / aspect_ratio)
        else:
            new_height = target_height
            new_width = int(new_height * aspect_ratio)

        resized_img = img.resize((new_width, new_height), Image.LANCZOS)
        new_img = Image.new('RGB', (target_width, target_height), (0, 0, 0))
        new_img.paste(resized_img, (
            (target_width - new_width) // 2,
            (target_height - new_height) // 2
        ))
        return new_img

class HistoryManager:
    """Manejador del historial de conversiones"""
    
    def __init__(self):
        self.history: List[Dict] = []
        self.load_history()

    def add_entry(self, entry: Dict) -> None:
        """Añade una nueva entrada al historial"""
        self.history.append(entry)
        self.save_history()

    def load_history(self) -> None:
        """Carga el historial desde el archivo"""
        try:
            if os.path.exists(HISTORY_FILE):
                with open(HISTORY_FILE, 'r') as f:
                    self.history = json.load(f)
        except Exception as e:
            logger.error(f"Error cargando historial: {str(e)}")

    def save_history(self) -> None:
        """Guarda el historial en el archivo"""
        try:
            with open(HISTORY_FILE, 'w') as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            logger.error(f"Error guardando historial: {str(e)}")

class ProcessingThread(QThread):
    """Hilo para procesamiento de imágenes en segundo plano"""
    progress_signal = pyqtSignal(int, int)
    finished_signal = pyqtSignal(int, int)
    
    def __init__(self, input_files, output_dir, image_type, maintain_aspect, auto_rename=False):
        super().__init__()
        self.input_files = input_files
        self.output_dir = output_dir
        self.image_type = image_type
        self.maintain_aspect = maintain_aspect
        self.auto_rename = auto_rename
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
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
                success, _ = ImageProcessor.convert_resize_image(
                    input_file, output_file,
                    self.image_type,
                    self.maintain_aspect
                )
                if success:
                    success_count += 1
                self.progress_signal.emit(i + 1, len(self.input_files))
            except Exception as e:
                logger.error(f"Error procesando {input_file}: {str(e)}")
        
        self.finished_signal.emit(success_count, len(self.input_files))

def get_drop_label_style(theme, is_drag_over):
    """Genera el estilo CSS para el DropLabel"""
    if is_drag_over:
        border_color = theme["drop_border"]
        background_color = theme["drop_target"]
        text_color = theme["text"]
    else:
        border_color = theme["border"]
        background_color = theme["card"]
        text_color = theme["text_secondary"]

    return f"""
        QLabel {{
            border: 2px dashed {border_color};
            border-radius: 8px;
            background-color: {background_color};
            color: {text_color};
            padding: 10px;
        }}
        QLabel:hover {{
            border-color: {theme["primary"]};
        }}
    """

class DropLabel(QLabel):
    """Label personalizado que acepta arrastrar y soltar archivos"""
    
    dropped_signal = pyqtSignal(list)
    
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignCenter)
        self.setAcceptDrops(True)
        self.setMinimumSize(300, 300)
        self.theme_manager = ThemeManager()
        self._update_style()
        
    def _update_style(self):
        """Actualiza el estilo según el tema actual"""
        theme = self.theme_manager.get_theme()
        self.setStyleSheet(get_drop_label_style(theme, False))
        
    def update_theme(self):
        """Actualiza el tema del componente"""
        self._update_style()
        
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            theme = self.theme_manager.get_theme()
            self.setStyleSheet(get_drop_label_style(theme, True))
    
    def dragLeaveEvent(self, event):
        self._update_style()
    
    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self._update_style()
            
            file_paths = []
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if os.path.isfile(file_path) and ImageProcessor.is_supported_format(file_path):
                    file_paths.append(file_path)
                elif os.path.isdir(file_path):
                    # Si es un directorio, buscar imágenes dentro
                    for root, _, filenames in os.walk(file_path):
                        for filename in filenames:
                            if ImageProcessor.is_supported_format(filename):
                                file_paths.append(os.path.join(root, filename))
            
            if file_paths:
                self.dropped_signal.emit(file_paths)

# Modificar la clase OPLImageConverterApp para usar el gestor de idiomas
class OPLImageConverterApp(QMainWindow):
    """Aplicación principal con interfaz gráfica PyQt5"""
    
    def __init__(self):
        super().__init__()
        self.theme_manager = ThemeManager()
        self.language_manager = LanguageManager()  # Inicializar el gestor de idiomas
        self._setup_window()
        self._initialize_variables()
        self._setup_ui()
        self.history_manager = HistoryManager()
        self._create_temp_dir()
        self._update_history_tree()
        self._apply_theme()
        self._center_window()
        
        # Conectar señal global de cambio de tema
        theme_signal.theme_changed.connect(self.on_theme_changed)
        
        # Conectar señal global de cambio de idioma
        language_signal.language_changed.connect(self.on_language_changed)
        
        self.showMaximized()  # Iniciar a pantalla completa
        
    def _create_temp_dir(self):
        """Crea el directorio temporal para vistas previas"""
        if not os.path.exists(TEMP_DIR):
            os.makedirs(TEMP_DIR)
            
    def _setup_window(self):
        """Configura la ventana principal"""
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setGeometry(100, 100, 1024, 768)
        self.setMinimumSize(800, 600)
        self.setMaximumSize(1600, 1200)  # Limitar tamaño máximo para evitar deformaciones
        
    def _center_window(self):
        """Centra la ventana en la pantalla"""
        frame_geometry = self.frameGeometry()
        screen_center = QDesktopWidget().availableGeometry().center()
        frame_geometry.moveCenter(screen_center)
        self.move(frame_geometry.topLeft())
        
    def _initialize_variables(self):
        """Inicializa las variables de estado"""
        self.input_files = []
        self.output_dir = DEFAULT_OUTPUT_DIR
        self.image_type = "caratula"
        self.maintain_aspect = True
        self.auto_rename = False
        self.current_preview_index = 0
        
    def _setup_ui(self):
        """Configura la interfaz de usuario"""
        # Barra de herramientas
        self._create_toolbar()
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QHBoxLayout(central_widget)
        
        # Panel izquierdo (controles)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_panel.setMaximumWidth(350)  # Aumentado para acomodar las tarjetas
        
        # Panel derecho (vista previa e historial)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Crear los componentes de la interfaz
        self._create_controls(left_layout)
        self._create_preview(right_layout)
        self._create_history(right_layout)
        
        # Añadir paneles al layout principal
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel, 1)  # El panel derecho se expande
        
        # Barra de estado
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(self.language_manager.get_text("status_ready", "Listo"))
        
        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumWidth(200)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
    def _create_toolbar(self):
        """Crea la barra de herramientas"""
        toolbar = QToolBar("Barra de herramientas principal")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        # Botón de ayuda
        help_action = QAction(self.language_manager.get_text("menu_help", "Ayuda"), self)
        help_action.triggered.connect(self._show_help)
        toolbar.addAction(help_action)
        
        # Botón de acerca de
        about_action = QAction(self.language_manager.get_text("menu_about", "Acerca de"), self)
        about_action.triggered.connect(self._show_about)
        toolbar.addAction(about_action)
        
        # Añadir espacio flexible
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        toolbar.addWidget(spacer)
        
        # Botón de idioma en la esquina superior derecha
        self.language_button = LanguageButton(self)
        toolbar.addWidget(self.language_button)
        
        # Botón de tema en la esquina superior derecha
        self.theme_button = ThemeButton(self)
        toolbar.addWidget(self.theme_button)
        
    def _create_controls(self, layout):
        """Crea el panel de controles"""
        # Grupo de selección de archivos
        self.file_group = QGroupBox(self.language_manager.get_text("file_selection", "Selección de Archivos"))
        file_layout = QVBoxLayout(self.file_group)
        
        # Botones de selección
        self.select_files_btn = QPushButton(self.language_manager.get_text("select_files", "Seleccionar Archivos"))
        self.select_files_btn.clicked.connect(self._select_files)
        file_layout.addWidget(self.select_files_btn)
        
        self.select_folder_btn = QPushButton(self.language_manager.get_text("select_folder", "Seleccionar Carpeta"))
        self.select_folder_btn.setObjectName("secondary_button")
        self.select_folder_btn.clicked.connect(self._select_folder)
        file_layout.addWidget(self.select_folder_btn)
        
        # Etiqueta de archivos seleccionados
        self.files_label = QLabel(self.language_manager.get_text("no_files_selected", "0 archivos seleccionados"))
        file_layout.addWidget(self.files_label)
        
        # Grupo de tipo de imagen
        self.type_group = QGroupBox(self.language_manager.get_text("image_type", "Tipo de Imagen"))
        type_layout = QVBoxLayout(self.type_group)
        
        # Botones de radio para tipos de imagen
        self.type_button_group = QButtonGroup(self)
        
        # Mapeo de tipos de imagen a claves de idioma
        self.type_to_key = {
            "caratula": "image_type_cover",
            "borde": "image_type_spine",
            "contracaratula": "image_type_back",
            "captura": "image_type_screenshot",
            "fondo": "image_type_background",
            "disco": "image_type_disc",
            "logo": "image_type_logo"
        }
        
        for i, (type_key, dimensions) in enumerate(ImageProcessor.DIMENSIONS.items()):
            lang_key = self.type_to_key.get(type_key, type_key)
            type_name = self.language_manager.get_text(lang_key, type_key.capitalize())
            radio_btn = QRadioButton(f"{type_name} ({dimensions[0]}x{dimensions[1]} px)")
            radio_btn.setProperty("type_key", type_key)
            self.type_button_group.addButton(radio_btn, i)
            type_layout.addWidget(radio_btn)
            
            # Seleccionar el primer tipo por defecto
            if i == 0:
                radio_btn.setChecked(True)
        
        self.type_button_group.buttonClicked.connect(self._on_type_changed)
        
        # Grupo de opciones
        self.options_group = QGroupBox(self.language_manager.get_text("options", "Opciones"))
        options_layout = QVBoxLayout(self.options_group)
        
        # Checkbox para mantener relación de aspecto
        self.aspect_checkbox = QCheckBox(self.language_manager.get_text("maintain_aspect_ratio", "Mantener relación de aspecto"))
        self.aspect_checkbox.setChecked(True)
        self.aspect_checkbox.stateChanged.connect(self._on_aspect_changed)
        options_layout.addWidget(self.aspect_checkbox)
        
        # Checkbox para renombrado automático
        self.rename_checkbox = QCheckBox(self.language_manager.get_text("auto_rename", "Renombrar automáticamente según tipo"))
        self.rename_checkbox.setChecked(False)
        self.rename_checkbox.stateChanged.connect(self._on_rename_changed)
        options_layout.addWidget(self.rename_checkbox)
        
        # Grupo de directorio de salida
        self.output_group = QGroupBox(self.language_manager.get_text("output_directory", "Directorio de Salida"))
        output_layout = QHBoxLayout(self.output_group)
        
        # Etiqueta de directorio
        self.output_label = QLabel(self.output_dir)
        self.output_label.setWordWrap(True)
        output_layout.addWidget(self.output_label, 1)
        
        # Botón para seleccionar directorio
        output_btn = QPushButton("...")
        output_btn.setMaximumWidth(30)
        output_btn.clicked.connect(self._select_output_dir)
        output_layout.addWidget(output_btn)
        
        # Botones de acción
        self.action_group = QGroupBox(self.language_manager.get_text("actions", "Acciones"))
        action_layout = QVBoxLayout(self.action_group)
        
        # Botón de conversión
        self.convert_btn = QPushButton(self.language_manager.get_text("convert", "Convertir"))
        self.convert_btn.setObjectName("convert_button")
        self.convert_btn.clicked.connect(self._process_images)
        action_layout.addWidget(self.convert_btn)
        
        # Botón para limpiar selección
        self.clear_btn = QPushButton(self.language_manager.get_text("clear_selection", "Limpiar Selección"))
        self.clear_btn.setObjectName("secondary_button")
        self.clear_btn.clicked.connect(self._clear_selection)
        action_layout.addWidget(self.clear_btn)
        
        # Añadir todos los grupos al layout principal
        layout.addWidget(self.file_group)
        layout.addWidget(self.type_group)
        layout.addWidget(self.options_group)
        layout.addWidget(self.output_group)
        layout.addWidget(self.action_group)
        layout.addStretch()
        
    def _on_type_changed(self, button):
        """Maneja el cambio de tipo de imagen"""
        self.image_type = button.property("type_key")
        self._update_preview()
        
    def _create_preview(self, layout):
        """Crea el área de vista previa"""
        self.preview_group = QGroupBox(self.language_manager.get_text("preview", "Vista Previa"))
        preview_layout = QVBoxLayout(self.preview_group)
        
        # Contenedor para las imágenes
        preview_container = QWidget()
        preview_container_layout = QHBoxLayout(preview_container)
        
        # Panel de imagen original
        self.original_group = QGroupBox(self.language_manager.get_text("original", "Original"))
        original_layout = QVBoxLayout(self.original_group)
        
        # Label para arrastrar y soltar
        self.original_label = DropLabel(self.language_manager.get_text("drag_drop_here", "Arrastra y suelta una imagen aquí"))
        self.original_label.dropped_signal.connect(self._handle_drop)
        original_layout.addWidget(self.original_label)
        
        # Panel de imagen procesada
        self.processed_group = QGroupBox(self.language_manager.get_text("processed", "Procesado"))
        processed_layout = QVBoxLayout(self.processed_group)
        
        # Label para imagen procesada
        self.processed_label = QLabel(self.language_manager.get_text("processed_preview", "Vista previa procesada"))
        self.processed_label.setAlignment(Qt.AlignCenter)
        self.processed_label.setMinimumSize(300, 300)
        theme = self.theme_manager.get_theme()
        self.processed_label.setStyleSheet(f"""
            QLabel {{
                border: 2px solid {theme["border"]};
                border-radius: 8px;
                background-color: {theme["card"]};
                color: {theme["text_secondary"]};
                padding: 10px;
            }}
        """)
        processed_layout.addWidget(self.processed_label)
        
        # Añadir paneles al contenedor
        preview_container_layout.addWidget(self.original_group)
        preview_container_layout.addWidget(self.processed_group)
        
        # Controles de navegación
        nav_container = QWidget()
        nav_layout = QHBoxLayout(nav_container)
        
        self.prev_btn = QPushButton(self.language_manager.get_text("previous", "← Anterior"))
        self.prev_btn.setObjectName("secondary_button")
        self.prev_btn.clicked.connect(self._prev_preview)
        nav_layout.addWidget(self.prev_btn)
        
        self.preview_index_label = QLabel("")
        self.preview_index_label.setAlignment(Qt.AlignCenter)
        nav_layout.addWidget(self.preview_index_label, 1)
        
        self.next_btn = QPushButton(self.language_manager.get_text("next", "Siguiente →"))
        self.next_btn.setObjectName("secondary_button")
        self.next_btn.clicked.connect(self._next_preview)
        nav_layout.addWidget(self.next_btn)
        
        # Añadir todo al layout de vista previa
        preview_layout.addWidget(preview_container)
        preview_layout.addWidget(nav_container)
        
        # Añadir al layout principal
        layout.addWidget(self.preview_group, 3)  # Proporción 3
        
    def _create_history(self, layout):
        """Crea el panel de historial"""
        self.history_group = QGroupBox(self.language_manager.get_text("history", "Historial"))
        history_layout = QVBoxLayout(self.history_group)
        
        # Árbol de historial
        self.history_tree = QTreeWidget()
        self.history_tree.setHeaderLabels([
            self.language_manager.get_text("date", "Fecha"),
            self.language_manager.get_text("type", "Tipo"),
            self.language_manager.get_text("files", "Archivos"),
            self.language_manager.get_text("status", "Estado")
        ])
        self.history_tree.setColumnWidth(0, 150)
        self.history_tree.setColumnWidth(1, 120)
        self.history_tree.setColumnWidth(2, 80)
        self.history_tree.setColumnWidth(3, 100)
        self.history_tree.setAlternatingRowColors(True)
        history_layout.addWidget(self.history_tree)
        
        # Botones de historial
        btn_container = QWidget()
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        
        self.open_folder_btn = QPushButton(self.language_manager.get_text("open_folder", "Abrir Carpeta"))
        self.open_folder_btn.clicked.connect(self._open_selected_history_folder)
        btn_layout.addWidget(self.open_folder_btn)
        
        btn_layout.addStretch()
        
        self.clear_history_btn = QPushButton(self.language_manager.get_text("clear_history", "Limpiar Historial"))
        self.clear_history_btn.setObjectName("secondary_button")
        self.clear_history_btn.clicked.connect(self._clear_history)
        btn_layout.addWidget(self.clear_history_btn)
        
        history_layout.addWidget(btn_container)
        
        # Añadir al layout principal
        layout.addWidget(self.history_group, 2)  # Proporción 2
        
    def _apply_theme(self):
        """Aplica el tema actual a toda la aplicación"""
        self.setStyleSheet(self.theme_manager.get_stylesheet())
        self.original_label.update_theme()
        
        # Actualizar el estilo del label procesado
        theme = self.theme_manager.get_theme()
        self.processed_label.setStyleSheet(f"""
            QLabel {{
                border: 2px solid {theme["border"]};
                border-radius: 8px;
                background-color: {theme["card"]};
                color: {theme["text_secondary"]};
                padding: 10px;
            }}
        """)
        
    def on_theme_changed(self, theme_key):
        """Maneja el cambio de tema"""
        print(f"Aplicando tema: {theme_key}")  # Depuración
        self.theme_manager.set_theme(theme_key)
        self._apply_theme()
        self.theme_button.update_checked_theme(theme_key)
        
    def on_language_changed(self, lang_code):
        """Maneja el cambio de idioma"""
        print(f"Aplicando idioma: {lang_code}")  # Depuración
        self._update_ui_texts()
        
    def _update_ui_texts(self):
        """Actualiza todos los textos de la interfaz según el idioma actual"""
        # Actualizar título de la ventana
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        
        # Actualizar textos de la barra de herramientas
        for action in self.findChildren(QAction):
            if action.text() == "Ayuda" or action.text() == "Help" or action.text() == "Помощь":
                action.setText(self.language_manager.get_text("menu_help", "Ayuda"))
            elif action.text() == "Acerca de" or action.text() == "About" or action.text() == "О программе":
                action.setText(self.language_manager.get_text("menu_about", "Acerca de"))
        
        # Actualizar textos de los grupos
        self.file_group.setTitle(self.language_manager.get_text("file_selection", "Selección de Archivos"))
        self.type_group.setTitle(self.language_manager.get_text("image_type", "Tipo de Imagen"))
        self.options_group.setTitle(self.language_manager.get_text("options", "Opciones"))
        self.output_group.setTitle(self.language_manager.get_text("output_directory", "Directorio de Salida"))
        self.action_group.setTitle(self.language_manager.get_text("actions", "Acciones"))
        self.preview_group.setTitle(self.language_manager.get_text("preview", "Vista Previa"))
        self.original_group.setTitle(self.language_manager.get_text("original", "Original"))
        self.processed_group.setTitle(self.language_manager.get_text("processed", "Procesado"))
        self.history_group.setTitle(self.language_manager.get_text("history", "Historial"))
        
        # Actualizar textos de los botones
        self.select_files_btn.setText(self.language_manager.get_text("select_files", "Seleccionar Archivos"))
        self.select_folder_btn.setText(self.language_manager.get_text("select_folder", "Seleccionar Carpeta"))
        self.convert_btn.setText(self.language_manager.get_text("convert", "Convertir"))
        self.clear_btn.setText(self.language_manager.get_text("clear_selection", "Limpiar Selección"))
        self.prev_btn.setText(self.language_manager.get_text("previous", "← Anterior"))
        self.next_btn.setText(self.language_manager.get_text("next", "Siguiente →"))
        self.open_folder_btn.setText(self.language_manager.get_text("open_folder", "Abrir Carpeta"))
        self.clear_history_btn.setText(self.language_manager.get_text("clear_history", "Limpiar Historial"))
        
        # Actualizar textos de los checkboxes
        self.aspect_checkbox.setText(self.language_manager.get_text("maintain_aspect_ratio", "Mantener relación de aspecto"))
        self.rename_checkbox.setText(self.language_manager.get_text("auto_rename", "Renombrar automáticamente según tipo"))
        
        # Actualizar textos de los radio buttons
        for radio in self.findChildren(QRadioButton):
            type_key = radio.property("type_key")
            if type_key:
                lang_key = self.type_to_key.get(type_key, type_key)
                type_name = self.language_manager.get_text(lang_key, type_key.capitalize())
                dimensions = ImageProcessor.DIMENSIONS.get(type_key, (0, 0))
                radio.setText(f"{type_name} ({dimensions[0]}x{dimensions[1]} px)")
        
        # Actualizar textos de las etiquetas
        if not self.input_files:
            self.files_label.setText(self.language_manager.get_text("no_files_selected", "0 archivos seleccionados"))
            self.original_label.setText(self.language_manager.get_text("drag_drop_here", "Arrastra y suelta una imagen aquí"))
            self.processed_label.setText(self.language_manager.get_text("processed_preview", "Vista previa procesada"))
        else:
            self.files_label.setText(self.language_manager.get_text("files_selected", "{} archivos seleccionados").format(len(self.input_files)))
            if self.current_preview_index < len(self.input_files):
                self.preview_index_label.setText(
                    self.language_manager.get_text("image_count", "Imagen {} de {}").format(
                        self.current_preview_index + 1, len(self.input_files)
                    )
                )
        
        # Actualizar encabezados del árbol de historial
        self.history_tree.setHeaderLabels([
            self.language_manager.get_text("date", "Fecha"),
            self.language_manager.get_text("type", "Tipo"),
            self.language_manager.get_text("files", "Archivos"),
            self.language_manager.get_text("status", "Estado")
        ])
        
        # Actualizar el historial
        self._update_history_tree()
        
    def _show_help(self):
        """Muestra la ayuda de la aplicación"""
        QMessageBox.information(
            self, 
            self.language_manager.get_text("dialog_help_title", "Ayuda"), 
            self.language_manager.get_text("dialog_help_content", 
                "OPL Image Converter - Ayuda\n\n"
                "1. Seleccione archivos o carpetas con imágenes\n"
                "2. Elija el tipo de imagen a convertir\n"
                "3. Configure las opciones deseadas\n"
                "4. Haga clic en 'Convertir' para procesar las imágenes\n\n"
                "También puede arrastrar y soltar imágenes directamente en el área de vista previa."
            )
        )
        
    def _show_about(self):
        """Muestra información sobre la aplicación"""
        about_dialog = AboutDialog(self)
        about_dialog.exec_()
        
    def _on_aspect_changed(self, state):
        """Maneja el cambio en mantener relación de aspecto"""
        self.maintain_aspect = state == Qt.Checked
        self._update_preview()
        
    def _on_rename_changed(self, state):
        """Maneja el cambio en renombrado automático"""
        self.auto_rename = state == Qt.Checked
        
    def _handle_drop(self, file_paths):
        """Maneja el evento de soltar archivos"""
        if file_paths:
            self.input_files = file_paths
            self.files_label.setText(
                self.language_manager.get_text("files_selected", "{} archivos seleccionados").format(len(file_paths))
            )
            self.current_preview_index = 0
            self._update_preview()
            self.status_bar.showMessage(
                self.language_manager.get_text("status_files_loaded", "{} archivos cargados").format(len(file_paths))
            )
        
    def _select_files(self):
        """Abre diálogo para seleccionar archivos"""
        file_filter = "Imágenes (" + " ".join(f"*{ext}" for ext in SUPPORTED_FORMATS) + ")"
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, self.language_manager.get_text("select_files", "Seleccionar Imágenes"), "", file_filter
        )
        
        if file_paths:
            self._handle_drop(file_paths)
            
    def _select_folder(self):
        """Selecciona una carpeta con imágenes"""
        folder = QFileDialog.getExistingDirectory(
            self, self.language_manager.get_text("select_folder", "Seleccionar Carpeta con Imágenes"), ""
        )
        
        if folder:
            file_paths = []
            for root, _, filenames in os.walk(folder):
                for filename in filenames:
                    if ImageProcessor.is_supported_format(filename):
                        file_paths.append(os.path.join(root, filename))
            
            if file_paths:
                self._handle_drop(file_paths)
            else:
                QMessageBox.warning(
                    self, 
                    self.language_manager.get_text("dialog_warning_title", "Sin imágenes"), 
                    self.language_manager.get_text("dialog_warning_no_images", "No se encontraron imágenes compatibles en la carpeta seleccionada.")
                )
                
    def _select_output_dir(self):
        """Selecciona un directorio de salida"""
        folder = QFileDialog.getExistingDirectory(
            self, self.language_manager.get_text("output_directory", "Seleccionar Directorio de Salida"), self.output_dir
        )
        
        if folder:
            self.output_dir = folder
            self.output_label.setText(folder)
            
    def _update_preview(self):
        """Actualiza la vista previa"""
        if not self.input_files:
            self.original_label.setText(self.language_manager.get_text("drag_drop_here", "Arrastra y suelta una imagen aquí"))
            self.original_label.setPixmap(QPixmap())
            self.processed_label.setText(self.language_manager.get_text("processed_preview", "Vista previa procesada"))
            self.processed_label.setPixmap(QPixmap())
            self.preview_index_label.setText("")
            return
        
        self.preview_index_label.setText(
            self.language_manager.get_text("image_count", "Imagen {} de {}").format(
                self.current_preview_index + 1, len(self.input_files)
            )
        )
        
        current_file = self.input_files[self.current_preview_index]
        
        try:
            # Vista previa original
            img = Image.open(current_file)
            img.thumbnail((300, 300))
            
            # Convertir imagen PIL a QPixmap para mostrar
            img_qt = self._pil_to_pixmap(img)
            self.original_label.setText("")
            self.original_label.setPixmap(img_qt)
            
            # Vista previa procesada
            temp_file = os.path.join(TEMP_DIR, "preview.png")
            success, _ = ImageProcessor.convert_resize_image(
                current_file, temp_file, 
                self.image_type, 
                self.maintain_aspect
            )
            
            if success:
                proc_img = Image.open(temp_file)
                proc_img.thumbnail((300, 300))
                proc_img_qt = self._pil_to_pixmap(proc_img)
                self.processed_label.setText("")
                self.processed_label.setPixmap(proc_img_qt)
        except Exception as e:
            logger.error(f"Error actualizando vista previa: {str(e)}")
            QMessageBox.critical(
                self, 
                self.language_manager.get_text("dialog_error_title", "Error"), 
                self.language_manager.get_text("dialog_error_preview", "No se pudo cargar la vista previa: {}").format(str(e))
            )
            
    def _pil_to_pixmap(self, pil_image):
        """Convierte una imagen PIL a QPixmap"""
        if pil_image.mode != "RGBA":
            pil_image = pil_image.convert("RGBA")
        
        data = pil_image.tobytes("raw", "RGBA")
        qimage = QImage(
            data, pil_image.width, pil_image.height, QImage.Format_RGBA8888
        )
        return QPixmap.fromImage(qimage)
            
    def _prev_preview(self):
        """Muestra la imagen anterior"""
        if self.input_files and self.current_preview_index > 0:
            self.current_preview_index -= 1
            self._update_preview()
            
    def _next_preview(self):
        """Muestra la siguiente imagen"""
        if self.input_files and self.current_preview_index < len(self.input_files) - 1:
            self.current_preview_index += 1
            self._update_preview()
            
    def _process_images(self):
        """Inicia el procesamiento de imágenes"""
        if not self.input_files:
            QMessageBox.warning(
                self, 
                self.language_manager.get_text("dialog_warning_title", "Sin archivos"), 
                self.language_manager.get_text("dialog_warning_no_files", "No hay imágenes seleccionadas para procesar")
            )
            return
        
        # Configurar y ejecutar el hilo de procesamiento
        self.processing_thread = ProcessingThread(
            self.input_files, 
            self.output_dir, 
            self.image_type, 
            self.maintain_aspect,
            self.auto_rename
        )
        
        # Conectar señales
        self.processing_thread.progress_signal.connect(self._update_progress)
        self.processing_thread.finished_signal.connect(self._processing_finished)
        
        # Iniciar procesamiento
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(len(self.input_files))
        self.status_bar.showMessage(self.language_manager.get_text("status_processing", "Procesando imágenes..."))
        self.processing_thread.start()
            
    def _update_progress(self, current, total):
        """Actualiza la barra de progreso"""
        self.progress_bar.setValue(current)
        self.status_bar.showMessage(
            self.language_manager.get_text("status_processing_count", "Procesando... {}/{}").format(current, total)
        )
        
    def _processing_finished(self, success_count, total_count):
        """Maneja la finalización del procesamiento"""
        # Actualizar historial
        timestamp = self.processing_thread.timestamp
        batch_dir = os.path.join(self.output_dir, f"{self.image_type}_{timestamp}")
        
        self.history_manager.add_entry({
            "timestamp": timestamp,
            "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "type": self.image_type,
            "total": total_count,
            "success": success_count,
            "directory": batch_dir
        })
        
        # Actualizar interfaz
        self._update_history_tree()
        self.progress_bar.setVisible(False)
        self.status_bar.showMessage(
            self.language_manager.get_text("status_completed", "Proceso completado: {}/{} éxitos").format(success_count, total_count)
        )
        
        # Mostrar mensaje de finalización
        QMessageBox.information(
            self, 
            self.language_manager.get_text("dialog_info_title", "Completado"), 
            self.language_manager.get_text("dialog_info_completed", "Procesadas {} imágenes correctamente").format(success_count)
        )
        
    def _clear_selection(self):
        """Limpia la selección actual"""
        self.input_files = []
        self.files_label.setText(self.language_manager.get_text("no_files_selected", "0 archivos seleccionados"))
        self.original_label.setText(self.language_manager.get_text("drag_drop_here", "Arrastra y suelta una imagen aquí"))
        self.original_label.setPixmap(QPixmap())
        self.processed_label.setText(self.language_manager.get_text("processed_preview", "Vista previa procesada"))
        self.processed_label.setPixmap(QPixmap())
        self.preview_index_label.setText("")
        self.status_bar.showMessage(self.language_manager.get_text("status_selection_cleared", "Selección limpiada"))
        
    def _update_history_tree(self):
        """Actualiza el árbol de historial"""
        self.history_tree.clear()
        
        # Mapeo de tipos de imagen a claves de idioma
        type_to_key = {
            "caratula": "image_type_cover",
            "borde": "image_type_spine",
            "contracaratula": "image_type_back",
            "captura": "image_type_screenshot",
            "fondo": "image_type_background",
            "disco": "image_type_disc",
            "logo": "image_type_logo"
        }
        
        for entry in reversed(self.history_manager.history):
            # Traducir el tipo de imagen
            type_key = entry["type"]
            lang_key = type_to_key.get(type_key, type_key)
            type_name = self.language_manager.get_text(lang_key, type_key.capitalize())
            
            item = QTreeWidgetItem([
                entry["date"],
                type_name,
                str(entry["total"]),
                f"{entry['success']}/{entry['total']}"
            ])
            item.setData(0, Qt.UserRole, entry["timestamp"])
            self.history_tree.addTopLevelItem(item)
            
    def _open_selected_history_folder(self):
        """Abre la carpeta de la entrada seleccionada en el historial"""
        selected_items = self.history_tree.selectedItems()
        if not selected_items:
            QMessageBox.warning(
                self, 
                self.language_manager.get_text("dialog_warning_title", "Selección requerida"), 
                self.language_manager.get_text("dialog_warning_selection_required", "Seleccione un elemento del historial")
            )
            return
            
        item = selected_items[0]
        timestamp = item.data(0, Qt.UserRole)
        
        if entry := next((e for e in self.history_manager.history if e['timestamp'] == timestamp), None):
            self._open_directory(entry['directory'])
        else:
            QMessageBox.critical(
                self, 
                self.language_manager.get_text("dialog_error_title", "Error"), 
                self.language_manager.get_text("dialog_error_history_entry", "Entrada del historial no encontrada")
            )
            
    def _open_directory(self, directory):
        """Abre un directorio en el explorador del sistema"""
        try:
            system = platform.system()
            if system == 'Windows':
                os.startfile(directory)
            elif system == 'Darwin':
                subprocess.run(['open', directory], check=True)
            else:
                subprocess.run(['xdg-open', directory], check=True)
            self.status_bar.showMessage(
                self.language_manager.get_text("status_directory_opened", "Directorio abierto: {}").format(directory)
            )
            logger.info(f"Directorio abierto: {directory}")
        except Exception as e:
            logger.error(f"Error abriendo directorio: {str(e)}")
            QMessageBox.critical(
                self, 
                self.language_manager.get_text("dialog_error_title", "Error"), 
                self.language_manager.get_text("dialog_error_directory", "No se pudo abrir el directorio:\n{}").format(str(e))
            )
            
    def _clear_history(self):
        """Limpia todo el historial"""
        reply = QMessageBox.question(
            self, 
            self.language_manager.get_text("dialog_confirm_title", "Confirmar"), 
            self.language_manager.get_text("dialog_confirm_clear_history", "¿Borrar todo el historial?"),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.history_manager.history = []
            self.history_manager.save_history()
            self._update_history_tree()
            self.status_bar.showMessage(self.language_manager.get_text("status_history_cleared", "Historial limpiado"))

def main():
    """Función principal de la aplicación"""
    try:
        # Crear directorio de salida por defecto si no existe
        if not os.path.exists(DEFAULT_OUTPUT_DIR):
            os.makedirs(DEFAULT_OUTPUT_DIR)
            
        # Crear directorio temporal si no existe
        if not os.path.exists(TEMP_DIR):
            os.makedirs(TEMP_DIR)
            
        # Iniciar aplicación
        app = QApplication(sys.argv)
        window = OPLImageConverterApp()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        logger.critical(f"Error crítico: {str(e)}", exc_info=True)
        if QApplication.instance():
            QMessageBox.critical(
                None, "Error Fatal", 
                f"Ha ocurrido un error irreparable:\n{str(e)}"
            )
        sys.exit(1)

if __name__ == "__main__":
    main()

