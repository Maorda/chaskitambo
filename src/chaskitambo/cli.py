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
@app.command("run-all")
def run_all_installed_plugins():
    """Ejecuta TODOS los plugins detectados en paralelo con salida secuencial."""
    async def _run():
        # Tomamos todos los nombres indexados dinámicamente por Entry Points
        todos_los_plugins = engine.list_available_plugins()
        
        async def mock_chaskywasi_handler(doc):
            # Simulamos un proceso secuencial lento (ej. guardar en Base de Datos)
            await asyncio.sleep(1) 
            logger.info(f" -> [CHASKIWASI] Procesado en orden: {doc.id_externo}")

        await engine.run_plugins_parallel(todos_los_plugins, chaskywasi_handler=mock_chaskywasi_handler)

    asyncio.run(_run())

if __name__ == "__main__":
    app()