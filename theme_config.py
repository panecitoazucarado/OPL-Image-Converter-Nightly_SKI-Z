"""
Configuración de temas para OPL Image Converter
Este archivo contiene todas las definiciones de colores y estilos para los diferentes temas
"""
import platform
import subprocess
import threading
import time
from typing import Callable, Optional

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

# Tema predeterminado
DEFAULT_THEME = "light"

class SystemThemeMonitor:
    """Monitorea cambios en el tema del sistema operativo"""
    
    def __init__(self, callback: Callable[[bool], None]):
        """
        Inicializa el monitor de tema del sistema
        
        Args:
            callback: Función a llamar cuando cambia el tema del sistema.
                     Recibe un booleano que indica si el tema es oscuro.
        """
        self.callback = callback
        self._running = False
        self._monitor_thread = None
        self._last_is_dark = None
    
    def start(self):
        """Inicia el monitoreo del tema del sistema"""
        if self._running:
            return
        
        self._running = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
    
    def stop(self):
        """Detiene el monitoreo del tema del sistema"""
        self._running = False
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=1.0)
    
    def _monitor_loop(self):
        """Bucle principal de monitoreo"""
        while self._running:
            try:
                is_dark = self._detect_system_theme()
                
                # Si el estado ha cambiado, notificar
                if is_dark != self._last_is_dark:
                    self._last_is_dark = is_dark
                    self.callback(is_dark)
                
                # Esperar antes de la siguiente comprobación
                time.sleep(1.0)  # Comprobar cada segundo
            except Exception as e:
                print(f"Error en el monitor de tema: {e}")
                time.sleep(5.0)  # Esperar más tiempo si hay un error
    
    def _detect_system_theme(self) -> bool:
        """
        Detecta si el sistema está usando tema oscuro
        
        Returns:
            bool: True si el sistema usa tema oscuro, False en caso contrario
        """
        system = platform.system()
        
        if system == "Windows":
            try:
                import winreg
                registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
                key = winreg.OpenKey(registry, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
                value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                return value == 0
            except Exception:
                return False
                
        elif system == "Darwin":  # macOS
            try:
                result = subprocess.run(
                    ["defaults", "read", "-g", "AppleInterfaceStyle"],
                    capture_output=True, text=True
                )
                return result.stdout.strip() == "Dark"
            except Exception:
                return False
                
        else:  # Linux y otros
            try:
                # Intenta detectar en entornos GNOME
                result = subprocess.run(
                    ["gsettings", "get", "org.gnome.desktop.interface", "gtk-theme"],
                    capture_output=True, text=True
                )
                return "dark" in result.stdout.lower()
            except Exception:
                # Intenta detectar en entornos KDE
                try:
                    result = subprocess.run(
                        ["kreadconfig5", "--group", "General", "--key", "ColorScheme"],
                        capture_output=True, text=True
                    )
                    return "dark" in result.stdout.lower()
                except Exception:
                    return False

class ThemeManager:
    """Gestor de temas para la aplicación con detección automática del tema del sistema"""
    
    def __init__(self, theme_changed_callback: Optional[Callable[[str], None]] = None):
        """
        Inicializa el gestor de temas
        
        Args:
            theme_changed_callback: Función opcional a llamar cuando cambia el tema.
                                   Recibe el nombre del tema como parámetro.
        """
        self._theme_changed_callback = theme_changed_callback
        self._current_theme = "system"  # Por defecto, usar el tema del sistema
        self._system_is_dark = False
        
        # Iniciar el monitor de tema del sistema
        self._system_monitor = SystemThemeMonitor(self._on_system_theme_changed)
        self._system_monitor.start()
        
        # Detectar el tema inicial del sistema
        self._system_is_dark = self._system_monitor._detect_system_theme()
    
    def _on_system_theme_changed(self, is_dark: bool):
        """
        Maneja los cambios en el tema del sistema
        
        Args:
            is_dark: True si el sistema cambió a tema oscuro, False si cambió a claro
        """
        if self._system_is_dark != is_dark:
            self._system_is_dark = is_dark
            
            # Solo notificar si estamos usando el tema del sistema
            if self._current_theme == "system" and self._theme_changed_callback:
                theme_name = self.get_theme_name()
                self._theme_changed_callback(theme_name)
    
    def get_theme_name(self) -> str:
        """
        Obtiene el nombre del tema actual
        
        Returns:
            str: Nombre del tema actual
        """
        if self._current_theme == "system":
            return "dark" if self._system_is_dark else "light"
        return self._current_theme
    
    def get_theme(self) -> dict:
        """
        Obtiene el diccionario de colores del tema actual
        
        Returns:
            dict: Diccionario con los colores del tema
        """
        theme_name = self.get_theme_name()
        return THEMES[theme_name]
    
    def set_theme(self, theme_name: str) -> bool:
        """
        Establece el tema actual
        
        Args:
            theme_name: Nombre del tema a establecer
            
        Returns:
            bool: True si se estableció correctamente, False en caso contrario
        """
        if theme_name in THEMES or theme_name == "system":
            old_theme = self.get_theme_name()
            self._current_theme = theme_name
            
            # Notificar el cambio si es necesario
            new_theme = self.get_theme_name()
            if old_theme != new_theme and self._theme_changed_callback:
                self._theme_changed_callback(new_theme)
                
            return True
        return False
    
    def cleanup(self):
        """Limpia los recursos utilizados por el gestor de temas"""
        if self._system_monitor:
            self._system_monitor.stop()

def get_stylesheet(theme):
    """Genera la hoja de estilos CSS para el tema especificado"""
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

def get_drop_label_style(theme, is_drag_over=False):
    """Genera el estilo para el DropLabel según el tema"""
    if is_drag_over:
        return f"""
            QLabel {{
                border: 2px dashed {theme["drop_border"]};
                border-radius: 8px;
                background-color: {theme["drop_target"]};
                color: {theme["text"]};
                padding: 10px;
            }}
        """
    else:
        return f"""
            QLabel {{
                border: 2px dashed {theme["border"]};
                border-radius: 8px;
                background-color: {theme["card"]};
                color: {theme["text_secondary"]};
                padding: 10px;
            }}
            QLabel:hover {{
                border-color: {theme["primary"]};
            }}
        """

def get_processed_label_style(theme):
    """Genera el estilo para el label de imagen procesada"""
    return f"""
        QLabel {{
            border: 2px solid {theme["border"]};
            border-radius: 8px;
            background-color: {theme["card"]};
            color: {theme["text_secondary"]};
            padding: 10px;
        }}
    """

def get_theme_button_style():
    """Genera el estilo para el botón de tema"""
    return """
        QToolButton {
            font-size: 16px;
            padding: 5px;
            border: none;
        }
    """

