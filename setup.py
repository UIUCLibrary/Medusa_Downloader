from setuptools import setup

setup(
    name='medusaDownloader',
    version='0.0.1',
    packages=['medusadownloader'],
    url='https://github.com/UIUCLibrary/',
    license='',
    zip_safe=False,
    author='Henry Borchers',
    author_email='hborcher@illinois.edu',
    entry_points={"console_scripts": ["msync=medusadownloader.msync:main"]},
    description='',
    tests_require=["pytest"],
    test_suite="tests",
    install_requires=['requests']
)
