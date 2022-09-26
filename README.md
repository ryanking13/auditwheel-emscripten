# auditwheel-emscripten

auditwheel-like tool for Pyodide

## Usage

```sh
$ pip install auditwheel-emscripten
```

```sh
 Usage: pyodide audit [OPTIONS] COMMAND [ARGS]...

 Auditwheel-like tool for emscripten wheels and shared libraries.

╭─ Options ───────────────────────╮
│ --help          Show this message and exit.   │
╰──────────────────────────────╯
╭─ Commands ────────────────────────────────────────────────────────────────────────────╮
│ copy      Copy shared libraries to the wheel directory. Similar to repair but does not modify the needed section of WASM module.
│ repair    [Experimental] Repair a wheel file: copy shared libraries to the wheel directory and modify the path in the wheel file.
│ show      Show shared library dependencies of a wheel of a shared library file.
╰───────────────────────────────────────────────────────────────────────────────────╯

```

```sh
# wget https://cdn.jsdelivr.net/pyodide/v0.21.3/full/Shapely-1.8.2-cp310-cp310-emscripten_3_1_14_wasm32.whl
$ pyodide audit show Shapely-1.8.2-cp310-cp310-emscripten_3_1_14_wasm32.whl

The following external shared libraries are required:
{
│   'shapely/speedups/_speedups.cpython-310-wasm32-emscripten.so': ['libgeos_c.so'],
│   'shapely/vectorized/_vectorized.cpython-310-wasm32-emscripten.so': ['libgeos_c.so']
}
```

```sh
$ pyodide audit copy --libdir <directory which contains libgeos_c.so> Shapely-1.8.2-cp310-cp310-emscripten_3_1_14_wasm32.whl

Repaired wheel has following external shared libraries:
{
│   'Shapely.libs/libgeos.so.3.10.3': [],
│   'Shapely.libs/libgeos_c.so': ['libgeos.so.3.10.3'],
│   'shapely/speedups/_speedups.cpython-310-wasm32-emscripten.so': ['libgeos_c.so'],
│   'shapely/vectorized/_vectorized.cpython-310-wasm32-emscripten.so': ['libgeos_c.so']
}
```
