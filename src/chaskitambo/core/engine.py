from loguru import logger
from typing import Optional, List, Callable, Awaitable
from .plugin_manager import PluginManager
from .contracts import ChaskiDocument

class ChaskitamboEngine:
    """
    Motor central de orquestación de Chaskitambo. Descubre los plugins,
    coordina su ejecución y despacha los documentos validados hacia chaskywasi.
    """

    def __init__(self):
        self.plugins = PluginManager.discover_plugins()

    def list_available_plugins(self) -> List[str]:
        """Retorna la lista de nombres de plugins de raspado detectados en el entorno."""
        return list(self.plugins.keys())

    async def run_plugin(
        self, 
        plugin_name: str, 
        chaskywasi_handler: Optional[Callable[[ChaskiDocument], Awaitable[None]]] = None
    ):
        """
        Ejecuta un plugin específico de forma autónoma y canaliza 
        cada ChaskiDocument generado hacia el motor de chaskywasi.
        """
        if plugin_name not in self.plugins:
            logger.error(f" -> [ERROR] El plugin '{plugin_name}' no se encuentra registrado en el sistema.")
            return

        plugin_class = self.plugins[plugin_name]
        scraper = plugin_class()

        logger.info(f" -> [ENGINE] Iniciando extracción autónoma con el plugin: '{plugin_name}'...")
        
        try:
            async for document in scraper.extract():
                # Validación estricta del contrato Pydantic
                if isinstance(document, ChaskiDocument):
                    logger.info(f" -> [OK] Documento capturado -> ID: {document.id_externo} | Fuente: {document.fuente}")
                    
                    # Si se proveyó el manejador de chaskywasi, despachamos el documento
                    if chaskywasi_handler:
                        await chaskywasi_handler(document)
                else:
                    logger.warning(f" -> [WARNING] El plugin '{plugin_name}' emitió un objeto que no cumple con ChaskiDocument.")
                    
        except Exception as e:
            logger.error(f" -> [ERROR] Falló la ejecución del plugin '{plugin_name}': {e}")