"""
Botón de selección de idioma para OPL Image Converter
"""
from PyQt5.QtWidgets import QToolButton, QMenu, QAction
from PyQt5.QtCore import Qt
from .language_manager import LanguageManager, language_signal

class LanguageButton(QToolButton):
    """Botón personalizado para seleccionar el idioma"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.language_manager = LanguageManager()
        self.setPopupMode(QToolButton.InstantPopup)
        self.setText("🌐")
        self.setToolTip(self.language_manager.get_text("menu_language", "Idioma"))
        
        # Crear menú de idiomas
        self.language_menu = QMenu(self)
        
        # Añadir opciones de idioma
        available_languages = self.language_manager.get_available_languages()
        for lang_code, lang_info in available_languages.items():
            # Usar el nombre con la bandera para el menú
            display_name = f"{lang_info['flag']} {lang_info['display_name']}"
            self.add_language_action(lang_code, display_name)
        
        self.setMenu(self.language_menu)
        self.setStyleSheet("""
            QToolButton {
                font-size: 16px;
                padding: 5px;
                border: none;
            }
        """)
        
        # Actualizar el estado inicial
        self.update_checked_language(self.language_manager.current_language)
        
        # Conectar señal de cambio de idioma para actualizar el botón
        language_signal.language_changed.connect(self.update_checked_language)
        
    def add_language_action(self, lang_code, display_name):
        """Añade una acción al menú de idiomas"""
        action = QAction(display_name, self)
        action.setData(lang_code)
        action.setCheckable(True)
        action.setChecked(self.language_manager.current_language == lang_code)
        action.triggered.connect(lambda checked, k=lang_code: self.on_language_selected(k))
        self.language_menu.addAction(action)
        
    def on_language_selected(self, lang_code):
        """Maneja la selección de un idioma"""
        # Cambiar el idioma
        success = self.language_manager.change_language(lang_code)
        print(f"Cambio de idioma a {lang_code}: {'exitoso' if success else 'fallido'}")
        
    def update_checked_language(self, lang_code):
        """Actualiza el idioma seleccionado en el menú"""
        for action in self.language_menu.actions():
            action.setChecked(action.data() == lang_code)

