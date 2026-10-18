
import sys
import asyncio

import typer
from loguru import logger

from .core.engine import ChaskitamboEngine


app = typer.Typer(
    help="Motor centralizador de plugins de raspado - Chaskitambo"
)

engine = ChaskitamboEngine()


@app.command("list")
def list_plugins():
    """Lista todos los plugins de raspado instalados y detectados."""
    plugins = engine.list_available_plugins()

    if not plugins:
        typer.echo("-> No se encontraron plugins de raspado registrados.")
        return

    typer.echo("-> Plugins de Chaskitambo disponibles:")

    for plugin in plugins:
        typer.echo(f"   - {plugin}")


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
    oficina: str | None = typer.Option(
        None,
        "--oficina",
        help="Oficina registral para los plugins que lo requieran.",
    ),
    partida: str | None = typer.Option(
        None,
        "--partida",
        help="Número de partida registral para la búsqueda SUNARP.",
    ),
):
    """Ejecuta un plugin de raspado de forma autónoma."""

    async def _run():
        async def mock_chaskywasi_handler(doc):
            logger.info(
                " -> [CHASKIWASI] Recibido documento con ID: "
                f"{doc.id_externo} desde fuente '{doc.fuente}'"
            )

        plugin_kwargs = {}
        parametros = {}

        if local:
            parametros["modo_local"] = True

        if oficina is not None:
            oficina_limpia = oficina.strip()

            if not oficina_limpia:
                raise typer.BadParameter(
                    "La oficina registral no puede estar vacía."
                )

            parametros["oficina"] = oficina_limpia

        if partida is not None:
            partida_limpia = partida.strip()

            if not partida_limpia:
                raise typer.BadParameter(
                    "El número de partida no puede estar vacío."
                )

            parametros["partida_objetivo"] = partida_limpia

        if parametros:
            plugin_kwargs[name] = parametros

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
    """Ejecuta todos los plugins detectados en paralelo."""

    async def _run():
        todos_los_plugins = engine.list_available_plugins()

        async def mock_chaskywasi_handler(doc):
            await asyncio.sleep(1)

            logger.info(
                " -> [CHASKIWASI] Procesado en orden: "
                f"{doc.id_externo}"
            )

        await engine.run_plugins_parallel(
            todos_los_plugins,
            chaskywasi_handler=mock_chaskywasi_handler,
        )

    if sys.platform == "win32":
        asyncio.set_event_loop_policy(
            asyncio.WindowsProactorEventLoopPolicy()
        )

    try:
        asyncio.run(_run())
    except KeyboardInterrupt:
        logger.warning(
            " -> [CLI] Ejecución masiva interrumpida manualmente por el usuario."
        )


if __name__ == "__main__":
    app()
