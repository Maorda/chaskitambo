class ChaskitamboError(Exception):
    """Excepción base para todos los errores del motor Chaskitambo."""
    pass

class PluginExecutionError(ChaskitamboError):
    """Lanzada cuando ocurre un fallo durante la ejecución de un plugin de raspado."""
    pass