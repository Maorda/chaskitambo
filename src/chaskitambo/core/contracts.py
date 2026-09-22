from pydantic import BaseModel, Field
from typing import Dict, Any
from datetime import datetime

class ChaskiDocument(BaseModel):
    """
    Contrato de datos universal y estricto que todo plugin de Chaskitambo
    debe retornar, independiente de la fuente de origen (REMAJU, SUNARP, etc.).
    """
    id_externo: str = Field(..., description="Identificador único del documento (ej. expediente, partida).")
    fuente: str = Field(..., description="Nombre de la fuente de origen ('remaju', 'sunarp', etc.).")
    metadatos: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Diccionario flexible para cualquier atributo particular de la fuente (ej. convocatoria, registrador, etc.)."
    )
    pdf_bytes: bytes = Field(..., description="El documento PDF en formato de bytes crudos.")
    nombre_archivo_sugerido: str = Field(..., description="Nombre sugerido para guardar o referenciar el PDF.")
    fecha_extraccion: datetime = Field(default_factory=datetime.utcnow, description="Timestamp UTC de la extracción.")

    class Config:
        arbitrary_types_allowed = True