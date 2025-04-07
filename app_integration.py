"""
Código de integración para conectar el ThemeManager con la aplicación PyQt
"""
from PyQt5.QtCore import QObject, pyqtSignal

# Señal personalizada para cambio de tema
class ThemeChangedSignal(QObject):
    theme_changed = pyqtSignal(str)

# Variable global para la señal de tema
theme_signal = ThemeChangedSignal()

