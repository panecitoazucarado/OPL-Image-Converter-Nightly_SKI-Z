"""
Gestor de idiomas para OPL Image Converter
Este módulo maneja la carga y cambio de idiomas en la aplicación
"""
import os
import json
import logging
import locale
import platform
from typing import Dict, Optional, Tuple
from PyQt5.QtCore import QObject, pyqtSignal, QSettings, QLocale

logger = logging.getLogger(__name__)

# Señal personalizada para cambio de idioma
class LanguageChangedSignal(QObject):
    language_changed = pyqtSignal(str)

# Variable global para la señal de idioma
language_signal = LanguageChangedSignal()

# Mapeo de códigos de idioma a banderas y nombres completos
LANGUAGE_FLAGS = {
    "es": {"flag": "🇪🇸", "name": "Español (España)"},
    "es_mx": {"flag": "🇲🇽", "name": "Español (México)"},
    "es_ar": {"flag": "🇦🇷", "name": "Español (Argentina)"},
    "en": {"flag": "🇺🇸", "name": "English (US)"},
    "en_gb": {"flag": "🇬🇧", "name": "English (UK)"},
    "ru": {"flag": "🇷🇺", "name": "Русский"},
    "gn_bo": {"flag": "🇧🇴", "name": "Guaraní (Bolivia)"},
    "gn_py": {"flag": "🇵🇾", "name": "Guaraní (Paraguay)"},
    "qu_pe": {"flag": "🇵🇪", "name": "Quechua (Perú)"},
    "qu_bo": {"flag": "🇧🇴", "name": "Quechua (Bolivia)"},
    "pt_br": {"flag": "🇧🇷", "name": "Português (Brasil)"},
    "de": {"flag": "🇩🇪", "name": "Deutsch"},
    "fr": {"flag": "🇫🇷", "name": "Français"},
    "it": {"flag": "🇮🇹", "name": "Italiano"},
    "ja": {"flag": "🇯🇵", "name": "日本語"},
    "ko": {"flag": "🇰🇷", "name": "한국어"},
    "zh_cn": {"flag": "🇨🇳", "name": "中文 (简体)"},
    "zh_tw": {"flag": "🇹🇼", "name": "中文 (繁體)"}
}

