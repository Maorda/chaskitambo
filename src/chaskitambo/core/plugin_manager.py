import importlib.metadata
from loguru import logger
from typing import Dict, Callable

class PluginManager:
    """
    Gestor responsable de descubrir y cargar de forma dinámica los plugins 
    de raspado registrados mediante Entry Points de Python.
    """
    GROUP_NAME = "chaskitambo.plugins"

    @classmethod
    def discover_plugins(cls) -> Dict[str, Callable]:
        """
        Escanea el entorno en busca de plugins registrados bajo el grupo 'chaskitambo.plugins'.
        Retorna un diccionario con el nombre del plugin y su clase o función principal cargada.
        """
        plugins = {}
        try:
            # Compatibilidad estándar con importlib.metadata (Python 3.10+)
            eps = importlib.metadata.entry_points()
            
            # Manejo según la versión de importlib.metadata
            if hasattr(eps, "select"):
                group_eps = eps.select(group=cls.GROUP_NAME)
            else:
                group_eps = eps.get(cls.GROUP_NAME, [])

            for ep in group_eps:
                logger.info(f" -> [PLUGIN] Detectado: '{ep.name}' ({ep.value})")
                plugins[ep.name] = ep.load()
                
        except Exception as e:
            logger.error(f" -> [ERROR] Falló el descubrimiento de plugins: {e}")
            
        return plugins