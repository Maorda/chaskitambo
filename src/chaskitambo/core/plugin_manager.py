import importlib.metadata
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger
from typing import Dict, Callable

class PluginManager:
    GROUP_NAME = "chaskitambo.plugins"

    @classmethod
    def discover_plugins(cls) -> Dict[str, Callable]:
        plugins = {}
        
        # 1. Carga autónoma del .env de chaskitambo para no depender del directorio desde donde se llama la CLI
        chaskitambo_env = Path(__file__).resolve().parents[2] / ".env"
        if chaskitambo_env.exists():
            load_dotenv(dotenv_path=chaskitambo_env)

        try:
            eps = importlib.metadata.entry_points()
            
            if hasattr(eps, "select"):
                group_eps = eps.select(group=cls.GROUP_NAME)
            else:
                group_eps = eps.get(cls.GROUP_NAME, [])

            # 2. Bucle aislado: si un plugin falla al importar, no destruye la lista general
            for ep in group_eps:
                try:
                    plugin_version = ep.dist.version if ep.dist else "Desconocida"
                    logger.info(f" -> [PLUGIN] Detectado: '{ep.name}' | Versión Indexada: v{plugin_version} | Origen: {ep.value}")
                    
                    # Intento de carga individual de la clase del scraper
                    plugins[ep.name] = ep.load()
                except Exception:
                    logger.exception(f" -> [ERROR] Falló la importación/carga del plugin '{ep.name}'")
                
        except Exception:
            logger.exception(" -> [ERROR] Falló la consulta de Entry Points en el sistema")
            
        return plugins