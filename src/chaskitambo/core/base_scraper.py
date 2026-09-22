from abc import ABC, abstractmethod
from typing import AsyncGenerator
from .contracts import ChaskiDocument

class BaseScraper(ABC):
    """
    Clase base abstracta que todo plugin de Chaskitambo debe heredar e implementar.
    Garantiza que la interfaz de autenticación y extracción sea idéntica para cualquier fuente.
    """

    @abstractmethod
    async def extract(self) -> AsyncGenerator[ChaskiDocument, None]:
        """
        Método generador asíncrono que ejecuta la navegación web, 
        extrae los metadatos, descarga el PDF en bytes y emite 
        objetos ChaskiDocument validados hacia el motor.
        """
        pass