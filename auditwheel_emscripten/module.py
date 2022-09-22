from pathlib import Path

import leb128

from .emscripten_tools import webassembly
from .emscripten_tools.webassembly import HEADER_SIZE, DylinkType
from .utils import libdir_candidates


class ModuleWritable(webassembly.Module):
    def encode_dylink_section(
        self, section: webassembly.Section, dylink: webassembly.Dylink
    ) -> bytes:
        """
        Encode given dylib section to bytes
        """
        buf = bytearray()

        # custom section
        buf += b"\x00"

        # section size
        buf.extend(leb128.u.encode(section.size))

        # section name
        buf.extend(leb128.u.encode(len(section.name.encode())))
        buf += section.name.encode()

        # section body
        # 1. MEM_INFO
        subsection_buf = bytearray()
        subsection_buf.extend(leb128.u.encode(dylink.mem_size))
        subsection_buf.extend(leb128.u.encode(dylink.mem_align))
        subsection_buf.extend(leb128.u.encode(dylink.table_size))
        subsection_buf.extend(leb128.u.encode(dylink.table_align))

        buf.extend(leb128.u.encode(DylinkType.MEM_INFO))
        buf.extend(leb128.u.encode(len(subsection_buf)))
        buf.extend(subsection_buf)

        # 2. NEEDED
        subsection_buf = bytearray()
        subsection_buf.extend(leb128.u.encode(len(dylink.needed)))
        for lib in dylink.needed:
            subsection_buf.extend(leb128.u.encode(len(lib.encode())))
            subsection_buf += lib.encode()

        buf.extend(leb128.u.encode(DylinkType.NEEDED))
        buf.extend(leb128.u.encode(len(subsection_buf)))
        buf.extend(subsection_buf)

        # 3. EXPORT_INFO
        subsection_buf = bytearray()
        subsection_buf.extend(leb128.u.encode(len(dylink.export_info)))
        for sym, flags in dylink.export_info:
            subsection_buf.extend(leb128.u.encode(len(sym.encode())))
            subsection_buf += sym.encode()
            subsection_buf.extend(leb128.u.encode(flags))

        buf.extend(leb128.u.encode(DylinkType.EXPORT_INFO))
        buf.extend(leb128.u.encode(len(subsection_buf)))
        buf.extend(subsection_buf)

        # 4. IMPORT_INFO
        subsection_buf = bytearray()
        subsection_buf.extend(leb128.u.encode(len(dylink.import_info)))
        for module, fields in dylink.import_info:
            for field, flags in fields:
                subsection_buf.extend(leb128.u.encode(len(module.encode())))
                subsection_buf += module.encode()
                subsection_buf.extend(leb128.u.encode(len(field.encode())))
                subsection_buf += field.encode()
                subsection_buf.extend(leb128.u.encode(flags))

        buf.extend(leb128.u.encode(DylinkType.IMPORT_INFO))
        buf.extend(leb128.u.encode(len(subsection_buf)))
        buf.extend(subsection_buf)

        return bytes(buf)

    def patch_dylink(self, data: bytes) -> bytes:
        orignal_module = open(self.filename, "rb").read()
        section = next(self.sections())
        if section.name not in ("dylink", "dylink.0"):
            raise RuntimeError(f"dylink section not found in {self.filename}")

        patched_module = (
            orignal_module[:HEADER_SIZE]
            + data
            + orignal_module[section.offset + section.size :]
        )
        return patched_module

    def write(self, data: bytes, filename: str) -> None:
        with open(filename, "wb") as f:
            f.write(data)

    def patch_and_write(self, offset: int, data: bytes, filename: str) -> None:
        raise NotImplementedError()
        patched_module = self.patch(offset, data)
        self.write(patched_module, filename)

    def find_needed_dylibs(self, libdir: str | Path) -> dict[str, str]:
        libdirs = libdir_candidates(libdir)

        section = self.parse_dylink_section()
        needed_libs = section.needed
        matched_libs = {}
        for lib in needed_libs:
            for libdir in libdirs:
                libpath = libdir / lib
                if libpath.exists():
                    break
            else:
                raise RuntimeError(f"cannot find library {lib}")

            matched_libs[str(lib)] = str(libpath)

        return matched_libs

    def patch_needed_dylibs(self, libdir: str | Path) -> None:
        libs = self.find_needed_dylibs(libdir)
        section = self.parse_dylink_section()
        section.needed = list(libs.values())
        self.patch_and_write(section.offset, section.encode(), self.filename)


def parse_dylink_section(dylib: Path):
    """
    Get dylink section from given dylib
    """
    with ModuleWritable(dylib) as m:
        dylink = m.parse_dylink_section()

    return dylink
