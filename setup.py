from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

about = {}
exec(open(path.join(here, 'steg/__init__.py')).read(), about)

with open(path.join(here, 'README.md')) as file:
    long_description = file.read()

setup(
    name='steg',
    version=about['__version__'],
    description='Steg is a simple python library for hiding and extracting messages from losslessly compressed images using least-significant-bit (LSB) steganography.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_dir={"steg": "steg"},
    entry_points={"console_scripts": ["steg=steg._steg:run"]},
    author='Andrew Scott',
    url='https://github.com/beatsbears/steg',
    packages=find_packages(),
    license='MIT License',
    install_requires=[
        "Pillow==8.1.2"
    ],
)