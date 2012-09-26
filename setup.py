from distutils.core import setup
from setuptools import find_packages


setup(
    name='pandas-sqlalchemy-pivot',
    version='0.1',
    packages=find_packages(
        exclude=["*.tests", "*.tests.*", "tests.*", "tests"]
    ),
    py_modules=[],
    url='',
    license='MIT',
    author='Tomas Drencak',
    author_email='tomas@drencak.com',
    description='',
    install_requires=['pandas', 'numpy', 'sqlalchemy'],
)
