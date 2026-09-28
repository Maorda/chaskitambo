# D:\libs\chaskitambo\src\chaskitambo\core\engine.py
import asyncio
from loguru import logger
from typing import Optional, List, Callable, Awaitable
from .plugin_manager import PluginManager
from .contracts import ChaskiDocument

class ChaskitamboEngine:
    """
    Motor central de orquestación de Chaskitambo. Capaz de ejecutar
    múltiples plugins en paralelo recolectando datos concurrentemente,
    pero garantizando un despacho secuencial y ordenado hacia chaskywasi.
    """

    def __init__(self):
        self.plugins = PluginManager.discover_plugins()

    def list_available_plugins(self) -> List[str]:
        """Retorna la lista de nombres de plugins de raspado detectados."""
        return list(self.plugins.keys())

    async def _producer_task(self, plugin_name: str, queue: asyncio.Queue):
        """Tarea productora: Ejecuta un plugin y añade sus documentos a la cola central."""
        if plugin_name not in self.plugins:
            logger.error(f" -> [ERROR] El plugin '{plugin_name}' no está registrado.")
            return

        plugin_class = self.plugins[plugin_name]
        scraper = plugin_class()

        logger.info(f" -> [PRODUCER] Lanzando raspado paralelo para: '{plugin_name}'...")
        try:
            async for document in scraper.extract():
                if isinstance(document, ChaskiDocument):
                    # Inyectamos el documento en la cola concurrente
                    await queue.put(document)
                else:
                    logger.warning(f" -> [WARNING] '{plugin_name}' emitió un objeto inválido.")
        except Exception:
            logger.exception(f" -> [ERROR] Error crítico en el productor del plugin '{plugin_name}'")

    async def _consumer_task(self, queue: asyncio.Queue, handler: Callable[[ChaskiDocument], Awaitable[None]]):
        """Tarea consumidora: Procesa secuencialmente los documentos de la cola en orden de llegada."""
        while True:
            document = await queue.get()
            
            # Condición de parada (Sentinel/Poison Pill)
            if document is None:
                queue.task_done()
                break

            try:
                logger.info(f" -> [ENGINE] Despachando secuencialmente -> ID: {document.id_externo} | Fuente: {document.fuente}")
                # Ejecución estrictamente secuencial (esperamos a que termine antes de pasar al siguiente)
                await handler(document)
            except Exception:
                logger.exception(f" -> [ERROR] Falló el procesamiento secuencial del documento {document.id_externo}")
            finally:
                queue.task_done()

    async def run_plugins_parallel(
        self, 
        plugin_names: List[str], 
        chaskywasi_handler: Optional[Callable[[ChaskiDocument], Awaitable[None]]] = None
    ):
        """
        Ejecuta una lista de plugins en paralelo, pero procesa sus salidas
        de forma secuencial a través del manejador de chaskywasi.
        """
        # Validar que existan los plugins solicitados
        plugins_validos = [name for name in plugin_names if name in self.plugins]
        if not plugins_validos:
            logger.error(" -> [ENGINE] No hay plugins válidos seleccionados para ejecutar.")
            return

        # Creamos una cola asíncrona ilimitada
        queue = asyncio.Queue()

        # 1. Configurar y arrancar el Consumidor Secuencial
        # Si no hay handler, creamos uno por defecto para auditoría en consola
        if not chaskywasi_handler:
            async def default_handler(doc):
                logger.info(f" -> [MOCK-CHASKIWASI] Guardado secuencial: {doc.id_externo}")
            chaskywasi_handler = default_handler

        consumer = asyncio.create_task(self._consumer_task(queue, chaskywasi_handler))

        # 2. Configurar y lanzar todos los Productores en Paralelo
        logger.info(f" -> [ENGINE] Iniciando procesamiento paralelo de {len(plugins_validos)} plugins...")
        producer_tasks = [
            asyncio.create_task(self._producer_task(name, queue)) 
            for name in plugins_validos
        ]

        # Esperamos a que todos los scrapers/productores terminen sus páginas web por completo
        await asyncio.gather(*producer_tasks)
        logger.info(" -> [ENGINE] Todos los plugins productores han terminado de raspar la web.")

        # 3. Enviar la 'píldora venenosa' (None) para apagar el consumidor secuencial de forma limpia
        await queue.put(None)
        
        # Esperamos a que el consumidor termine de procesar los documentos que quedaban haciendo fila
        await consumer
        logger.info(" -> [ENGINE] Orquestación paralela con salida secuencial finalizada con éxito.")
