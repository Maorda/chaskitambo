# D:\libs\chaskitambo\src\chaskitambo\core\contracts.py
from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Any
from datetime import datetime

class ChaskiDocument(BaseModel):
    """
    Contrato de datos universal y estricto que todo plugin de Chaskitambo
    debe retornar, independiente de la fuente de origen (REMAJU, SUNARP, etc.).
    """
    # CORREGIDO: Configuración nativa para Pydantic v2.0+
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id_externo: str = Field(..., description="Identificador único del documento (ej. expediente, partida).")
    fuente: str = Field(..., description="Nombre de la fuente de origen ('remaju', 'sunarp', etc.).")
    metadatos: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Diccionario flexible para cualquier atributo particular de la fuente (ej. convocatoria, registrador, etc.)."
    )
    pdf_bytes: bytes = Field(..., description="El documento PDF en formato de bytes crudos.")
    nombre_archivo_sugerido: str = Field(..., description="Nombre sugerido para guardar o referenciar el PDF.")
    # CORREGIDO: Evitar datetime.utcnow() ya que está deprecado en Python moderno; se prefiere UTC explícito
    fecha_extraccion: datetime = Field(
        default_factory=lambda: datetime.now(datetime.timezone.utc), 
        description="Timestamp UTC de la extracción."
    )
