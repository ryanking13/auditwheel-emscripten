from pathlib import Path

import rich
import typer
from rich.pretty import pprint

from .. import repair, show

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
    try:
        dependencies = show(wheel_or_so_file)
        rich.print("The following external shared libraries are required:")
        pprint(dependencies)
    except Exception as e:
        raise e


@app.command("repair")
def _repair(
    wheel_file: Path = typer.Argument(..., help="Path to wheel file."),
    libdir: Path = typer.Option(
        "lib",
        help="Path to the directory containing the shared libraries.",
    ),
    output_dir: Path = typer.Option(
        None,
        help="Directory to output repaired wheel or shared library. (default: overwrite the input file)",
    ),
):
    """
    Repair a wheel file: copy shared libraries to the wheel directory and modify the path in the wheel file.
    """
    try:
        repaired_wheel = repair(wheel_file, libdir, output_dir)
        dependencies = show(repaired_wheel)
        rich.print("Repaired wheel has following external shared libraries:")
        pprint(dependencies)
    except RuntimeError as e:
        raise e
