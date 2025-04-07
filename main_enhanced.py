"""
Punto de entrada mejorado para OPL Image Converter con soporte para algoritmos de escalado
"""
import os
import sys
import logging
from PyQt5.QtWidgets import QApplication, QToolBar

# Importar la aplicación original
from opl_image_converter_pyqt import OPLImageConverterApp, DEFAULT_OUTPUT_DIR, TEMP_DIR

# Importar la integración de la interfaz de usuario
from image_scaling.ui_integration import integrate_scaling_ui

def main():
    """Función principal de la aplicación mejorada"""
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
        
        # Integrar componentes de escalado
        toolbar = window.findChild(QToolBar)
        integrate_scaling_ui(window, toolbar, window.options_group.layout())
        
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        logging.critical(f"Error crítico: {str(e)}", exc_info=True)
        from PyQt5.QtWidgets import QMessageBox
        if QApplication.instance():
            QMessageBox.critical(
                None, "Error Fatal", 
                f"Ha ocurrido un error irreparable:\n{str(e)}"
            )
        sys.exit(1)

if __name__ == "__main__":
    main()

