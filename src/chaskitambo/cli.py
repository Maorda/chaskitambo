import typer
import asyncio
from loguru import logger
from .core.engine import ChaskitamboEngine

app = typer.Typer(help="Motor centralizador de plugins de raspado - Chaskitambo")
engine = ChaskitamboEngine()

@app.command("list")
def list_plugins():
    """Lista todos los plugins de raspado instalados y detectados en el entorno."""
    plugins = engine.list_available_plugins()
    if not plugins:
        typer.echo("-> No se encontraron plugins de raspado registrados.")
    else:
        typer.echo("-> Plugins de Chaskitambo disponibles:")
        for p in plugins:
            typer.echo(f"   - {p}")

@app.command("run")
def run_plugin(
    name: str = typer.Argument(..., help="Nombre del plugin a ejecutar (ej. remaju, sunarp)")
):
    """Ejecuta un plugin de raspado de forma autónoma."""
    async def _run():
        # Aquí puedes inyectar el manejador real hacia chaskywasi si lo deseas
        async def mock_chaskywasi_handler(doc):
            logger.info(f" -> [CHASKIWASI] Recibido documento con ID: {doc.id_externo} desde fuente '{doc.fuente}'")
            
        await engine.run_plugin(name, chaskywasi_handler=mock_chaskywasi_handler)

    asyncio.run(_run())

if __name__ == "__main__":
    app()