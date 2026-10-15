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
    name: str = typer.Argument(
        ...,
        help="Nombre del plugin de raspado (ej. remaju, sunarp)",
    ),
    local: bool = typer.Option(
        False,
        "--local",
        help="Activa el modo de pruebas locales del plugin, si lo admite.",
    ),
):
    """Ejecuta un plugin de raspado de forma autónoma."""

    async def _run():
        async def mock_chaskywasi_handler(doc):
            logger.info(
                f" -> [CHASKIWASI] Recibido documento con ID: "
                f"{doc.id_externo} desde fuente '{doc.fuente}'"
            )

        plugin_kwargs = {}

        if local:
            plugin_kwargs[name] = {"modo_local": True}

        await engine.run_plugins_parallel(
            [name],
            chaskywasi_handler=mock_chaskywasi_handler,
            plugin_kwargs=plugin_kwargs,
        )

    if sys.platform == "win32":
        asyncio.set_event_loop_policy(
            asyncio.WindowsProactorEventLoopPolicy()
        )

    try:
        asyncio.run(_run())
    except KeyboardInterrupt:
        logger.warning(
            " -> [CLI] Ejecución interrumpida manualmente por el usuario."
        )

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