class LanguageManager:
    """Gestor de idiomas para la aplicación"""
    
    _instance = None
    
    def __new__(cls):
        """Implementación del patrón Singleton para asegurar una única instancia"""
        if cls._instance is None:
            cls._instance = super(LanguageManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Inicializa el gestor de idiomas"""
        # Evitar reinicialización si ya está inicializado (Singleton)
        if self._initialized:
            return
            
        self._initialized = True
        self.settings = QSettings("OPLManager", "ImageConverter")
        self.languages = {}
        self.available_languages = {}
        self._load_available_languages()
        
        # Detectar idioma del sistema
        system_language = self._detect_system_language()
        
        # Cargar idioma guardado o usar el del sistema (o español por defecto)
        saved_language = self.settings.value("language", None)
        
        if saved_language and saved_language in self.available_languages:
            # Usar el idioma guardado si está disponible
            self.current_language = saved_language
        elif system_language in self.available_languages:
            # Usar el idioma del sistema si está disponible
            self.current_language = system_language
        else:
            # Usar español por defecto
            self.current_language = "es"
        
        # Guardar el idioma actual
        self.settings.setValue("language", self.current_language)
        
        # Cargar el idioma actual
        self._load_language(self.current_language)
        
        # Imprimir información de depuración
        print(f"Idioma del sistema detectado: {system_language}")
        print(f"Idioma guardado: {saved_language}")
        print(f"Idioma actual: {self.current_language}")
        print(f"Idiomas disponibles: {list(self.available_languages.keys())}")
    
    def _detect_system_language(self) -> str:
        """
        Detecta el idioma del sistema operativo
        
        Returns:
            str: Código de idioma de dos letras (es, en, ru, etc.)
        """
        try:
            # Intentar obtener el idioma del sistema usando QLocale
            system_locale = QLocale.system().name()
            language_code = system_locale.split('_')[0].lower()
            
            # Si no se pudo obtener o es un código no estándar, intentar con locale
            if not language_code or len(language_code) != 2:
                # Intentar con locale
                try:
                    current_locale = locale.getlocale()[0]
                    if current_locale:
                        language_code = current_locale.split('_')[0].lower()
                except:
                    pass
            
            # Si aún no tenemos un código válido, intentar con variables de entorno
            if not language_code or len(language_code) != 2:
                env_lang = os.environ.get('LANG') or os.environ.get('LANGUAGE') or os.environ.get('LC_ALL')
                if env_lang:
                    language_code = env_lang.split('_')[0].lower()
            
            # Si todo falla, usar 'es' por defecto
            if not language_code or len(language_code) != 2:
                return 'es'
                
            return language_code
            
        except Exception as e:
            logger.error(f"Error detectando idioma del sistema: {str(e)}")
            return 'es'  # Español por defecto
    
    def _load_available_languages(self):
        """Carga la lista de idiomas disponibles"""
        try:
            # Directorio donde se encuentran los archivos de idioma
            languages_dir = os.path.join(os.path.dirname(__file__), "translations")
            
            # Verificar que el directorio existe
            if not os.path.exists(languages_dir):
                logger.error(f"Directorio de idiomas no encontrado: {languages_dir}")
                return
            
            # Buscar archivos de idioma
            for filename in os.listdir(languages_dir):
                if filename.endswith(".json"):
                    language_code = filename.split(".")[0]
                    language_path = os.path.join(languages_dir, filename)
                    
                    # Cargar el nombre del idioma desde el archivo
                    try:
                        with open(language_path, 'r', encoding='utf-8') as f:
                            language_data = json.load(f)
                            language_name = language_data.get("language_name", language_code)
                            
                            # Obtener la bandera y el nombre completo del idioma
                            flag = ""
                            display_name = language_name
                            
                            if language_code in LANGUAGE_FLAGS:
                                flag = LANGUAGE_FLAGS[language_code]["flag"]
                                # Usar el nombre del archivo JSON si está disponible, de lo contrario usar el predeterminado
                                if not language_data.get("use_default_name", False):
                                    display_name = language_name
                                else:
                                    display_name = LANGUAGE_FLAGS[language_code]["name"]
                            
                            self.available_languages[language_code] = {
                                "name": language_name,
                                "display_name": display_name,
                                "flag": flag,
                                "path": language_path
                            }
                    except Exception as e:
                        logger.error(f"Error cargando información del idioma {language_code}: {str(e)}")
        
        except Exception as e:
            logger.error(f"Error cargando idiomas disponibles: {str(e)}")
    
    def _load_language(self, language_code: str) -> bool:
        """
        Carga un idioma específico
        
        Args:
            language_code: Código del idioma a cargar
            
        Returns:
            bool: True si se cargó correctamente, False en caso contrario
        """
        try:
            # Verificar si el idioma está disponible
            if language_code not in self.available_languages:
                logger.error(f"Idioma no disponible: {language_code}")
                # Si el idioma solicitado no está disponible, intentar cargar español
                if language_code != "es" and "es" in self.available_languages:
                    return self._load_language("es")
                return False
            
            # Cargar el archivo de idioma
            language_path = self.available_languages[language_code]["path"]
            with open(language_path, 'r', encoding='utf-8') as f:
                self.languages[language_code] = json.load(f)
            
            # Establecer como idioma actual
            self.current_language = language_code
            self.settings.setValue("language", language_code)
            
            return True
        
        except Exception as e:
            logger.error(f"Error cargando idioma {language_code}: {str(e)}")
            return False
    
    def get_text(self, key: str, default: Optional[str] = None) -> str:
        """
        Obtiene un texto en el idioma actual
        
        Args:
            key: Clave del texto a obtener
            default: Texto por defecto si no se encuentra la clave
            
        Returns:
            str: Texto traducido o valor por defecto
        """
        # Si no hay idioma cargado, devolver el valor por defecto
        if not self.languages or self.current_language not in self.languages:
            return default if default is not None else key
        
        # Buscar la clave en el idioma actual
        return self.languages[self.current_language].get(key, default if default is not None else key)
    
    def change_language(self, language_code: str) -> bool:
        """
        Cambia el idioma actual
        
        Args:
            language_code: Código del idioma a establecer
            
        Returns:
            bool: True si se cambió correctamente, False en caso contrario
        """
        # Si es el mismo idioma, no hacer nada
        if language_code == self.current_language:
            return True
        
        # Cargar el nuevo idioma
        if self._load_language(language_code):
            # Emitir señal de cambio de idioma
            language_signal.language_changed.emit(language_code)
            print(f"Idioma cambiado a: {language_code}")  # Depuración
            return True
        
        return False
    
    def get_available_languages(self) -> Dict[str, Dict[str, str]]:
        """
        Obtiene la lista de idiomas disponibles con sus banderas y nombres
        
        Returns:
            Dict[str, Dict[str, str]]: Diccionario con códigos, nombres y banderas de idiomas
        """
        return self.available_languages
    
    def get_language_display_name(self, language_code: str) -> str:
        """
        Obtiene el nombre de visualización completo de un idioma con su bandera
        
        Args:
            language_code: Código del idioma
            
        Returns:
            str: Nombre del idioma con su bandera
        """
        if language_code in self.available_languages:
            lang_info = self.available_languages[language_code]
            return f"{lang_info['flag']} {lang_info['display_name']}"
        return language_code

