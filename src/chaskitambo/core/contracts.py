# D:\libs\chaskitambo\src\chaskitambo\core\contracts.py
from datetime import datetime, timezone  # <-- CORREGIDO: Importamos timezone explícitamente
from typing import Any, Dict
from pydantic import BaseModel, ConfigDict, Field


class ChaskiDocument(BaseModel):
    """Contrato de datos universal y estricto que todo plugin de Chaskitambo

    debe retornar, independiente de la fuente de origen (REMAJU, SUNARP, etc.).
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    id_externo: str = Field(
        ...,
        description="Identificador único del documento (ej. expediente, partida).",
    )
    fuente: str = Field(
        ...,
        description="Nombre de la fuente de origen ('remaju', 'sunarp', etc.).",
    )
    metadatos: Dict[str, Any] = Field(
        default_factory=dict,
        description="Diccionario flexible para cualquier atributo particular de la fuente (ej. convocatoria, registrador, etc.).",
    )
    pdf_bytes: bytes = Field(
        ..., description="El documento PDF en formato de bytes crudos."
    )
    nombre_archivo_sugerido: str = Field(
        ..., description="Nombre sugerido para guardar o referenciar el PDF."
    )

    # CORREGIDO: Cambiado 'datetime.timezone.utc' por 'timezone.utc' directamente
    fecha_extraccion: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp UTC de la extracción.",
    )
