# D:\libs\chaskitambo\src\chaskitambo\cli.py
import sys
import asyncio
import typer
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
    """Ejecuta un plugin de raspado de forma autónoma utilizando la infraestructura paralela."""
    async def _run():
        async def mock_chaskywasi_handler(doc):
            logger.info(f" -> [CHASKIWASI] Recibido documento con ID: {doc.id_externo} desde fuente '{doc.fuente}'")
            
        # CORREGIDO: Llamamos a 'run_plugins_parallel' envolviendo el nombre en una lista [name]
        await engine.run_plugins_parallel([name], chaskywasi_handler=mock_chaskywasi_handler)

    # Forzar la política Proactor requerida por Playwright en sistemas Windows
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    try:
        asyncio.run(_run())
    except KeyboardInterrupt:
        logger.warning(" -> [CLI] Ejecución interrumpida manualmente por el usuario.")

@app.command("run-all")
def run_all_installed_plugins():
    """Ejecuta TODOS los plugins detectados en paralelo con salida secuencial."""
    async def _run():
        todos_los_plugins = engine.list_available_plugins()
        
        async def mock_chaskywasi_handler(doc):
            await asyncio.sleep(1) 
            logger.info(f" -> [CHASKIWASI] Procesado en orden: {doc.id_externo}")

        await engine.run_plugins_parallel(todos_los_plugins, chaskywasi_handler=mock_chaskywasi_handler)

    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    try:
        asyncio.run(_run())
    except KeyboardInterrupt:
        logger.warning(" -> [CLI] Ejecución masiva interrumpida por el usuario.")

if __name__ == "__main__":
    app()
