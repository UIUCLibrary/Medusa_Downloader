from cx_Freeze import setup, Executable
from shared_setup import metadata

metadata['options'] = {
    "build_exe": {
        "includes": ["queue", "atexit"],
        "packages": ["os"],
        "excludes": ["tkinter"]
    }
}
metadata['executables'] = [Executable("medusadownloader/msync.py")]

setup(**metadata)
