"""
Componente de botón de tema mejorado para la aplicación
"""
from PyQt5.QtWidgets import QToolButton, QMenu, QAction
from theme_config import ThemeManager
from app_integration import theme_signal

class ThemeButton(QToolButton):
    """Botón personalizado para seleccionar el tema con soporte para tema automático del sistema"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPopupMode(QToolButton.InstantPopup)
        self.setText("⚙️")
        self.setToolTip("Cambiar tema")
        
        # Crear menú de temas
        self.theme_menu = QMenu(self)
        
        # Añadir opciones de tema
        self.add_theme_action("system", "Sistema (Auto)")
        self.add_theme_action("light", "Modo Claro")
        self.add_theme_action("dark", "Modo Oscuro")
        self.add_theme_action("purple", "Púrpura")
        self.add_theme_action("dark_purple", "Púrpura Oscuro")
        
        self.setMenu(self.theme_menu)
        self.setStyleSheet("""
            QToolButton {
                font-size: 16px;
                padding: 5px;
                border: none;
            }
        """)
        
    def add_theme_action(self, theme_key, theme_name):
        """Añade una acción al menú de temas"""
        action = QAction(theme_name, self)
        action.setData(theme_key)
        action.setCheckable(True)
        action.setChecked(False)  # Se actualizará después
        action.triggered.connect(lambda checked, k=theme_key: self.on_theme_selected(k))
        self.theme_menu.addAction(action)
        
    def on_theme_selected(self, theme_key):
        """Maneja la selección de un tema"""
        # Actualizar estado de las acciones
        for act in self.theme_menu.actions():
            act.setChecked(act.data() == theme_key)
        
        # Emitir señal global de cambio de tema
        theme_signal.theme_changed.emit(theme_key)
        
    def update_checked_theme(self, theme_key):
        """Actualiza el tema seleccionado en el menú"""
        for action in self.theme_menu.actions():
            action.setChecked(action.data() == theme_key)

