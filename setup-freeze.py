# from setuptools import setup
import sys
from cx_Freeze import setup, Executable
from shared_setup import metadata

base = None
if sys.platform == 'win32':
    base = 'Win32GUI'


metadata['options'] = {
    "build_exe": {
        "includes": ["queue", "atexit"],
        "packages": ["os"],
        "excludes": ["tkinter"]
    }
}
metadata['executables'] = [Executable("medusadownloader/msync.py")]

setup(**metadata)
