from setuptools import setup
from shared_setup import metadata

setup(**metadata, entry_points={"console_scripts": ["msync=medusadownloader.msync:main"]},
      tests_require=["pytest"],
      zip_safe=False,
      setup_requires=["pytest-runner"],
      install_requires=['requests']
      )
