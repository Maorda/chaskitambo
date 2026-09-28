# D:\libs\chaskitambo\src\chaskitambo\core\plugin_manager.py
import importlib.metadata
from loguru import logger
from typing import Dict, Callable

class PluginManager:
    GROUP_NAME = "chaskitambo.plugins"

    @classmethod
    def discover_plugins(cls) -> Dict[str, Callable]:
        plugins = {}
        try:
            eps = importlib.metadata.entry_points()
            
            if hasattr(eps, "select"):
                group_eps = eps.select(group=cls.GROUP_NAME)
            else:
                group_eps = eps.get(cls.GROUP_NAME, [])

            for ep in group_eps:
                # MODIFICADO: Extraemos la versión real del paquete que registra el Entry Point
                plugin_version = ep.dist.version if ep.dist else "Desconocida"
                
                logger.info(f" -> [PLUGIN] Detectado: '{ep.name}' | Versión Indexada: v{plugin_version} | Origen: {ep.value}")
                plugins[ep.name] = ep.load()
                
        except Exception as e:
            logger.error(f" -> [ERROR] Falló el descubrimiento de plugins: {e}")
            
        return plugins
