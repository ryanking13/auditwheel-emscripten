from pathlib import Path

import typer
from rich.pretty import pprint

from .. import show

app = typer.Typer()


@app.callback(no_args_is_help=True)
def main():
    """Auditwheel-like tool for emscripten wheels and shared libraries."""


@app.command("show")
def _show(
    wheel_or_so_file: Path = typer.Argument(
        ..., help="Path to wheel or a shared library file."
    )
):
    """
    Show shared library dependencies of a wheel of a shared library file.
    """
    result = show.execute(wheel_or_so_file)
    print("The following external shared libraries are required:")
    pprint(result)
