import re
from functools import cache
from pathlib import Path

from packaging.utils import parse_wheel_filename


def libdir_candidates(libdir: str | Path) -> list[Path]:
    libdir = Path(libdir)
    return [
        libdir,
        libdir / "lib",
        # search relocatable first.
        libdir / "lib" / "wasm32-emscripten" / "pic",
        libdir / "lib" / "wasm32-emscripten",
    ]


def is_emscripten_wheel(filename: str) -> bool:
    _, _, _, tags = parse_wheel_filename(filename)
    tag = list(tags)[0]
    platform = tag.platform
    return platform.startswith("emscripten")


@cache
def sharedlib_regex() -> re.Pattern:
    return re.compile(r"(\.dylib|\.so(.\d+)*)$")
